"""Export plugin implementing data export functionality."""

def cmd_export(cli, arg):
    if not arg:
        print("✗ Usage: export <filename>")
        return

    filename = arg.strip()
    if cli.current_data is None:
        print("✗ No data to export.")
        return

    try:
        if filename.endswith('.csv'):
            cli.current_data.to_csv(filename, index=False)
        elif filename.endswith('.json'):
            cli.current_data.to_json(filename, orient='records', indent=2)
        elif filename.endswith('.xlsx'):
            cli.current_data.to_excel(filename, index=False)
        else:
            print("✗ Unsupported file format (only .csv, .json, .xlsx supported)")
            return

        print(f"✓ Data exported successfully: {filename}")
    except Exception as e:
        print(f"✗ Export failed: {e}")


commands = {
    'export': cmd_export,
}

