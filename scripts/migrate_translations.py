#!/usr/bin/env python3
"""Extract translation ZIPs into proper module directories with v3.0.0 manifests.

Takes the 55 lang-*-custom.zip files under ui-translations/ and:
1. Extracts each into ui-translations/lang-{locale}-custom/
2. Upgrades manifest.json to schema v3.0.0
3. Recalculates SHA-256 checksum
4. Adds compatibility and repository fields
5. Removes the ZIP files after successful extraction
"""

import hashlib
import json
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
TRANSLATIONS_DIR = ROOT / "ui-translations"
REPO_URL = "https://github.com/asb-42/danwa-modules"
DANWA_MIN_VERSION = "2.1.0"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def process_zip(zip_path: Path) -> bool:
    """Extract a translation ZIP and upgrade its manifest."""
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            # Find the manifest and profile inside the ZIP
            names = zf.namelist()
            manifest_name = None
            profile_name = None
            for n in names:
                if n.endswith("manifest.json"):
                    manifest_name = n
                elif n.endswith("ui_strings.json"):
                    profile_name = n

            if not manifest_name:
                print(f"  SKIP (no manifest): {zip_path.name}")
                return False

            # Read manifest from ZIP
            manifest = json.loads(zf.read(manifest_name))

            # Determine target directory name from ZIP filename
            # lang-de-custom.zip → lang-de-custom
            dir_name = zip_path.stem  # removes .zip
            target_dir = TRANSLATIONS_DIR / dir_name
            target_dir.mkdir(parents=True, exist_ok=True)

            # Extract all files
            zf.extractall(TRANSLATIONS_DIR)

            # Upgrade manifest to v3.0.0
            now = datetime.now(timezone.utc).isoformat()
            manifest["schema_version"] = "3.0.0"

            if "compatibility" not in manifest:
                manifest["compatibility"] = {
                    "danwa_min_version": DANWA_MIN_VERSION,
                    "danwa_max_version": None,
                }

            if "repository" not in manifest:
                manifest["repository"] = {
                    "type": "github",
                    "url": REPO_URL,
                    "ref": f"v{manifest.get('version', '1.0.0')}",
                }

            # Ensure profile_file is set
            if "profile_file" not in manifest:
                manifest["profile_file"] = "ui_strings.json"
                manifest["profile_format"] = "json"

            # Recalculate checksum
            profile_path = target_dir / manifest.get("profile_file", "ui_strings.json")
            if profile_path.exists():
                manifest["checksum"] = sha256_file(profile_path)
                # Count translated strings
                try:
                    strings = json.loads(profile_path.read_text(encoding="utf-8"))
                    manifest["string_count"] = len(strings)
                except Exception:
                    pass

            # Update timestamp
            if "created_at" not in manifest:
                manifest["created_at"] = now
            manifest["updated_at"] = now

            # Remove empty files array if present
            if "files" in manifest and not manifest["files"]:
                del manifest["files"]

            # Write upgraded manifest
            manifest_path = target_dir / "manifest.json"
            manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            module_id = manifest.get("module_id", dir_name)
            locale = manifest.get("language", "?")
            strings = manifest.get("string_count", "?")
            print(f"  OK: {module_id} ({locale}, {strings} strings)")
            return True

    except Exception as e:
        print(f"  ERROR: {zip_path.name}: {e}")
        return False


def main():
    if not TRANSLATIONS_DIR.exists():
        print(f"ERROR: Directory not found: {TRANSLATIONS_DIR}")
        sys.exit(1)

    zips = sorted(TRANSLATIONS_DIR.glob("lang-*-custom.zip"))
    print(f"Found {len(zips)} translation ZIPs in {TRANSLATIONS_DIR}")
    print()

    success = 0
    for zip_path in zips:
        if process_zip(zip_path):
            success += 1

    print(f"\nExtracted {success}/{len(zips)} translation modules.")

    # Remove ZIP files after successful extraction
    if success > 0:
        remaining_zips = list(TRANSLATIONS_DIR.glob("lang-*-custom.zip"))
        print(f"\nRemoving {len(remaining_zips)} ZIP files...")
        for z in remaining_zips:
            z.unlink()
        print("Done.")

    # Summary
    print("\nTranslation modules:")
    for d in sorted(TRANSLATIONS_DIR.iterdir()):
        if d.is_dir() and (d / "manifest.json").exists():
            m = json.loads((d / "manifest.json").read_text())
            locale = m.get("language", "?")
            strings = m.get("string_count", "?")
            print(f"  {d.name}: {locale} ({strings} strings)")


if __name__ == "__main__":
    main()
