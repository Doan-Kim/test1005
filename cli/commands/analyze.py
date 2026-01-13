"""Analysis plugin with basic summary and method dispatch."""

def _analyze_summary(cli):
    if cli.current_data is None:
        print("✗ No data loaded. Please use 'load data' command first.")
        return

    print("\n=== Data Summary ===")
    try:
        print(cli.current_data.describe())
    except Exception as e:
        print(f"✗ Summary failed: {e}")


def cmd_analyze(cli, arg):
    args = arg.split()
    if len(args) < 1:
        print("✗ Usage: analyze <method>")
        print("  Methods: diameter, contact-angle, rim-height, summary")
        return

    method = args[0].lower()
    if method == 'summary':
        return _analyze_summary(cli)
    elif method in ('diameter', 'contact-angle', 'rim-height'):
        print(f"✓ Running {method} analysis...")
        print("  (Implement analysis logic here)")
    else:
        print(f"✗ Unknown method: {method}")


commands = {
    'analyze': cmd_analyze,
}
