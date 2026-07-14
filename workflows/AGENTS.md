# DOX: workflows/

## Purpose

Workflow template modules (wt-*) defining multi-step agent workflows and execution patterns.

## Ownership

- **Module Pattern**: Each `wt-{uuid}/` directory contains a self-contained workflow template
- **8 modules** total: various workflow configurations for different scenarios

## Local Contracts

- Each module contains: `index.json`, `manifest.json`, content files
- Modules follow the standard Danwa module format
- Workflows reference agent cores, bundles, and LLM profiles

## Work Guidance

- Follow existing module structure when adding new workflows
- Ensure workflow step references are valid
- Update `index.json` when adding/removing modules

## Verification

- Run `python scripts/validate.py` to validate modules
- Check dependency references are valid

## Child DOX Index

| Child | Purpose |
|-------|---------|
| (UUID-named directories, each is a standalone module) |
