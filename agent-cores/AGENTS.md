# DOX: agent-cores/

## Purpose

Agent core modules (ac-*) defining fundamental agent personalities, roles, and capabilities.

## Ownership

- **Module Pattern**: Each `ac-{uuid}/` directory contains a self-contained agent core
- **35 modules** total: advocate, adversary, referee, reviewer, reviser, interviewer, interviewee, and specialized roles

## Local Contracts

- Each module contains: `index.json`, `manifest.json`, content files
- Modules follow the standard Danwa module format
- Cores are foundational building blocks for bundles

## Work Guidance

- Follow existing module structure when adding new cores
- Ensure core definitions are complete and self-contained
- Update `index.json` when adding/removing modules

## Verification

- Run `python scripts/validate.py` to validate modules
- Check `index.json` consistency

## Child DOX Index

| Child | Purpose |
|-------|---------|
| (UUID-named directories, each is a standalone module) |
