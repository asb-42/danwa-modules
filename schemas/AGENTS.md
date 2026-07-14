# DOX: schemas/

## Purpose

JSON Schema definitions for Danwa module formats: manifest, action templates, and migration guides.

## Ownership

- **Module Manifest**: `module-manifest.json` — schema for module manifest files
- **Action Template**: `action-template.json` — schema for action template modules
- **Migration Guide**: `migration-guide.md` — documentation for module format migrations

## Local Contracts

- All modules must validate against their respective schemas
- Schema changes require version bumps and migration guides

## Work Guidance

- Update schemas when module format changes
- Maintain backward compatibility where possible
- Document schema changes in migration guide

## Verification

- Validate modules against schemas
- Check schema references in module manifests

## Child DOX Index

| Child | Purpose |
|-------|---------|
| (flat structure, 3 files) |
