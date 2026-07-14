# DOX: ui-translations/

## Purpose

UI translation modules (lp-*) defining language packs and localization strings for the Danwa Studio interface.

## Ownership

- **Module Pattern**: Each `lp-{uuid}/` directory contains a self-contained translation pack
- **57 modules** total: translations for multiple languages and locales

## Local Contracts

- Each module contains: `index.json`, `manifest.json`, translation files
- Modules follow the standard Danwa module format
- Translation files use JSON format with nested key structure

## Work Guidance

- Follow existing module structure when adding new translations
- Ensure translation keys are consistent across languages
- Update `index.json` when adding/removing modules

## Verification

- Run `python scripts/validate.py` to validate modules
- Check translation key coverage

## Child DOX Index

| Child | Purpose |
|-------|---------|
| (UUID-named directories, each is a standalone module) |
