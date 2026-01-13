"""Data/contour loading plugin with full load logic."""

import os
import pandas as pd
import numpy as np


def _load_data(cli, src):
    if not all([cli.settings['height'], cli.settings['surface'], 
               cli.settings['degree'], cli.settings['viscosity'], 
               cli.settings['number']]):
        print("✗ Required settings missing. Please set:")
        print("  set height <value>")
        print("  set surface <value>")
        print("  set degree <value>")
        print("  set viscosity <value>")
        print("  set number <value>")
        return

    filename = f"{cli.settings['height']}CM_{cli.settings['surface']}_{cli.settings['degree']}_{cli.settings['viscosity']}_{cli.settings['number']}"
    filepath = os.path.join(src, filename, "_DATA.csv")

    try:
        if cli.verbose:
            print(f"Loading: {filepath}")
        cli.current_data = pd.read_csv(filepath)
        print(f"✓ Data loaded successfully: {len(cli.current_data)} rows")
        print(f"  Columns: {', '.join(cli.current_data.columns.tolist())}")
        if cli.verbose:
            print("\nData preview:")
            print(cli.current_data.head())
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
    except Exception as e:
        print(f"✗ Load failed: {e}")


def _load_contour(cli, src):
    if not all([cli.settings['height'], cli.settings['surface'], 
               cli.settings['degree'], cli.settings['viscosity'], 
               cli.settings['number']]):
        print("✗ Required settings missing (use 'set' command)")
        return

    dirname = f"{cli.settings['height']}CM_{cli.settings['surface']}_{cli.settings['degree']}_{cli.settings['viscosity']}_{cli.settings['number']}"
    contour_path = os.path.join(src, dirname, "Contour Files")
    if not os.path.exists(contour_path):
        print(f"✗ Contour directory not found: {contour_path}")
        return

    try:
        file_lst = os.listdir(contour_path)
        contours = []
        print(f"Loading... Total {len(file_lst)} frames")
        for i in range(len(file_lst)):
            src_path = os.path.join(contour_path, f'Imagenumber_{i}')
            if not os.path.exists(src_path):
                continue
            file_list2 = os.listdir(src_path)
            temp = []
            for filename in file_list2:
                filepath = os.path.join(src_path, filename)
                try:
                    t = np.load(filepath)
                    temp.append(t)
                except:
                    if cli.verbose:
                        print(f"  Warning: {filepath} load failed")
            contours.append(temp if temp else 0)
        cli.current_contours = contours
        print(f"✓ Contours loaded successfully: {len(contours)} frames")
    except Exception as e:
        print(f"✗ Load failed: {e}")


def cmd_load(cli, arg):
    args = arg.split()
    if len(args) < 1:
        print("✗ Usage: load <data|contour> [path]")
        return

    load_type = args[0].lower()
    src = args[1] if len(args) > 1 else cli.current_src
    if not src:
        src = cli.settings.get('src') or './data'
    cli.current_src = src

    if load_type == 'data':
        return _load_data(cli, src)
    elif load_type == 'contour':
        return _load_contour(cli, src)
    else:
        print(f"✗ Unknown type: {load_type}")
        print("  Available: data, contour")


commands = {
    'load': cmd_load,
}
