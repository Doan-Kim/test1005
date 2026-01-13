from interactive_cli import ContactAngleCLI
from .dispatcher import register_plugins


def main():
    cli = ContactAngleCLI()
    register_plugins(cli)
    cli.cmdloop()


if __name__ == '__main__':
    main()
