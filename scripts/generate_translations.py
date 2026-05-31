#!/usr/bin/env python3
"""Generate all translation files from per-locale JSON data files.

Reads English keys from scripts/translations/en.json (source of truth).
For each locale, reads scripts/translations/{locale}.json if available.
Missing keys fall back to English values.

Usage:
  python scripts/generate_translations.py --all          # all locales
  python scripts/generate_translations.py fr             # single locale
  python scripts/generate_translations.py --stats        # coverage report
  python scripts/generate_translations.py --validate     # check all locale files exist
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TRANSLATIONS_DIR = Path(__file__).parent / "translations"
EN_SOURCE = Path(__file__).parent / "translations" / "en.json"

ALL_LOCALES = [
    "bg", "bn", "bo", "br", "cz", "da", "de", "en", "eo", "es", "et", "eu",
    "fa", "fi", "fr", "ga", "hi", "hr", "hu", "hy", "id", "io", "is",
    "it", "iu", "ja", "ka", "ko", "ku", "la", "lt", "lv", "mi", "mk", "mr",
    "ms", "nb", "nl", "nn", "pl", "pt", "ro", "ru", "sa", "sk", "sl",
    "sq", "sr", "ta", "te", "th", "tl", "tr", "ur", "vi", "yi", "zh",
]

SKIP_LOCALES = {"en", "de"}  # en = source; de = from de.js


def load_json(path: Path) -> dict:
    """Load a JSON file and return its contents."""
    return json.loads(path.read_text(encoding="utf-8"))


def get_en_keys() -> dict:
    """Load the English source keys."""
    return load_json(EN_SOURCE)


def get_locale_translations(locale: str) -> dict:
    """Load translations for a locale from its JSON file, if available."""
    locale_file = TRANSLATIONS_DIR / f"{locale}.json"
    if locale_file.exists():
        return load_json(locale_file)
    return {}


def generate(locale: str) -> dict:
    """Generate ui_strings.json for a locale. Returns stats dict."""
    en = get_en_keys()
    translations = get_locale_translations(locale)

    result = {}
    translated = 0
    fallback = 0
    for key, en_value in en.items():
        if key in translations:
            result[key] = translations[key]
            translated += 1
        else:
            result[key] = en_value
            fallback += 1

    out_dir = ROOT / "ui-translations" / f"lang-{locale}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ui_strings.json"
    out_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    total = len(en)
    pct = (translated / total * 100) if total else 0
    print(f"[{locale:>3}] {total} keys | {translated} translated ({pct:.1f}%) | {fallback} fallback")
    return {"locale": locale, "total": total, "translated": translated, "fallback": fallback, "pct": pct}


def generate_all() -> None:
    """Generate translation files for all non-source locales."""
    results = []
    for locale in ALL_LOCALES:
        if locale in SKIP_LOCALES:
            continue
        results.append(generate(locale))

    print(f"\nDone. Generated {len(results)} translation files.")
    # Summary
    full = sum(1 for r in results if r["pct"] >= 100)
    partial = sum(1 for r in results if 0 < r["pct"] < 100)
    empty = sum(1 for r in results if r["pct"] == 0)
    print(f"  100% coverage: {full} locales")
    print(f"  Partial:       {partial} locales")
    print(f"  No translations: {empty} locales")


def show_stats() -> None:
    """Show coverage statistics for all locales."""
    en = get_en_keys()
    total = len(en)
    print(f"English source: {total} keys\n")
    print(f"{'Locale':>6} {'Translated':>10} {'Fallback':>10} {'Coverage':>8}")
    print("-" * 40)
    for locale in ALL_LOCALES:
        if locale in SKIP_LOCALES:
            continue
        translations = get_locale_translations(locale)
        translated = sum(1 for k in en if k in translations)
        fallback = total - translated
        pct = (translated / total * 100) if total else 0
        marker = " ✓" if pct >= 100 else ""
        print(f"{locale:>6} {translated:>10} {fallback:>10} {pct:>7.1f}%{marker}")


def validate_locales() -> None:
    """Check which locale files exist and their key counts."""
    en = get_en_keys()
    total = len(en)
    missing = []
    incomplete = []
    for locale in ALL_LOCALES:
        if locale in SKIP_LOCALES:
            continue
        locale_file = TRANSLATIONS_DIR / f"{locale}.json"
        if not locale_file.exists():
            missing.append(locale)
        else:
            translations = load_json(locale_file)
            if len(translations) < total:
                incomplete.append((locale, len(translations), total))

    if missing:
        print(f"Missing locale files ({len(missing)}): {', '.join(missing)}")
    else:
        print("All locale files present.")

    if incomplete:
        print(f"\nIncomplete translations ({len(incomplete)}):")
        for locale, count, tot in incomplete:
            pct = count / tot * 100
            print(f"  {locale}: {count}/{tot} ({pct:.1f}%)")
    else:
        print("All locale files have complete translations.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--all":
            generate_all()
        elif cmd == "--stats":
            show_stats()
        elif cmd == "--validate":
            validate_locales()
        else:
            generate(cmd)
    else:
        print("Usage:")
        print("  python scripts/generate_translations.py --all")
        print("  python scripts/generate_translations.py fr")
        print("  python scripts/generate_translations.py --stats")
        print("  python scripts/generate_translations.py --validate")
