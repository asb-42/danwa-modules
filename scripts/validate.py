#!/usr/bin/env python3
"""Validate all module manifests against the v3.0.0 schema.

Checks:
1. Each manifest.json is valid JSON and conforms to schemas/module-manifest.json
2. module_id values are unique across all modules
3. Profile files exist and are non-empty
4. SHA-256 checksums match (if present)
"""

import hashlib
import json
import sys
from pathlib import Path

try:
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("ERROR: jsonschema package not installed. Run: pip install jsonschema")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
SCHEMA_PATH = ROOT / "schemas" / "module-manifest.json"
SKIP_DIRS = {".git", ".github", "plans", "scripts", "schemas", "ui-translations"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def find_manifests() -> list[Path]:
    """Find all manifest.json files, skipping non-module directories."""
    results = []
    for p in sorted(ROOT.rglob("manifest.json")):
        rel_parts = p.relative_to(ROOT).parts
        if any(d in SKIP_DIRS for d in rel_parts):
            continue
        results.append(p)
    return results


def validate_manifest(manifest_path: Path, schema: dict) -> list[str]:
    """Validate a single manifest. Returns list of error strings."""
    errors = []
    rel = manifest_path.relative_to(ROOT)

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"{rel}: Invalid JSON: {e}"]

    # Schema validation
    validator = Draft7Validator(schema)
    for error in sorted(validator.iter_errors(manifest), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        errors.append(f"{rel}: Schema error at {path}: {error.message}")

    module_dir = manifest_path.parent

    # Check profile file exists and is non-empty
    profile_file = manifest.get("profile_file", "")
    if profile_file:
        profile_path = module_dir / profile_file
        if not profile_path.exists():
            errors.append(f"{rel}: Profile file not found: {profile_file}")
        elif profile_path.stat().st_size == 0:
            errors.append(f"{rel}: Profile file is empty: {profile_file}")

    # Verify checksum if present
    checksum = manifest.get("checksum", "")
    if checksum and profile_file:
        profile_path = module_dir / profile_file
        if profile_path.exists():
            actual = sha256_file(profile_path)
            if actual != checksum:
                errors.append(
                    f"{rel}: Checksum mismatch for {profile_file}: "
                    f"expected {checksum}, got {actual}"
                )

    return errors


def check_uniqueness(manifests: list[Path]) -> list[str]:
    """Check that all module_ids are unique."""
    errors = []
    seen: dict[str, Path] = {}

    for manifest_path in manifests:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        module_id = manifest.get("module_id", "")
        if not module_id:
            continue

        if module_id in seen:
            errors.append(
                f"Duplicate module_id '{module_id}': "
                f"{seen[module_id].relative_to(ROOT)} and "
                f"{manifest_path.relative_to(ROOT)}"
            )
        else:
            seen[module_id] = manifest_path

    return errors


def main() -> int:
    if not SCHEMA_PATH.exists():
        print(f"ERROR: Schema not found: {SCHEMA_PATH}")
        return 1

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    manifests = find_manifests()

    print(f"Validating {len(manifests)} manifests against {SCHEMA_PATH.relative_to(ROOT)}...")
    print()

    total_errors = []

    # Validate each manifest
    for manifest_path in manifests:
        errs = validate_manifest(manifest_path, schema)
        total_errors.extend(errs)

    # Check uniqueness
    uniqueness_errors = check_uniqueness(manifests)
    total_errors.extend(uniqueness_errors)

    if total_errors:
        print(f"FAILED — {len(total_errors)} error(s):")
        for err in total_errors:
            print(f"  ✗ {err}")
        return 1
    else:
        print(f"OK — All {len(manifests)} manifests are valid.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
