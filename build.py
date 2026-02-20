#!/usr/bin/env python3
"""
Converts the Flow Icons VS Code extension to Zed icon theme extensions.
Processes all three variants: deep (dark), dim (dark/muted), dawn (light).
"""

import json
import shutil
from pathlib import Path

SRC_ROOT = Path("/Users/maxktz/.cursor/extensions/thang-nm.flow-icons-1.3.1-universal")
ZED_ROOT = Path(__file__).parent

VARIANTS = [
    {"key": "deep", "label": "Flow Deep", "appearance": "dark"},
    {"key": "dim", "label": "Flow Dim", "appearance": "dark"},
    {"key": "dawn", "label": "Flow Dawn", "appearance": "light"},
]


def convert(variant: dict):
    key = variant["key"]
    label = variant["label"]
    appearance = variant["appearance"]

    src_json = SRC_ROOT / f"{key}.json"
    src_icons = SRC_ROOT / key
    dst_icons = ZED_ROOT / "icons" / key
    dst_json = ZED_ROOT / "icon_themes" / f"flow-{key}.json"

    def icon_path(name: str) -> str:
        return f"./icons/{key}/{name}.png"

    with open(src_json) as f:
        vsc = json.load(f)

    needed: set[str] = set()

    default_file_icon = vsc.get("file", "file")
    needed.add(default_file_icon)

    default_folder = vsc.get("folder", "folder_gray")
    default_folder_open = vsc.get("folderExpanded", "folder_gray_open")
    needed.add(default_folder)
    needed.add(default_folder_open)

    file_suffixes: dict[str, str] = {}
    for ext, icon_name in vsc.get("fileExtensions", {}).items():
        file_suffixes[ext] = icon_name
        needed.add(icon_name)

    file_stems: dict[str, str] = {}
    for filename, icon_name in vsc.get("fileNames", {}).items():
        file_stems[filename] = icon_name
        needed.add(icon_name)

    named_directory_icons: dict[str, dict] = {}
    folder_names_expanded = vsc.get("folderNamesExpanded", {})
    for folder_name, icon_name in vsc.get("folderNames", {}).items():
        expanded_icon = folder_names_expanded.get(folder_name, icon_name + "_open")
        named_directory_icons[folder_name] = {
            "collapsed": icon_path(icon_name),
            "expanded": icon_path(expanded_icon),
        }
        needed.add(icon_name)
        needed.add(expanded_icon)

    file_icons: dict[str, dict] = {"default": {"path": icon_path(default_file_icon)}}
    for icon_name in sorted(
        needed - {default_folder, default_folder_open, default_file_icon}
    ):
        if (src_icons / f"{icon_name}.png").exists():
            file_icons[icon_name] = {"path": icon_path(icon_name)}

    dst_icons.mkdir(parents=True, exist_ok=True)
    copied = missing = 0
    for icon_name in needed:
        src = src_icons / f"{icon_name}.png"
        if src.exists():
            shutil.copy2(src, dst_icons / f"{icon_name}.png")
            copied += 1
        else:
            print(f"  [{key}] missing: {icon_name}.png")
            missing += 1

    theme = {
        "$schema": "https://zed.dev/schema/icon_themes/v0.2.0.json",
        "name": label,
        "author": "thang-nm",
        "themes": [
            {
                "name": label,
                "appearance": appearance,
                "directory_icons": {
                    "collapsed": icon_path(default_folder),
                    "expanded": icon_path(default_folder_open),
                },
                "named_directory_icons": named_directory_icons,
                "file_stems": file_stems,
                "file_suffixes": file_suffixes,
                "file_icons": file_icons,
            }
        ],
    }

    dst_json.parent.mkdir(parents=True, exist_ok=True)
    with open(dst_json, "w") as f:
        json.dump(theme, f, indent=2)

    print(
        f"  {label}: {copied} icons, {len(file_suffixes)} suffixes, "
        f"{len(file_stems)} stems, {len(named_directory_icons)} dirs → {dst_json.name}"
    )


def main():
    for variant in VARIANTS:
        convert(variant)
    print("\nAll variants done.")


if __name__ == "__main__":
    main()
