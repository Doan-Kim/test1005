"""Settings commands implemented as plugins (full logic).

These functions were moved from the original `ContactAngleCLI` class
and adapted to operate on the `cli` instance passed in.
"""

import os
import json


def cmd_set(cli, arg):
    args = arg.split()
    if len(args) < 2:
        print("✗ Usage: set <key> <value> [<key2> <value2> ...]")
        print("Current settings:")
        return cli._show_settings()

    i = 0
    success_count = 0
    error_count = 0

    while i < len(args):
        key = args[i].lower()
        if key in cli.setting_aliases:
            key = cli.setting_aliases[key]

        if i + 1 >= len(args):
            print(f"✗ Missing value for key: {key}")
            error_count += 1
            break

        value_parts = []
        j = i + 1
        while j < len(args):
            next_token = args[j].lower()
            if next_token in cli.settings or next_token in cli.setting_aliases or next_token == 'verbose':
                break
            value_parts.append(args[j])
            j += 1

        if not value_parts:
            print(f"✗ Missing value for key: {key}")
            error_count += 1
            i += 1
            continue

        value = ' '.join(value_parts)

        if key == 'verbose':
            cli.verbose = value.lower() in ['on', 'true', '1', 'yes']
            print(f"✓ verbose mode: {'ON' if cli.verbose else 'OFF'}")
            success_count += 1
        elif key in cli.settings:
            try:
                if key in ['surface']:
                    cli.settings[key] = str(value)
                elif key in ['degree', 'viscosity', 'number','height']:
                    cli.settings[key] = int(value)
                else:
                    cli.settings[key] = value
                print(f"✓ {key} = {cli.settings[key]}")
                success_count += 1
            except ValueError:
                print(f"✗ Invalid value for {key}: {value}")
                error_count += 1
        else:
            print(f"✗ Unknown setting: {key}")
            print("  Available keys: height(h), surface(s,sur), degree(d,deg), viscosity(v,vis), number(n,num)")
            error_count += 1

        i = j

    if success_count + error_count > 1:
        print(f"\n📊 Summary: {success_count} succeeded, {error_count} failed")


def cmd_show(cli, arg):
    arg = arg.strip().lower()

    if not arg or arg == 'all' or arg == 'settings':
        print("\n=== Current Settings ===")
        cli._show_settings()

    if not arg or arg == 'all' or arg == 'data':
        print("\n=== Data Status ===")
        if cli.current_data is not None:
            print(f"  ✓ Data loaded: {len(cli.current_data)} rows")
            print(f"  Columns: {', '.join(cli.current_data.columns.tolist())}")
        else:
            print("  ✗ No data")

    if not arg or arg == 'all' or arg == 'contours':
        print("\n=== Contour Status ===")
        if cli.current_contours:
            print(f"  ✓ Contours loaded: {len(cli.current_contours)} frames")
        else:
            print("  ✗ No contours")
    print()


def cmd_loadconfig(cli, arg):
    filename = arg.strip() if arg.strip() else cli.config_file
    if not os.path.exists(filename):
        print(f"✗ Config file not found: {filename}")
        return

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            config = json.load(f)

        loaded_count = 0
        for key in cli.settings.keys():
            if key in config:
                cli.settings[key] = config[key]
                loaded_count += 1

        if 'workdir' in config:
            cli.workdir = config['workdir']
            loaded_count += 1
            if cli.workdir and os.path.exists(cli.workdir):
                try:
                    os.chdir(cli.workdir)
                    if cli.verbose:
                        print(f"  → Changed to workdir: {cli.workdir}")
                except Exception as e:
                    print(f"  Warning: Could not change to workdir: {e}")

        if 'verbose' in config:
            cli.verbose = config['verbose']
            loaded_count += 1
        if 'settings' in config:
            for key in cli.settings.keys():
                if key in config['settings']:
                    cli.settings[key] = config['settings'][key]
                    loaded_count += 1

        print(f"✓ Config loaded from {filename}")
        print(f"  Loaded {loaded_count} settings")
        if cli.verbose:
            print("\nLoaded settings:")
            cli._show_settings()

    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON format: {e}")
    except Exception as e:
        print(f"✗ Failed to load config: {e}")


def cmd_saveconfig(cli, arg):
    filename = arg.strip() if arg.strip() else cli.config_file
    try:
        config = {}
        for key, value in cli.settings.items():
            if value is not None:
                config[key] = value

        if cli.current_src:
            config['src'] = cli.current_src

        current_dir = os.getcwd()
        config['workdir'] = current_dir
        cli.workdir = current_dir
        config['verbose'] = cli.verbose

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"✓ Config saved to {filename}")
        print(f"  Saved {len(config)} settings")
        if cli.verbose:
            print("\nSaved settings:")
            for key, value in config.items():
                print(f"  {key:15s} = {value}")

    except Exception as e:
        print(f"✗ Failed to save config: {e}")


def cmd_setworkdir(cli, arg):
    path = arg.strip()
    if not path:
        print("✗ Usage: setworkdir <path>")
        return
    if os.path.exists(path) and os.path.isdir(path):
        os.chdir(path)
        print(f"✓ Current working directory: {os.getcwd()}")
    else:
        print(f"✗ Path not found or not a directory: {path}")


commands = {
    'set': cmd_set,
    'show': cmd_show,
    'loadconfig': cmd_loadconfig,
    'saveconfig': cmd_saveconfig,
    'setworkdir': cmd_setworkdir,
}
