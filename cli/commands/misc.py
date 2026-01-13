"""Misc commands plugin (clear, history, exit)."""

import os
import sys


def cmd_clear(cli, arg):
    os.system('cls' if os.name == 'nt' else 'clear')


def cmd_history(cli, arg):
    if hasattr(cli, 'cmdqueue'):
        print("\n=== Command History ===")
        for i, cmd in enumerate(cli.cmdqueue, 1):
            print(f"{i:3d}. {cmd}")


def cmd_exit(cli, arg):
    print("\nGoodbye!")
    return True


commands = {
    'clear': cmd_clear,
    'history': cmd_history,
    'exit': cmd_exit,
    'quit': cmd_exit,
}

