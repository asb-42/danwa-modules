#!/usr/bin/env python3
"""Build module ZIP archives for GitHub Releases.

Creates a ZIP file for every module directory that contains a
``manifest.json``.  The ZIP includes *all* files (including
``manifest.json``) so that ``ModuleInstaller.install_from_url()``
can discover the manifest after extraction.

Output directory: ``releases/``  (created if missing)
ZIP naming:       ``releases/{module_id}.zip``

Usage:
    python scripts/build_zips.py              # Build all ZIPs
    python scripts/build_zips.py --clean      # Remove releases/ first
    python scripts/build_zips.py --dry-run    # Show what would be built
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELEASES_DIR = ROOT / "releases"

SKIP_DIRS = {".git", ".github", "plans", "scripts", "schemas", "releases"}


def find_modules() -> list[tuple[Path, str]]:
    """Return ``(module_dir, module_id)`` for every module in the repo."""
    modules: list[tuple[Path, str]] = []
    for manifest_path in sorted(ROOT.rglob("manifest.json")):
        rel_parts = manifest_path.relative_to(ROOT).parts
        if any(p in SKIP_DIRS for p in rel_parts):
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"  WARN: Cannot parse {manifest_path}: {exc}", file=sys.stderr)
            continue
        module_id = manifest.get("module_id", manifest_path.parent.name)
        modules.append((manifest_path.parent, module_id))
    return modules


def build_zip(module_dir: Path, module_id: str, releases_dir: Path) -> Path:
    """Create a ZIP archive for *module_dir* and return the path.

    Rejects archive entry names containing ``..`` segments to prevent
    Zip Slip path-traversal on extraction (supply-side defence).
    """
    zip_path = releases_dir / f"{module_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(module_dir.rglob("*")):
            if f.is_file():
                arcname = f.relative_to(module_dir).as_posix()
                # Reject path-traversal entries (supply-side Zip Slip defence)
                if ".." in arcname.split("/"):
                    print(f"  WARN: Skipping path-traversal entry: {arcname}", file=sys.stderr)
                    continue
                zf.write(f, arcname)
    return zip_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build module ZIPs")
    parser.add_argument("--clean", action="store_true", help="Remove releases/ before building")
    parser.add_argument("--dry-run", action="store_true", help="Only list modules, don't build")
    args = parser.parse_args()

    modules = find_modules()
    if not modules:
        print("No modules found.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f"=== Dry run: {len(modules)} modules would be built ===")
        for _, mid in modules:
            print(f"  {mid}.zip")
        return

    if args.clean and RELEASES_DIR.exists():
        import shutil
        shutil.rmtree(RELEASES_DIR)
        print("Cleaned releases/ directory.")

    RELEASES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"=== Building {len(modules)} module ZIPs ===")
    for module_dir, module_id in modules:
        zip_path = build_zip(module_dir, module_id, RELEASES_DIR)
        size_kb = zip_path.stat().st_size / 1024
        print(f"  {zip_path.name:50s} ({size_kb:7.1f} KB)")

    print(f"\nDone! {len(modules)} ZIPs in {RELEASES_DIR}")


if __name__ == "__main__":
    main()
