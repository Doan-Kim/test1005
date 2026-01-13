"""Folder and data-folder related commands plugin (full logic).

Moved from `interactive_cli.py` and adapted to operate on `cli` instance.
"""

import os
import json
from pathlib import Path


def cmd_folder(cli, arg):
    args = arg.strip().split()
    if len(args) > 0:
        src = args[0]
        if os.path.exists(src):
            cli.current_src = src
            print(f"✓ Source path set to: {src}")
        else:
            print(f"✗ Path not found: {src}")
            return

    if not all([cli.settings['height'], cli.settings['surface'], 
               cli.settings['degree'], cli.settings['viscosity'], 
               cli.settings['number']]):
        print("✗ Please set all required settings first:")
        print("  set height <value>")
        print("  set surface <value>")
        print("  set degree <value>")
        print("  set viscosity <value>")
        print("  set number <value>")
        return

    folder_name = f"{cli.settings['height']}CM_{cli.settings['surface']}_{cli.settings['degree']}_{cli.settings['viscosity']}_{cli.settings['number']}"
    src = cli.current_src or './data'
    cli.current_data_folder = os.path.join(src, folder_name)

    print(f"\n=== Current Data Folder ===")
    print(f"  Source: {cli.current_src or './data'}")
    print(f"  Folder: {cli.current_data_folder}")

    if os.path.exists(cli.current_data_folder):
        print(f"  Status: ✓ Exists")
        try:
            items = os.listdir(cli.current_data_folder)
            dirs = [i for i in items if os.path.isdir(os.path.join(cli.current_data_folder, i))]
            files = [i for i in items if os.path.isfile(os.path.join(cli.current_data_folder, i))]
            print(f"  Contents: {len(dirs)} directories, {len(files)} files")
            if files:
                print(f"  Files: {', '.join(files[:5])}")
                if len(files) > 5:
                    print(f"         ... and {len(files) - 5} more")
            if dirs:
                print(f"  Directories: {', '.join(dirs[:5])}")
                if len(dirs) > 5:
                    print(f"               ... and {len(dirs) - 5} more")
        except Exception as e:
            print(f"  Error reading folder: {e}")
    else:
        print(f"  Status: ✗ Does not exist")
    print()


def cmd_setfolder(cli, arg):
    return cmd_folder(cli, arg)


def cmd_makefolder(cli, arg):
    missing_settings = []
    for key in ['height', 'surface', 'degree', 'viscosity', 'number']:
        if cli.settings[key] is None:
            missing_settings.append(key)

    if missing_settings:
        print("✗ Required settings missing:")
        for key in missing_settings:
            aliases = [k for k, v in cli.setting_aliases.items() if v == key]
            alias_hint = f" (or: {', '.join(aliases)})" if aliases else ""
            print(f"  ✗ {key:15s} - use: set {key} <value>{alias_hint}")
        return

    args = arg.strip().split()
    base_path = args[0] if len(args) > 0 else (cli.workdir if cli.workdir else os.getcwd())

    if not os.path.exists(base_path):
        print(f"✗ Base path does not exist: {base_path}")
        print(f"  Please create the base path first or specify a valid path.")
        return

    folder_name = f"{cli.settings['height']}CM_{cli.settings['surface']}_{cli.settings['degree']}_{cli.settings['viscosity']}_{cli.settings['number']}"
    folder_path = os.path.join(base_path, folder_name)

    if os.path.exists(folder_path):
        print(f"✓ Folder already exists: {folder_path}")
        try:
            items = os.listdir(folder_path)
            dirs = [i for i in items if os.path.isdir(os.path.join(folder_path, i))]
            files = [i for i in items if os.path.isfile(os.path.join(folder_path, i))]
            print(f"  Contents: {len(dirs)} directories, {len(files)} files")
        except Exception as e:
            print(f"  Error reading folder: {e}")
        return

    try:
        os.makedirs(folder_path, exist_ok=True)
        print(f"✓ Folder created successfully!")
        print(f"  Path: {folder_path}")
        cli.current_data_folder = folder_path
        scalenumber = 0
        try:
            scalenumber = os.getcwd().split('-SN')[1].split('_')[0]
        except Exception:
            scalenumber = 114155

        rawimage_path = os.path.abspath(os.getcwd())
        image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif'}
        image_files = []
        image_types = set()
        try:
            for file in os.listdir(rawimage_path):
                file_path = os.path.join(rawimage_path, file)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in image_extensions:
                        image_files.append(file)
                        if ext in ['.jpg', '.jpeg']:
                            image_types.add('jpeg')
                        elif ext == '.png':
                            image_types.add('png')
                        elif ext in ['.tiff', '.tif']:
                            image_types.add('tiff')
        except Exception as e:
            print(f"  Warning: Could not analyze images: {e}")

        imagetype = ','.join(sorted(image_types)) if image_types else 'none'
        imagenumber = len(image_files)
        imagename = image_files[0] if image_files else ''

        folder_info_path = os.path.join(folder_path, "folder_info.json")
        folder_info = {
            "rawimage_path": rawimage_path,
            "scalenumber": scalenumber,
            "imagetype": imagetype,
            "imagenumber": imagenumber,
            "imagename": imagename,
            "settings": {
                "height": cli.settings['height'],
                "surface": cli.settings['surface'],
                "degree": cli.settings['degree'],
                "viscosity": cli.settings['viscosity'],
                "number": cli.settings['number']
            }
        }

        try:
            with open(folder_info_path, 'w', encoding='utf-8') as f:
                json.dump(folder_info, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Folder info saved: folder_info.json")
            if imagenumber > 0:
                print(f"  ✓ Found {imagenumber} image(s) - Type(s): {imagetype}")
        except Exception as e:
            print(f"  Warning: Could not save folder info: {e}")

        if cli.verbose:
            print(f"\n  You can now use this folder for your data.")
            print(f"  Suggested subdirectories:")
            print(f"    - Contour Files")
            print(f"    - Images")
            print(f"    - Results")

    except Exception as e:
        print(f"✗ Failed to create folder: {e}")


def _readfolder_json(cli, folder):
    try:
        csv_path = os.path.join(folder, "_DATA.csv")
        if not os.path.exists(csv_path):
            if cli.verbose:
                print(f"  ⚠ _DATA.csv not found in {folder}")
            return

        import pandas as pd
        data = pd.read_csv(csv_path)
        if len(data) == 0:
            if cli.verbose:
                print(f"  ⚠ _DATA.csv is empty in {folder}")
            return

        folder_name = os.path.basename(folder)
        parts = folder_name.split('_')
        if len(parts) >= 5:
            try:
                height = parts[0].replace('CM', '')
                surface = parts[1]
                degree = parts[2]
                viscosity = parts[3]
                number = parts[4]

                if cli.workdir:
                    config_path = os.path.join(cli.workdir, "config.json")
                else:
                    config_path = cli.config_file

                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                else:
                    config = {"workdir": cli.workdir, "verbose": False, "settings": {}}

                config['settings'] = {
                    'height': int(height) if height.isdigit() else height,
                    'surface': surface,
                    'degree': int(degree) if degree.isdigit() else degree,
                    'viscosity': int(viscosity) if viscosity.isdigit() else viscosity,
                    'number': int(number) if number.isdigit() else number
                }

                if 'value' in data.columns:
                    config['data_value'] = data['value'].iloc[0]

                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)

                if cli.verbose:
                    print(f"  ✓ Updated config: {folder_name}")

            except (ValueError, IndexError):
                if cli.verbose:
                    print(f"  ⚠ Failed to parse folder name: {folder_name}")
        else:
            if cli.verbose:
                print(f"  ⚠ Invalid folder name format: {folder_name}")

    except Exception as e:
        if cli.verbose:
            print(f"  ✗ Error processing {folder}: {e}")


def cmd_readfolder(cli, arg):
    args = arg.strip()
    if not args:
        print("✗ Usage: readfolder <folder_path>")
        print("Example: readfolder D:/data")
        return

    folder_path = Path(args)
    if not folder_path.exists():
        print(f"✗ 폴더를 찾을 수 없습니다: {folder_path}")
        return
    if not folder_path.is_dir():
        print(f"✗ 폴더가 아닙니다: {folder_path}")
        return

    subfolders = []
    try:
        for item in folder_path.iterdir():
            if item.is_dir():
                subfolders.append(str(item))

        if subfolders:
            n = 0
            for folder in subfolders:
                print(f"[{n}]: {folder}")
                n += 1
                _readfolder_json(cli, folder)
            cli.last_dirs = subfolders
        else:
            print(f"✓ '{folder_path}'에 하위 폴더가 없습니다.")
            cli.last_dirs = []
    except PermissionError as e:
        print(f"✗ 접근 권한 오류: {e}")
    except Exception as e:
        print(f"✗ 오류 발생: {e}")


commands = {
    'folder': cmd_folder,
    'setfolder': cmd_setfolder,
    'makefolder': cmd_makefolder,
    'readfolder': cmd_readfolder,
}
