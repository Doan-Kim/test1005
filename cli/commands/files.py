"""Filesystem and navigation commands plugin (full implementations)."""

import os


def cmd_ls(cli, arg):
    args = arg.strip().split()
    path = '.'
    show_all = False
    for a in args:
        if a in ['-a', '-all']:
            show_all = True
        else:
            path = a

    if not os.path.exists(path):
        print(f"✗ Path not found: {path}")
        return

    try:
        items = os.listdir(path)
        print(f"\nDirectory: {os.path.abspath(path)}")
        print("=" * 70)
        dirs = sorted([i for i in items if os.path.isdir(os.path.join(path, i))])
        files = sorted([i for i in items if os.path.isfile(os.path.join(path, i))])
        cli.last_dirs = dirs

        if dirs:
            print("\n[Directories]")
            display_dirs = dirs if show_all else dirs[:20]
            for idx, d in enumerate(display_dirs, 1):
                print(f"  [{idx:2d}] 📁 {d}/")
            if not show_all and len(dirs) > 20:
                print(f"  ... and {len(dirs) - 20} more directories (show all: ls -a)")

        if files:
            print("\n[Files]")
            display_files = files if show_all else files[:20]
            for f in display_files:
                size = os.path.getsize(os.path.join(path, f))
                size_str = cli._format_size(size)
                print(f"  📄 {f:<45s} {size_str:>10s}")
            if not show_all and len(files) > 20:
                print(f"  ... and {len(files) - 20} more files (show all: ls -a)")

        print(f"\nTotal: {len(dirs)} directories, {len(files)} files")
        if not show_all and (len(dirs) > 20 or len(files) > 20):
            print("💡 Use 'ls -a' or 'ls -all' to show complete list.")
        print()
    except PermissionError:
        print(f"✗ Permission denied: {path}")


def cmd_cd(cli, arg):
    arg = arg.strip()
    if not arg or arg == '.':
        print(f"Current directory: {os.getcwd()}")
        return

    if arg == '~':
        path = os.path.expanduser('~')
    elif arg.isdigit():
        idx = int(arg) - 1
        if not cli.last_dirs:
            print("✗ Please use 'ls' command first to see directory list.")
            return
        if idx < 0 or idx >= len(cli.last_dirs):
            print(f"✗ Invalid number. (Enter a number between 1-{len(cli.last_dirs)})")
            return
        path = cli.last_dirs[idx]
        print(f"→ Moving to {path}/")
    else:
        path = arg

    try:
        os.chdir(path)
        print(f"✓ Current directory: {os.getcwd()}")
        if cli.verbose:
            print()
            cli.do_ls('')
    except FileNotFoundError:
        print(f"✗ Path not found: {path}")
    except NotADirectoryError:
        print(f"✗ Not a directory: {path}")
    except PermissionError:
        print(f"✗ Permission denied: {path}")


def cmd_pwd(cli, arg):
    print(os.getcwd())


commands = {
    'ls': cmd_ls,
    'cd': cmd_cd,
    'pwd': cmd_pwd,
}
