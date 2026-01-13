"""Example command module for cli.commands.

Provides a simple `greet` command as a usage example.
"""

def greet(cli, arg):
    name = arg.strip() or "User"
    print(f"Hello, {name}!")


commands = {
    'greet': greet,
}
