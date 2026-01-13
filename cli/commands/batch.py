"""Batch execution plugin implementing batch file processing."""

import os


def cmd_batch(cli, arg):
    if not arg:
        print("✗ Usage: batch <filename>")
        return

    filename = arg.strip()
    if not os.path.exists(filename):
        print(f"✗ File not found: {filename}")
        return

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            commands = f.readlines()

        print(f"✓ Executing batch file: {filename} ({len(commands)} commands)")
        print("=" * 60)

        for i, cmd_line in enumerate(commands, 1):
            cmd_line = cmd_line.strip()
            if not cmd_line or cmd_line.startswith('#'):
                continue
            print(f"\n[{i}] {cmd_line}")
            cli.onecmd(cmd_line)

        print("\n" + "=" * 60)
        print("✓ Batch processing completed")
    except Exception as e:
        print(f"✗ Batch execution failed: {e}")


commands = {
    'batch': cmd_batch,
}

