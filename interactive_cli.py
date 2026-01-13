#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""경량화된 Interactive CLI

이 모듈은 CLI의 상태와 공통 헬퍼만 유지합니다. 모든 명령은
`cli/commands` 플러그인에서 제공되며, 엔트리포인트는 `cli/app.py`입니다.
"""

import cmd
import os
import sys
import json


class ContactAngleCLI(cmd.Cmd):
    """Contact Angle CLI: 상태와 유틸리티만 보관."""

    intro = """
╔════════════════════════════════════════════════════════════╗
║     Contact Angle Analysis - Interactive CLI               ║
╚════════════════════════════════════════════════════════════╝

Command Help: help or ?
End program: exit or quit
Command List: help

    """

    prompt = '(ContactAngle) > '

    def __init__(self):
        super().__init__()
        # 상태
        self.current_data = None
        self.current_contours = []
        self.current_src = None
        self.current_data_folder = None

        self.settings = {
            'height': None,
            'surface': None,
            'degree': None,
            'viscosity': None,
            'number': None,
        }

        self.setting_aliases = {
            'h': 'height', 's': 'surface', 'sur': 'surface',
            'd': 'degree', 'deg': 'degree',
            'v': 'viscosity', 'vis': 'viscosity',
            'n': 'number', 'num': 'number',
        }

        self.verbose = False
        self.last_dirs = []

        # 기본 설정 파일 및 작업 디렉터리
        self.config_file = os.path.join(os.getcwd(), 'config.json')
        self.workdir = os.getcwd()

        # 시작 시 존재하면 조용히 로드
        self._load_config_silent()

    # ---------- 설정 출력 및 헬퍼 ----------
    def _show_settings(self):
        """현재 설정을 보기 좋게 출력한다."""
        for key, value in self.settings.items():
            status = "✓" if value is not None else "✗"
            print(f"  {status} {key:15s} = {value}")
        print(f"  {'✓' if self.verbose else '✗'} verbose        = {self.verbose}")
        if self.current_src:
            print(f"  ✓ src           = {self.current_src}")
        if self.workdir:
            print(f"  ✓ workdir       = {self.workdir}")
        if self.current_data_folder:
            print(f"  ✓ data_folder   = {self.current_data_folder}")

    def _load_config_silent(self):
        """시작 시 설정 파일을 조용히 로드한다 (오류 무시)."""
        try:
            if not os.path.exists(self.config_file):
                return
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            for key in self.settings.keys():
                if key in config:
                    self.settings[key] = config[key]
            if 'src' in config:
                self.current_src = config['src']
            if 'workdir' in config:
                self.workdir = config['workdir']
                if self.workdir and os.path.exists(self.workdir):
                    try:
                        os.chdir(self.workdir)
                    except Exception:
                        pass
            if 'verbose' in config:
                self.verbose = config['verbose']
        except Exception:
            pass

    def _format_size(self, size):
        """파일 크기를 사람이 읽기 쉬운 형식으로 변환한다."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    # 기본 동작
    def emptyline(self):
        pass

    def default(self, line):
        print(f"✗ Unknown command: {line}")
        print("  Type 'help' or '?' to see available commands.")

    def do_EOF(self, arg):
        print()
        return True


def main():
    try:
        ContactAngleCLI().cmdloop()
    except KeyboardInterrupt:
        print("\n\nExiting.")
        sys.exit(0)


if __name__ == '__main__':
    main()
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Interactive CLI - 경량화된 Contact Angle CLI 클래스

이 파일은 CLI의 상태와 공통 헬퍼만 유지하며, 실제 명령 구현은
`cli/commands` 플러그인으로 분리되어 있습니다.
"""

import cmd
import os
import sys
import json
from pathlib import Path


class ContactAngleCLI(cmd.Cmd):
    """Interactive Contact Angle Analysis CLI (state + helpers only)"""

    intro = """
╔════════════════════════════════════════════════════════════╗
║     Contact Angle Analysis - Interactive CLI               ║
╚════════════════════════════════════════════════════════════╝

Command Help: help or ?
End program: exit or quit
Command List: help

    """
    prompt = '(ContactAngle) > '

    def __init__(self):
        super().__init__()
        # State
        self.current_data = None
        self.current_contours = []
        self.current_src = None
        self.current_data_folder = None
        self.settings = {
            'height': None,
            'surface': None,
            'degree': None,
            'viscosity': None,
            'number': None,
        }
        self.setting_aliases = {
            'h': 'height', 's': 'surface', 'sur': 'surface',
            'd': 'degree', 'deg': 'degree',
            'v': 'viscosity', 'vis': 'viscosity',
            'n': 'number', 'num': 'number',
        }
        self.verbose = False
        self.last_dirs = []
        # Keep a sane default config path (can be overridden by plugins)
        self.config_file = os.path.join(os.getcwd(), 'config.json')
        self.workdir = os.getcwd()

        # Load config silently if present
        self._load_config_silent()
    
    # ==================== 설정 관련 명령 ====================
    
    def do_set(self, arg):
        """
        Change setting value
        Usage: set <key> <value> [<key2> <value2> ...]
        Example: set threshold 150
                 set height 5.0  (or: set h 5.0)
                 set h 5 s Glass d 45 v 1000 n 001  # Multiple settings at once
                 set surface Glass degree 45
                 set verbose on
        
        Shortcuts:
          h, height     → height
          s, sur        → surface
          d, deg        → degree
          v, vis        → viscosity
          n, num        → number
        """
        args = arg.split()
        if len(args) < 2:
            print("✗ Usage: set <key> <value> [<key2> <value2> ...]")
            print("Current settings:")
            self._show_settings()
            return
        
        # Check if multiple key-value pairs are provided
        # Parse arguments as key-value pairs
        i = 0
        success_count = 0
        error_count = 0
        
        while i < len(args):
            key = args[i].lower()
            
            # Convert alias to actual key
            if key in self.setting_aliases:
                actual_key = self.setting_aliases[key]
                if self.verbose:
                    print(f"  ({key} → {actual_key})")
                key = actual_key
            
            # Check if there's a value following the key
            if i + 1 >= len(args):
                print(f"✗ Missing value for key: {key}")
                error_count += 1
                break
            
            # Get value - it might be multi-word for surface, so check if next item is a key
            value_parts = []
            j = i + 1
            
            # Collect value tokens until we hit another key or end of args
            while j < len(args):
                next_token = args[j].lower()
                # Check if next token is a known key or alias
                if next_token in self.settings or next_token in self.setting_aliases or next_token == 'verbose':
                    break
                value_parts.append(args[j])
                j += 1
            
            if not value_parts:
                print(f"✗ Missing value for key: {key}")
                error_count += 1
                i += 1
                continue
            
            value = ' '.join(value_parts)
            
            # Set the value
            if key == 'verbose':
                self.verbose = value.lower() in ['on', 'true', '1', 'yes']
                print(f"✓ verbose mode: {'ON' if self.verbose else 'OFF'}")
                success_count += 1
            elif key in self.settings:
                # Type conversion
                try:
                    if key in ['surface']:
                        self.settings[key] = str(value)
                    elif key in ['degree', 'viscosity', 'number','height']:
                        self.settings[key] = int(value)
                    else:
                        self.settings[key] = value
                    print(f"✓ {key} = {self.settings[key]}")
                    success_count += 1
                except ValueError:
                    print(f"✗ Invalid value for {key}: {value}")
                    error_count += 1
            else:
                print(f"✗ Unknown setting: {key}")
                print("  Available keys: height(h), surface(s,sur), degree(d,deg), viscosity(v,vis), number(n,num)")
                error_count += 1
            
            # Move to next key-value pair
            i = j
        
        # Summary if multiple settings were changed
        if success_count + error_count > 1:
            print(f"\n📊 Summary: {success_count} succeeded, {error_count} failed")
    
    def do_show(self, arg):
        """
        Show current settings and status
        Usage: show [settings|data|contours|all]
        """
        arg = arg.strip().lower()
        
        if not arg or arg == 'all' or arg == 'settings':
            print("\n=== Current Settings ===")
            self._show_settings()
        
        if not arg or arg == 'all' or arg == 'data':
            print("\n=== Data Status ===")
            if self.current_data is not None:
                print(f"  ✓ Data loaded: {len(self.current_data)} rows")
                print(f"  Columns: {', '.join(self.current_data.columns.tolist())}")
            else:
                print("  ✗ No data")
        
        if not arg or arg == 'all' or arg == 'contours':
            print("\n=== Contour Status ===")
            if self.current_contours:
                print(f"  ✓ Contours loaded: {len(self.current_contours)} frames")
            else:
                print("  ✗ No contours")
        print()
    
    def _show_settings(self):
        """설정 출력"""
        for key, value in self.settings.items():
            status = "✓" if value is not None else "✗"
            print(f"  {status} {key:15s} = {value}")
        print(f"  {'✓' if self.verbose else '✗'} verbose        = {self.verbose}")
        if self.current_src:
            print(f"  ✓ src           = {self.current_src}")
        if self.workdir:
            print(f"  ✓ workdir        = {self.workdir}")
        if self.current_data_folder:
            print(f"  ✓ data_folder    = {self.current_data_folder}")
    
    # ==================== Config 파일 관련 ====================
    
    def do_loadconfig(self, arg):
        """
        Load settings from config.json file
        Usage: loadconfig [filename]
        Example: loadconfig
                 loadconfig my_config.json
        """
        filename = arg.strip() if arg.strip() else self.config_file
        
        if not os.path.exists(filename):
            print(f"✗ Config file not found: {filename}")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Load settings
            loaded_count = 0
            for key in self.settings.keys():
                if key in config:
                    self.settings[key] = config[key]
                    loaded_count += 1
            
            # Load other settings
            
            if 'workdir' in config:
                self.workdir = config['workdir']
                loaded_count += 1
                # Change to workdir if it exists
                if self.workdir and os.path.exists(self.workdir):
                    try:
                        os.chdir(self.workdir)
                        if self.verbose:
                            print(f"  → Changed to workdir: {self.workdir}")
                    except Exception as e:
                        print(f"  Warning: Could not change to workdir: {e}")
            
            if 'verbose' in config:
                self.verbose = config['verbose']
                loaded_count += 1
            if 'settings' in config:
                for key in self.settings.keys():
                    if key in config['settings']:
                        self.settings[key] = config['settings'][key]
                        loaded_count += 1
            print(f"✓ Config loaded from {filename}")
            print(f"  Loaded {loaded_count} settings")
            
            if self.verbose:
                print("\nLoaded settings:")
                self._show_settings()
                
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON format: {e}")
        except Exception as e:
            print(f"✗ Failed to load config: {e}")
    
    def _load_config_silent(self):
        """Silently load config on startup (no error messages)"""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for key in self.settings.keys():
                if key in config:
                    self.settings[key] = config[key]
            
            if 'src' in config:
                self.current_src = config['src']
            
            if 'workdir' in config:
                self.workdir = config['workdir']
                if self.workdir and os.path.exists(self.workdir):
                    try:
                        os.chdir(self.workdir)
                    except:
                        pass
            
            if 'verbose' in config:
                self.verbose = config['verbose']
        except:
            pass  # Silently ignore errors on startup
    
    def do_saveconfig(self, arg):
        """
        Save current settings to config.json file
        Usage: saveconfig [filename]
        Example: saveconfig
                 saveconfig my_config.json
        """
        filename = arg.strip() if arg.strip() else self.config_file
        
        try:
            # Prepare config data
            config = {}
            
            # Save current settings
            for key, value in self.settings.items():
                if value is not None:
                    config[key] = value
            
            # Save other settings
            if self.current_src:
                config['src'] = self.current_src
            
            # Save current working directory as workdir
            current_dir = os.getcwd()
            config['workdir'] = current_dir
            self.workdir = current_dir
            
            config['verbose'] = self.verbose
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Config saved to {filename}")
            print(f"  Saved {len(config)} settings")
            
            if self.verbose:
                print("\nSaved settings:")
                for key, value in config.items():
                    print(f"  {key:15s} = {value}")
                
        except Exception as e:
            print(f"✗ Failed to save config: {e}")
    
    def do_setworkdir(self, arg):
        """
        Set current working directory
        Usage: setworkdir <path>
        Example: setworkdir ./data
        """
        path = arg.strip()
        if not path:
            print("✗ Usage: setworkdir <path>")
            return
        if os.path.exists(path) and os.path.isdir(path):
            os.chdir(path)
            print(f"✓ Current working directory: {os.getcwd()}")
        else:
            print(f"✗ Path not found or not a directory: {path}")
    
    # ==================== 폴더 관련 명령 ====================
    
    def do_folder(self, arg):
        """
        Set or display data folder path based on current settings
        Usage: folder [src_path]
        Example: folder           # Display current folder
                 folder ./data    # Set source path and update folder
        """
        args = arg.strip().split()
        
        if len(args) > 0:
            # Set source path
            src = args[0]
            if os.path.exists(src):
                self.current_src = src
                print(f"✓ Source path set to: {src}")
            else:
                print(f"✗ Path not found: {src}")
                return
        
        # Display current folder
        if not all([self.settings['height'], self.settings['surface'], 
                   self.settings['degree'], self.settings['viscosity'], 
                   self.settings['number']]):
            print("✗ Please set all required settings first:")
            print("  set height <value>")
            print("  set surface <value>")
            print("  set degree <value>")
            print("  set viscosity <value>")
            print("  set number <value>")
            return
        
        folder_name = f"{self.settings['height']}CM_{self.settings['surface']}_{self.settings['degree']}_{self.settings['viscosity']}_{self.settings['number']}"
        src = self.current_src or './data'
        self.current_data_folder = os.path.join(src, folder_name)
        
        print(f"\n=== Current Data Folder ===")
        print(f"  Source: {self.current_src or './data'}")
        print(f"  Folder: {self.current_data_folder}")
        
        # Check if folder exists
        if os.path.exists(self.current_data_folder):
            print(f"  Status: ✓ Exists")
            # Show folder contents
            try:
                items = os.listdir(self.current_data_folder)
                dirs = [i for i in items if os.path.isdir(os.path.join(self.current_data_folder, i))]
                files = [i for i in items if os.path.isfile(os.path.join(self.current_data_folder, i))]
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
    
    def do_setfolder(self, arg):
        """
        Alias for 'folder' command
        """
        return self.do_folder(arg)
    
    def do_makefolder(self, arg):
        """
        Create data folder based on current settings
        Usage: makefolder [path]
        Example: makefolder           # Create in current working directory
                 makefolder ./data    # Create in specified path
        """
        # Check if all required settings are set
        missing_settings = []
        for key in ['height', 'surface', 'degree', 'viscosity', 'number']:
            if self.settings[key] is None:
                missing_settings.append(key)
        
        if missing_settings:
            print("✗ Required settings missing:")
            for key in missing_settings:
                # Show alias hints for each missing setting
                aliases = [k for k, v in self.setting_aliases.items() if v == key]
                if aliases:
                    alias_hint = f" (or: {', '.join(aliases)})"
                else:
                    alias_hint = ""
                print(f"  ✗ {key:15s} - use: set {key} <value>{alias_hint}")
            return
        
        # Determine base path
        args = arg.strip().split()
        if len(args) > 0:
            base_path = args[0]
        else:
            base_path = self.workdir if self.workdir else os.getcwd()
        
        # Check if base path exists
        if not os.path.exists(base_path):
            print(f"✗ Base path does not exist: {base_path}")
            print(f"  Please create the base path first or specify a valid path.")
            return
        
        # Generate folder name
        folder_name = f"{self.settings['height']}CM_{self.settings['surface']}_{self.settings['degree']}_{self.settings['viscosity']}_{self.settings['number']}"
        folder_path = os.path.join(base_path, folder_name)
        
        # Check if folder already exists
        if os.path.exists(folder_path):
            print(f"✓ Folder already exists: {folder_path}")
            
            # Show folder contents
            try:
                items = os.listdir(folder_path)
                dirs = [i for i in items if os.path.isdir(os.path.join(folder_path, i))]
                files = [i for i in items if os.path.isfile(os.path.join(folder_path, i))]
                print(f"  Contents: {len(dirs)} directories, {len(files)} files")
            except Exception as e:
                print(f"  Error reading folder: {e}")
            return
        
        # Create the folder
        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f"✓ Folder created successfully!")
            print(f"  Path: {folder_path}")
            
            # Update current_data_folder
            self.current_data_folder = folder_path
            scalenumber = 0
            try:
                scalenumber = os.getcwd().split('-SN')[1].split('_')[0]
            except Exception as e:
                scalenumber = 114155
            
            # Analyze images in rawimage_path
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
                            # Normalize extension names
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
            
            # Save folder path to JSON file
            folder_info_path = os.path.join(folder_path, "folder_info.json")
            folder_info = {
                "rawimage_path": rawimage_path,
                "scalenumber": scalenumber,
                "imagetype": imagetype,
                "imagenumber": imagenumber,
                "imagename": imagename,
                "settings": {
                    "height": self.settings['height'],
                    "surface": self.settings['surface'],
                    "degree": self.settings['degree'],
                    "viscosity": self.settings['viscosity'],
                    "number": self.settings['number']
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
            
            # Optionally create subdirectories
            if self.verbose:
                print(f"\n  You can now use this folder for your data.")
                print(f"  Suggested subdirectories:")
                print(f"    - Contour Files")
                print(f"    - Images")
                print(f"    - Results")
                
        except Exception as e:
            print(f"✗ Failed to create folder: {e}")
    
    def do_readfolder(self, arg):
        """
        List direct subfolders in a given directory
        Usage: readfolder <folder_path>
        Example: readfolder D:/data
                 readfolder .
                 readfolder ./subfolder
        """
        args = arg.strip()
        
        if not args:
            print("✗ Usage: readfolder <folder_path>")
            print("Example: readfolder D:/data")
            return
        
        folder_path = Path(args)
        
        # 경로가 존재하는지 확인
        if not folder_path.exists():
            print(f"✗ 폴더를 찾을 수 없습니다: {folder_path}")
            return
        
        if not folder_path.is_dir():
            print(f"✗ 폴더가 아닙니다: {folder_path}")
            return
        
        # 직속 하위 폴더만 수집
        subfolders = []
        
        try:
            # 현재 폴더의 직속 항목만 확인
            for item in folder_path.iterdir():
                if item.is_dir():
                    subfolders.append(str(item))
            
            # 결과 출력
            if subfolders:
                n = 0
                for folder in subfolders:
                    print(f"[{n}]: {folder}")
                    n += 1
                    self._readfolder_json(folder)                      
                # 폴더 리스트를 배열로 저장
                self.last_dirs = subfolders
            else:
                print(f"✓ '{folder_path}'에 하위 폴더가 없습니다.")
                self.last_dirs = []
            
        except PermissionError as e:
            print(f"✗ 접근 권한 오류: {e}")
        except Exception as e:
            print(f"✗ 오류 발생: {e}")
    
    def _readfolder_json(self, folder):
        """
        Read _DATA.csv from a folder and update config.json with extracted values
        
        Args:
            folder: Path to folder containing _DATA.csv
        """
        try:
            # _DATA.csv 파일 경로
            csv_path = os.path.join(folder, "_DATA.csv")
            
            # 파일이 존재하는지 확인
            if not os.path.exists(csv_path):
                if self.verbose:
                    print(f"  ⚠ _DATA.csv not found in {folder}")
                return
            
            # CSV 파일 읽기
            data = pd.read_csv(csv_path)
            
            if len(data) == 0:
                if self.verbose:
                    print(f"  ⚠ _DATA.csv is empty in {folder}")
                return
            
            # 폴더 이름에서 설정값 추출
            # 예: "20CM_AL_0_5_1" -> height=20, surface=AL, degree=0, viscosity=5, number=1
            folder_name = os.path.basename(folder)
            parts = folder_name.split('_')
            
            if len(parts) >= 5:
                try:
                    # 폴더 이름 파싱
                    height = parts[0].replace('CM', '')
                    surface = parts[1]
                    degree = parts[2]
                    viscosity = parts[3]
                    number = parts[4]
                    
                    # workdir의 config.json 경로
                    if self.workdir:
                        config_path = os.path.join(self.workdir, "config.json")
                    else:
                        config_path = self.config_file
                    
                    # 기존 config 읽기
                    if os.path.exists(config_path):
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                    else:
                        config = {"workdir": self.workdir, "verbose": False, "settings": {}}
                    
                    # 설정값 업데이트
                    config['settings'] = {
                        'height': int(height) if height.isdigit() else height,
                        'surface': surface,
                        'degree': int(degree) if degree.isdigit() else degree,
                        'viscosity': int(viscosity) if viscosity.isdigit() else viscosity,
                        'number': int(number) if number.isdigit() else number
                    }
                    
                    # CSV에서 특정 값 추출 (필요시 여기에 추가)
                    # 예: 첫 번째 행의 특정 컬럼 값
                    if 'value' in data.columns:
                        config['data_value'] = data['value'].iloc[0]
                    
                    # config.json에 저장
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                    
                    if self.verbose:
                        print(f"  ✓ Updated config: {folder_name}")
                        
                except (ValueError, IndexError) as e:
                    if self.verbose:
                        print(f"  ⚠ Failed to parse folder name: {folder_name}")
            else:
                if self.verbose:
                    print(f"  ⚠ Invalid folder name format: {folder_name}")
                    
        except Exception as e:
            if self.verbose:
                print(f"  ✗ Error processing {folder}: {e}")

    def do_load(self, arg):
        """
        Load data file
        Usage: load <data|contour> [path]
        Example: load data
                 load data ./data
                 load contour
        """
        args = arg.split()
        if len(args) < 1:
            print("✗ Usage: load <data|contour> [path]")
            return
        
        load_type = args[0].lower()
        src = args[1] if len(args) > 1 else self.current_src
        
        if not src:
            src = self.settings.get('src') or './data'
        
        self.current_src = src
        
        if load_type == 'data':
            self._load_data(src)
        elif load_type == 'contour':
            self._load_contour(src)
        else:
            print(f"✗ Unknown type: {load_type}")
            print("  Available: data, contour")
    
    def _load_data(self, src):
        """Load CSV data"""
        if not all([self.settings['height'], self.settings['surface'], 
                   self.settings['degree'], self.settings['viscosity'], 
                   self.settings['number']]):
            print("✗ Required settings missing. Please set:")
            print("  set height <value>")
            print("  set surface <value>")
            print("  set degree <value>")
            print("  set viscosity <value>")
            print("  set number <value>")
            return
        
        filename = f"{self.settings['height']}CM_{self.settings['surface']}_{self.settings['degree']}_{self.settings['viscosity']}_{self.settings['number']}"
        filepath = os.path.join(src, filename, "_DATA.csv")
        
        try:
            if self.verbose:
                print(f"Loading: {filepath}")
            
            self.current_data = pd.read_csv(filepath)
            print(f"✓ Data loaded successfully: {len(self.current_data)} rows")
            print(f"  Columns: {', '.join(self.current_data.columns.tolist())}")
            
            if self.verbose:
                print("\nData preview:")
                print(self.current_data.head())
                
        except FileNotFoundError:
            print(f"✗ File not found: {filepath}")
        except Exception as e:
            print(f"✗ Load failed: {e}")
    
    def _load_contour(self, src):
        """Load contour data"""
        if not all([self.settings['height'], self.settings['surface'], 
                   self.settings['degree'], self.settings['viscosity'], 
                   self.settings['number']]):
            print("✗ Required settings missing (use 'set' command)")
            return
        
        dirname = f"{self.settings['height']}CM_{self.settings['surface']}_{self.settings['degree']}_{self.settings['viscosity']}_{self.settings['number']}"
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
                        if self.verbose:
                            print(f"  Warning: {filepath} load failed")
                
                contours.append(temp if temp else 0)
            
            self.current_contours = contours
            print(f"✓ Contours loaded successfully: {len(contours)} frames")
            
        except Exception as e:
            print(f"✗ Load failed: {e}")
    
    # ==================== 분석 명령 ====================
    
    def do_analyze(self, arg):
        """
        Perform data analysis
        Usage: analyze <method> [options]
        Methods: diameter, contact-angle, rim-height, summary
        Example: analyze diameter
                 analyze contact-angle
                 analyze summary
        """
        args = arg.split()
        if len(args) < 1:
            print("✗ Usage: analyze <method>")
            print("  Methods: diameter, contact-angle, rim-height, summary")
            return
        
        method = args[0].lower()
        
        if method == 'summary':
            self._analyze_summary()
        elif method == 'diameter':
            print(f"✓ Running {method} analysis...")
            # Call actual analysis function
            print("  (Implement analysis logic here)")
        elif method == 'contact-angle':
            print(f"✓ Running {method} analysis...")
            print("  (Implement analysis logic here)")
        elif method == 'rim-height':
            print(f"✓ Running {method} analysis...")
            print("  (Implement analysis logic here)")
        else:
            print(f"✗ Unknown method: {method}")
    
    def _analyze_summary(self):
        """Data summary statistics"""
        if self.current_data is None:
            print("✗ No data loaded. Please use 'load data' command first.")
            return
        
        print("\n=== Data Summary ===")
        print(self.current_data.describe())
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
    # ==================== 파일/디렉토리 명령 ====================
    
    def do_ls(self, arg):
        """
        List files and directories
        Usage: ls [path] [-a|-all]
        Options: -a, -all  Show all files (default: first 20 only)
        Example: ls
                 ls ./data
                 ls -a          # Show all files
                 ls ./data -all # Show all
        """
        args = arg.strip().split()
        path = '.'
        show_all = False
        
        # Parse arguments
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
            
            # Save directory list (for cd command)
            self.last_dirs = dirs
            
            # Display directories
            if dirs:
                print("\n[Directories]")
                display_dirs = dirs if show_all else dirs[:20]
                
                for idx, d in enumerate(display_dirs, 1):
                    print(f"  [{idx:2d}] 📁 {d}/")
                
                if not show_all and len(dirs) > 20:
                    print(f"  ... and {len(dirs) - 20} more directories (show all: ls -a)")
            
            # Display files
            if files:
                print("\n[Files]")
                display_files = files if show_all else files[:20]
                
                for f in display_files:
                    size = os.path.getsize(os.path.join(path, f))
                    size_str = self._format_size(size)
                    print(f"  📄 {f:<45s} {size_str:>10s}")
                
                if not show_all and len(files) > 20:
                    print(f"  ... and {len(files) - 20} more files (show all: ls -a)")
            
            print(f"\nTotal: {len(dirs)} directories, {len(files)} files")
            if not show_all and (len(dirs) > 20 or len(files) > 20):
                print("💡 Use 'ls -a' or 'ls -all' to show complete list.")
            print()
            
        except PermissionError:
            print(f"✗ Permission denied: {path}")
    
    def do_cd(self, arg):
        """
        Change working directory
        Usage: cd <path|number>
        Example: cd ./data     # Move to path
                 cd ..         # Parent directory
                 cd 1          # Move to directory #1 from ls command
                 cd ~          # Home directory
        """
        arg = arg.strip()
        
        if not arg or arg == '.':
            # Display current directory
            print(f"Current directory: {os.getcwd()}")
            return
        
        # Move to home directory
        if arg == '~':
            path = os.path.expanduser('~')
        # If number, select from directory list shown by ls
        elif arg.isdigit():
            idx = int(arg) - 1
            if not self.last_dirs:
                print("✗ Please use 'ls' command first to see directory list.")
                return
            if idx < 0 or idx >= len(self.last_dirs):
                print(f"✗ Invalid number. (Enter a number between 1-{len(self.last_dirs)})")
                return
            path = self.last_dirs[idx]
            print(f"→ Moving to {path}/")
        else:
            path = arg
        
        try:
            os.chdir(path)
            print(f"✓ Current directory: {os.getcwd()}")
            # Auto-display list after changing directory
            if self.verbose:
                print()
                self.do_ls('')
        except FileNotFoundError:
            print(f"✗ Path not found: {path}")
        except NotADirectoryError:
            print(f"✗ Not a directory: {path}")
        except PermissionError:
            print(f"✗ Permission denied: {path}")
    
    def do_pwd(self, arg):
        """Display current working directory"""
        print(os.getcwd())
    
    def _format_size(self, size):
        """Convert file size to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    # ==================== 내보내기 명령 ====================
    
    def do_export(self, arg):
        """
        Export data to file
        Usage: export <filename>
        Example: export results.csv
                 export output.json
        """
        if not arg:
            print("✗ Usage: export <filename>")
            return
        
        filename = arg.strip()
        
        if self.current_data is None:
            print("✗ No data to export.")
            return
        
        try:
            if filename.endswith('.csv'):
                self.current_data.to_csv(filename, index=False)
            elif filename.endswith('.json'):
                self.current_data.to_json(filename, orient='records', indent=2)
            elif filename.endswith('.xlsx'):
                self.current_data.to_excel(filename, index=False)
            else:
                print("✗ Unsupported file format (only .csv, .json, .xlsx supported)")
                return
            
            print(f"✓ Data exported successfully: {filename}")
        except Exception as e:
            print(f"✗ Export failed: {e}")
    
    # ==================== 시각화 명령 ====================
    def do_view(self, arg):
        args = arg.strip().split()
        mode = None
        for a in args:
            if a in ['-i', '-image']:
                mode = 'image'
            elif a in ['-c', '-contour']:
                mode = 'contour'
            elif a in ['-b', '-binary']:
                mode = 'binary'    
        if mode == 'image':
            self._view_image()
    
    def _view_image(self):
        img_num = 0
        def trackbar(x):
            nonlocal img_num
            img_num = cv2.getTrackbarPos("frame", "Image Viewer")
        """View raw images based on loaded config"""
        # Check if all required settings are set
        missing_settings = []
        for key in ['height', 'surface', 'degree', 'viscosity', 'number']:
            if self.settings[key] is None:
                missing_settings.append(key)
        
        if missing_settings:
            print("✗ Required settings missing:")
            for key in missing_settings:
                # Show alias hints for each missing setting
                aliases = [k for k, v in self.setting_aliases.items() if v == key]
                if aliases:
                    alias_hint = f" (or: {', '.join(aliases)})"
                else:
                    alias_hint = ""
                print(f"  ✗ {key:15s} - use: set {key} <value>{alias_hint}")
            return
        src = self.workdir + '/' + f"{self.settings['height']}CM_{self.settings['surface']}_{self.settings['degree']}_{self.settings['viscosity']}_{self.settings['number']}"
        src = src + '/folder_info.json'

        if not os.path.exists(src):
            print(f"✗ Config file not found: {src}")
            return
        
        try:
            with open(src, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if 'rawimage_path' in config:
                self.rawimage_path = config['rawimage_path']
            if 'scalenumber' in config:
                self.scalenumber = config['scalenumber']
            if 'imagetype' in config:
                self.imagetype = config['imagetype']
            if 'imagenumber' in config:
                self.imagenumber = config['imagenumber']
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON format: {e}")
        except Exception as e:
            print(f"✗ Failed to load config: {e}")
    
        # Get list of image files from rawimage_path
        image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif'}
        image_files = []
        
        try:
            for file in sorted(os.listdir(self.rawimage_path)):
                file_path = os.path.join(self.rawimage_path, file)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in image_extensions:
                        image_files.append(file_path)
        except Exception as e:
            print(f"✗ Failed to read images from {self.rawimage_path}: {e}")
            return
        
        if not image_files:
            print(f"✗ No images found in {self.rawimage_path}")
            return
        
        # Print current settings
        print("\n" + "="*60)
        print("Current Settings:")
        print(f"  Height       : {self.settings['height']} CM")
        print(f"  Surface      : {self.settings['surface']}")
        print(f"  Degree       : {self.settings['degree']}")
        print(f"  Viscosity    : {self.settings['viscosity']}")
        print(f"  Number       : {self.settings['number']}")
        print("="*60)
        
        esc_key = 'q'
        print(f"\nPress '{esc_key}' to exit image viewer\n")
        
        cv2.destroyAllWindows()
        window_width = 1200
        window_height = 800
        cv2.namedWindow("Image Viewer", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Image Viewer", window_width, window_height)
        cv2.createTrackbar("frame", "Image Viewer", 0, len(image_files) - 1, trackbar)
        
        while cv2.waitKey(1) != ord(esc_key):
            imagesrc = image_files[img_num] if img_num < len(image_files) else image_files[0]
            _img = cv2.imread(imagesrc)
            if _img is not None:
                # Get original image dimensions
                h, w = _img.shape[:2]
                
                # Calculate scaling factor to fit window while maintaining aspect ratio
                scale = min(window_width / w, window_height / h)
                new_w = int(w * scale)
                new_h = int(h * scale)
                
                # Resize image maintaining aspect ratio
                resized_img = cv2.resize(_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                
                # Create canvas with window size and black background
                canvas = np.zeros((window_height, window_width, 3), dtype=np.uint8)
                
                # Calculate position to center the image
                x_offset = (window_width - new_w) // 2
                y_offset = (window_height - new_h) // 2
                
                # Place resized image on canvas
                canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_img
                
                cv2.imshow("Image Viewer", canvas)
            else:
                print(f"✗ Failed to load image: {imagesrc}")
                break
        cv2.destroyAllWindows()

    # ==================== 배치 처리 명령 ====================
    
    def do_batch(self, arg):
        """
        Execute batch file
        Usage: batch <filename>
        Example: batch commands.txt
        
        Batch file format (one command per line):
          set height 5.0
          set surface Glass
          load data
          analyze summary
        """
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
                self.onecmd(cmd_line)
            
            print("\n" + "=" * 60)
            print("✓ Batch processing completed")
            
        except Exception as e:
            print(f"✗ Batch execution failed: {e}")
    
    # ==================== 유틸리티 명령 ====================
    
    def do_clear(self, arg):
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def do_history(self, arg):
        """Display command history"""
        if hasattr(self, 'cmdqueue'):
            print("\n=== Command History ===")
            for i, cmd in enumerate(self.cmdqueue, 1):
                print(f"{i:3d}. {cmd}")
    
    def do_exit(self, arg):
        """Exit program"""
        print("\nGoodbye!")
        return True
    
    def do_quit(self, arg):
        """Exit program (same as exit)"""
        return self.do_exit(arg)
    
    def do_EOF(self, arg):
        """Exit with Ctrl+D"""
        print()
        return self.do_exit(arg)
    
    # ==================== 도움말 ====================
    
    def help_quick(self):
        """Quick start guide"""
        print("""
=== Quick Start Guide ===

1. Configure settings:
   set height 5.0
   set surface Glass
   set degree 45
   set viscosity 1000
   set number 001

2. Load data:
   load data ./data
   load contour

3. Check data:
   show
   view data

4. Run analysis:
   analyze summary
   analyze diameter

5. Save results:
   export results.csv
        """)
    
    def emptyline(self):
        """Do nothing on empty line"""
        pass
    
    def default(self, line):
        """Handle unknown command"""
        print(f"✗ Unknown command: {line}")
        print("  Type 'help' or '?' to see available commands.")


def main():
    """Main function"""
    try:
        ContactAngleCLI().cmdloop()
    except KeyboardInterrupt:
        print("\n\nExiting.")
        sys.exit(0)


if __name__ == '__main__':
    main()
