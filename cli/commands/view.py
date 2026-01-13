"""View / visualization plugin.

Implements an image viewer based on the original `interactive_cli.py` logic.
"""

import os
import json
import cv2
import numpy as np


def cmd_view(cli, arg):
    args = arg.strip().split()
    mode = None
    for a in args:
        if a in ['-i', '-image']:
            mode = 'image'
        elif a in ['-c', '-contour']:
            mode = 'contour'
        elif a in ['-b', '-binary']:
            mode = 'binary'
    if mode == 'image' or not args:
        return _view_image(cli)


def _view_image(cli):
    img_num = 0

    def trackbar(x):
        nonlocal img_num
        img_num = cv2.getTrackbarPos("frame", "Image Viewer")

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

    src = os.path.join(cli.workdir, f"{cli.settings['height']}CM_{cli.settings['surface']}_{cli.settings['degree']}_{cli.settings['viscosity']}_{cli.settings['number']}")
    src = src + '/folder_info.json'

    if not os.path.exists(src):
        print(f"✗ Config file not found: {src}")
        return

    try:
        with open(src, 'r', encoding='utf-8') as f:
            config = json.load(f)
        rawimage_path = config.get('rawimage_path')
        cli.scalenumber = config.get('scalenumber')
        cli.imagetype = config.get('imagetype')
        cli.imagenumber = config.get('imagenumber')
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON format: {e}")
        return
    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        return

    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif'}
    image_files = []
    try:
        for file in sorted(os.listdir(rawimage_path)):
            file_path = os.path.join(rawimage_path, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in image_extensions:
                    image_files.append(file_path)
    except Exception as e:
        print(f"✗ Failed to read images from {rawimage_path}: {e}")
        return

    if not image_files:
        print(f"✗ No images found in {rawimage_path}")
        return

    print("\n" + "="*60)
    print("Current Settings:")
    print(f"  Height       : {cli.settings['height']} CM")
    print(f"  Surface      : {cli.settings['surface']}")
    print(f"  Degree       : {cli.settings['degree']}")
    print(f"  Viscosity    : {cli.settings['viscosity']}")
    print(f"  Number       : {cli.settings['number']}")
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
            h, w = _img.shape[:2]
            scale = min(window_width / w, window_height / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            resized_img = cv2.resize(_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            canvas = np.zeros((window_height, window_width, 3), dtype=np.uint8)
            x_offset = (window_width - new_w) // 2
            y_offset = (window_height - new_h) // 2
            canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_img
            cv2.imshow("Image Viewer", canvas)
        else:
            print(f"✗ Failed to load image: {imagesrc}")
            break
    cv2.destroyAllWindows()


commands = {
    'view': cmd_view,
}

