import importlib
import pkgutil
import types


def register_plugins(cli_instance):
    """Discover modules in cli.commands and bind their commands to the CLI instance.

    Each command module should expose a dict named `commands` mapping
    command_name -> callable(cli_instance, arg).
    """
    package = 'cli.commands'
    try:
        pkg = importlib.import_module(package)
    except Exception:
        return

    if not hasattr(pkg, '__path__'):
        return

    for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__):
        mod_name = f"{package}.{name}"
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue

        cmds = getattr(mod, 'commands', None)
        if not isinstance(cmds, dict):
            continue

        for cmd_name, func in cmds.items():
            method_name = f"do_{cmd_name}"
            # Always override existing do_<cmd> methods so plugins fully replace behavior
            # Wrap the plugin function to make it a bound method on the CLI instance

            def make_wrapper(f):
                def wrapper(self, arg):
                    return f(self, arg)
                return wrapper

            setattr(cli_instance, method_name, types.MethodType(make_wrapper(func), cli_instance))
