# DOX: scripts/

## Purpose

Python scripts for module management: validation, indexing, building, migration, and release.

## Ownership

- **Validation**: `validate.py` — module schema validation
- **Indexing**: `generate_index.py` — generate module index.json
- **Building**: `build_zips.py`, `build_translations.py` — build artifacts
- **Migration**: `migrate_modules.py`, `migrate_translations.py` — data migration
- **Release**: `release.py` — release management
- **Translations**: `generate_translations.py` — translation generation
- **Translations Data**: `translations/` — translation source files

## Local Contracts

- Scripts use Python with standard library + requests
- Scripts are idempotent where possible
- Scripts log progress and errors

## Work Guidance

- Test scripts before commit
- Maintain idempotency for migration scripts
- Document script usage in docstrings

## Verification

- Run scripts in dry-run mode when available
- Verify output correctness

## Child DOX Index

| Child | Purpose |
|-------|---------|
| `translations/` | Translation source files |
