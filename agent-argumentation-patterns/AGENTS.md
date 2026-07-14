# DOX: agent-argumentation-patterns/

## Purpose

Argumentation pattern modules (ap-*) defining debate/argumentation strategies for multi-agent discussions.

## Ownership

- **Module Pattern**: Each `ap-{uuid}/` directory contains a self-contained argumentation pattern module
- **12 modules** total: debate strategies, argument structures, reasoning patterns

## Local Contracts

- Each module contains: `index.json`, `manifest.json`, content files
- Modules follow the standard Danwa module format
- UUID-based naming ensures uniqueness

## Work Guidance

- Follow existing module structure when adding new patterns
- Update `index.json` when adding/removing modules
- Validate modules against schemas before commit

## Verification

- Run `python scripts/validate.py` to validate modules
- Check `index.json` consistency

## Child DOX Index

| Child | Purpose |
|-------|---------|
| (UUID-named directories, each is a standalone module) |
