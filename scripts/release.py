#!/usr/bin/env python3
"""Release script — bumps semver tag and pushes to trigger CI.

Reads the latest ``v*`` tag, bumps the requested segment (patch by default),
commits any pending changes, creates the tag, and pushes both.

Usage:
    python scripts/release.py                # auto-bump patch: v1.0.0 → v1.0.1
    python scripts/release.py --minor        # bump minor:     v1.0.0 → v1.1.0
    python scripts/release.py --major        # bump major:     v1.0.0 → v2.0.0
    python scripts/release.py --version 2.0.0  # explicit version
    python scripts/release.py --dry-run      # show what would happen
    python scripts/release.py --no-push      # tag locally only
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], *, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a shell command and return the result."""
    return subprocess.run(
        cmd,
        cwd=ROOT,
        check=check,
        capture_output=capture,
        text=True,
    )


def get_latest_tag() -> str | None:
    """Return the latest semver tag or None if none exists."""
    result = run(["git", "tag", "--list", "v*", "--sort=-version:refname"])
    tags = [t.strip() for t in result.stdout.strip().splitlines() if t.strip()]
    return tags[0] if tags else None


def bump_version(version: str, segment: str = "patch") -> str:
    """Bump a semver version string.

    >>> bump_version("1.0.0", "patch")
    '1.0.1'
    >>> bump_version("1.0.9", "patch")
    '1.0.10'
    >>> bump_version("1.2.3", "minor")
    '1.3.0'
    >>> bump_version("1.2.3", "major")
    '2.0.0'
    """
    match = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", version)
    if not match:
        print(f"ERROR: '{version}' is not a valid semver tag.", file=sys.stderr)
        sys.exit(1)
    major, minor, patch = int(match[1]), int(match[2]), int(match[3])
    if segment == "major":
        return f"{major + 1}.0.0"
    if segment == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def has_uncommitted_changes() -> bool:
    """Check if the working tree has uncommitted changes."""
    result = run(["git", "status", "--porcelain"])
    return bool(result.stdout.strip())


def has_staged_changes() -> bool:
    """Check if there are staged (but not committed) changes."""
    result = run(["git", "diff", "--cached", "--name-only"])
    return bool(result.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Bump semver tag and push to trigger CI")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--major", action="store_true", help="Bump major version (vX.0.0)")
    group.add_argument("--minor", action="store_true", help="Bump minor version (vX.Y.0)")
    group.add_argument("--patch", action="store_true", help="Bump patch version (vX.Y.Z) [default]")
    group.add_argument("--version", type=str, help="Set explicit version (e.g. 2.0.0)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen, don't execute")
    parser.add_argument("--no-push", action="store_true", help="Tag locally but don't push")
    parser.add_argument("--no-commit", action="store_true", help="Skip auto-commit of pending changes")
    parser.add_argument("-m", "--message", type=str, help="Commit message (used when auto-committing)")
    args = parser.parse_args()

    # Determine bump segment
    if args.version:
        new_version = args.version.lstrip("v")
    else:
        segment = "major" if args.major else "minor" if args.minor else "patch"
        latest = get_latest_tag()
        if latest is None:
            print("No existing tags found. Starting from v0.1.0.")
            latest = "v0.1.0"
        else:
            print(f"Latest tag: {latest}")
        new_version = bump_version(latest, segment)

    new_tag = f"v{new_version}"
    print(f"Next tag: {new_tag}")

    if args.dry_run:
        dirty = has_uncommitted_changes()
        print(f"\n=== Dry run complete ===")
        print(f"  Would create tag: {new_tag}")
        if dirty and not args.no_commit:
            print(f"  Would auto-commit pending changes first")
        elif dirty:
            print(f"  WARNING: Working tree has uncommitted changes (--no-commit)")
        print(f"  Would push: {'no (--no-push)' if args.no_push else 'yes'}")
        return

    # Regenerate index.json before committing
    gen_index = ROOT / "scripts" / "generate_index.py"
    if gen_index.exists():
        print("Regenerating index.json...")
        idx_result = run([sys.executable, str(gen_index)], check=False)
        if idx_result.returncode != 0:
            print(f"WARNING: generate_index.py failed (exit {idx_result.returncode})", file=sys.stderr)
            print(idx_result.stderr, file=sys.stderr)

    # Auto-commit pending changes if needed
    if not args.no_commit and has_uncommitted_changes():
        msg = args.message or f"release: prepare {new_tag}"
        print(f"Auto-committing pending changes: {msg}")
        run(["git", "add", "-A"])
        run(["git", "commit", "-m", msg])

    # Verify clean working tree
    if has_uncommitted_changes():
        print("ERROR: Working tree has uncommitted changes.", file=sys.stderr)
        print("  Run with --no-commit or commit manually first.", file=sys.stderr)
        sys.exit(1)

    # Create annotated tag
    print(f"Creating tag {new_tag}...")
    run(["git", "tag", "-a", new_tag, "-m", f"Release {new_tag}"])

    if args.no_push:
        print(f"Tag {new_tag} created locally (--no-push).")
        print(f"Push later with: git push origin {new_tag}")
        return

    # Push commit + tag
    print("Pushing commit and tag...")
    run(["git", "push"])
    run(["git", "push", "origin", new_tag])

    print(f"\n✅ Released {new_tag} — CI workflow should start automatically.")
    print(f"   https://github.com/asb-42/danwa-modules/actions")


if __name__ == "__main__":
    main()
