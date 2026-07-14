# DOX: agent-bundles/

## Purpose

Agent bundle modules (bd-*) defining complete agent configurations with roles, prompts, and behavior settings.

## Ownership

- **Module Pattern**: Each `bd-{uuid}/` directory contains a self-contained agent bundle
- **15 modules** total: pre-configured agent bundles for different use cases

## Local Contracts

- Each module contains: `index.json`, `manifest.json`, content files
- Modules follow the standard Danwa module format
- Bundles reference other modules (cores, profiles, patterns)

## Work Guidance

- Follow existing module structure when adding new bundles
- Ensure bundle references are valid module UUIDs
- Update `index.json` when adding/removing modules

## Verification

- Run `python scripts/validate.py` to validate modules
- Check dependency references are valid

## Child DOX Index

| Child | Purpose |
|-------|---------|
| (UUID-named directories, each is a standalone module) |
