#!/usr/bin/env python3
"""Generate index.json from all module manifests.

Recursively finds all manifest.json files, extracts metadata,
computes checksums, and writes a compiled catalog to index.json.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKIP_DIRS = {".git", ".github", "plans", "scripts", "schemas"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def find_category(module_dir: Path) -> str:
    """Derive category from the parent directory name."""
    parts = module_dir.relative_to(ROOT).parts
    return parts[0] if len(parts) > 1 else ""


def build_module_entry(manifest_path: Path) -> dict | None:
    """Build an index entry for a single module."""
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"  WARN: Cannot parse {manifest_path}: {e}", file=sys.stderr)
        return None

    module_dir = manifest_path.parent
    module_id = manifest.get("module_id", module_dir.name)
    version = manifest.get("version", "0.0.0")

    # Compute checksum of profile file
    profile_file = manifest.get("profile_file", "")
    profile_checksum = ""
    if profile_file:
        profile_path = module_dir / profile_file
        if profile_path.exists():
            profile_checksum = sha256_file(profile_path)

    # Compute overall module checksum (all files except manifest.json)
    all_files = sorted(
        f for f in module_dir.rglob("*")
        if f.is_file() and f.name != "manifest.json"
    )
    module_checksum = ""
    if all_files:
        h = hashlib.sha256()
        for f in all_files:
            h.update(f.read_bytes())
        module_checksum = h.hexdigest()

    category = find_category(module_dir)
    download_url = (
        f"https://github.com/asb-42/danwa-modules/releases/download/"
        f"v{version}/{module_id}.zip"
    )

    entry = {
        "module_id": module_id,
        "version": version,
        "type": manifest.get("type", ""),
        "category": category,
        "name": manifest.get("name", {}),
        "description": manifest.get("description", {}),
        "language": manifest.get("language", ""),
        "profile_file": profile_file,
        "profile_checksum_sha256": profile_checksum,
        "module_checksum_sha256": module_checksum,
        "download_url": download_url,
        "compatibility": manifest.get("compatibility", {}),
        "dependencies": manifest.get("dependencies", {}),
        "tags": manifest.get("tags", []),
        "license": manifest.get("license", ""),
        "created_at": manifest.get("created_at", ""),
        "updated_at": manifest.get("updated_at", ""),
    }

    return entry


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    modules = []

    for manifest_path in sorted(ROOT.rglob("manifest.json")):
        # Skip non-module directories
        rel_parts = manifest_path.relative_to(ROOT).parts
        if any(p in SKIP_DIRS for p in rel_parts):
            continue

        entry = build_module_entry(manifest_path)
        if entry:
            modules.append(entry)

    index = {
        "generated_at": now,
        "schema_version": "3.0.0",
        "repository": "https://github.com/asb-42/danwa-modules",
        "total_modules": len(modules),
        "modules": modules,
    }

    output_path = ROOT / "index.json"
    output_path.write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Generated index.json with {len(modules)} modules → {output_path}")


if __name__ == "__main__":
    main()
