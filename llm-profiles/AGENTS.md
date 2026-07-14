# DOX: llm-profiles/

## Purpose

LLM profile modules (llm-*) defining model configurations, parameters, and provider settings.

## Ownership

- **Module Pattern**: Each `llm-{uuid}/` directory contains a self-contained LLM profile
- **21 modules** total: various LLM configurations for different providers and use cases

## Local Contracts

- Each module contains: `index.json`, `manifest.json`, content files
- Modules follow the standard Danwa module format
- Profiles define model parameters, providers, and capabilities

## Work Guidance

- Follow existing module structure when adding new profiles
- Ensure provider references are valid
- Update `index.json` when adding/removing modules

## Verification

- Run `python scripts/validate.py` to validate modules
- Check `index.json` consistency

## Child DOX Index

| Child | Purpose |
|-------|---------|
| (UUID-named directories, each is a standalone module) |
