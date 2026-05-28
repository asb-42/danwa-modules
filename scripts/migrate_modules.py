#!/usr/bin/env python3
"""Migrate modules from Danwa main project to danwa-modules repository.

Copies all module directories, upgrades manifest.json to schema v3.0.0,
adds compatibility/repository fields, and recalculates checksums.
"""

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_ROOT = Path("/media/data/coding/danwa/modules")
TARGET_ROOT = Path(__file__).parent.parent

# Directory mapping: source_dir → target_dir
# If source_dir not in this map, it's copied as-is
DIR_MAP = {
    "prompt-modifiers": "agent-prompt-modifiers",
    "prompt-modifier-text-only": "agent-prompt-modifiers",  # will be nested
}

# Standalone modules that need special handling (not under a category dir)
STANDALONE_MODULES = {
    "prompt-modifier-text-only": "agent-prompt-modifiers/prompt-modifier-text-only",
}

REPO_URL = "https://github.com/asb-42/danwa-modules"
DANWA_MIN_VERSION = "2.1.0"


def sha256_of_file(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def upgrade_manifest(manifest: dict, module_dir: Path, version_tag: str | None = None) -> dict:
    """Upgrade a manifest from v1/v2 to v3.0.0."""
    now = datetime.now(timezone.utc).isoformat()

    # Upgrade schema version
    manifest["schema_version"] = "3.0.0"

    # Add compatibility block if not present
    if "compatibility" not in manifest:
        manifest["compatibility"] = {
            "danwa_min_version": DANWA_MIN_VERSION,
            "danwa_max_version": None,
        }

    # Add repository block if not present
    if "repository" not in manifest:
        ref = version_tag or f"v{manifest.get('version', '1.0.0')}"
        manifest["repository"] = {
            "type": "github",
            "url": REPO_URL,
            "ref": ref,
        }

    # Ensure profile_file + profile_format exist (detect from directory)
    if "profile_file" not in manifest:
        for fname, fmt in [
            ("profile.yaml", "yaml"),
            ("profile.json", "json"),
            ("profile.md", "markdown"),
        ]:
            if (module_dir / fname).exists():
                manifest["profile_file"] = fname
                manifest["profile_format"] = fmt
                break

    # Recalculate checksum of profile file
    profile_file = manifest.get("profile_file", "")
    if profile_file:
        profile_path = module_dir / profile_file
        if profile_path.exists():
            manifest["checksum"] = sha256_of_file(profile_path)

    # Remove legacy empty files array if profile_file is present
    if "files" in manifest and manifest.get("profile_file"):
        if not manifest["files"]:  # empty array
            del manifest["files"]

    # Update timestamps
    if "created_at" not in manifest:
        manifest["created_at"] = now
    manifest["updated_at"] = now

    return manifest


def copy_module(source_dir: Path, target_dir: Path, version_tag: str | None = None) -> bool:
    """Copy a single module directory and upgrade its manifest."""
    manifest_path = source_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"  SKIP (no manifest): {source_dir}")
        return False

    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy all files
    for item in source_dir.iterdir():
        dest = target_dir / item.name
        if item.is_file():
            shutil.copy2(item, dest)
        elif item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)

    # Read and upgrade manifest
    with open(target_dir / "manifest.json", "r") as f:
        manifest = json.load(f)

    manifest = upgrade_manifest(manifest, target_dir, version_tag)

    # Write upgraded manifest
    with open(target_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    module_id = manifest.get("module_id", target_dir.name)
    version = manifest.get("version", "?")
    print(f"  OK: {module_id} v{version}")
    return True


def migrate_category(category_dir: Path, target_category: str) -> int:
    """Migrate all modules in a category directory."""
    count = 0
    target_base = TARGET_ROOT / target_category

    for module_dir in sorted(category_dir.iterdir()):
        if not module_dir.is_dir():
            continue
        target_dir = target_base / module_dir.name
        if copy_module(module_dir, target_dir):
            count += 1

    return count


def main():
    if not SOURCE_ROOT.exists():
        print(f"ERROR: Source directory not found: {SOURCE_ROOT}")
        sys.exit(1)

    total = 0
    now = datetime.now(timezone.utc)
    version_tag = None  # will be set on first release

    print("Migrating modules from Danwa to danwa-modules...")
    print(f"Source: {SOURCE_ROOT}")
    print(f"Target: {TARGET_ROOT}")
    print()

    # Process standard category directories
    for category_dir in sorted(SOURCE_ROOT.iterdir()):
        if not category_dir.is_dir():
            continue

        cat_name = category_dir.name

        # Handle standalone modules
        if cat_name in STANDALONE_MODULES:
            target_path = TARGET_ROOT / STANDALONE_MODULES[cat_name]
            print(f"[{cat_name}] → {STANDALONE_MODULES[cat_name]}")
            if copy_module(category_dir, target_path):
                total += 1
            continue

        # Map directory name or use as-is
        target_category = DIR_MAP.get(cat_name, cat_name)
        print(f"[{cat_name}] → {target_category}/")

        count = migrate_category(category_dir, target_category)
        total += count
        print(f"  Migrated {count} modules")
        print()

    print(f"\nDone! Total modules migrated: {total}")

    # Print summary
    print("\nSummary by category:")
    for cat_dir in sorted(TARGET_ROOT.iterdir()):
        if not cat_dir.is_dir() or cat_dir.name.startswith(".") or cat_dir.name in ("plans", "scripts", "schemas", "ui-translations"):
            continue
        modules = [d for d in cat_dir.iterdir() if d.is_dir() and (d / "manifest.json").exists()]
        if modules:
            print(f"  {cat_dir.name}/: {len(modules)} modules")


if __name__ == "__main__":
    main()
