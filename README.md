# danwa-modules

Community module repository for the [Danwa Debate Engine](https://github.com/asb-42/danwa).

## Overview

This repository contains installable modules for Danwa (155 modules total):

| Category | Directory | Modules | Description |
|----------|-----------|---------|-------------|
| Agent Cores | [`agent-cores/`](agent-cores/) | 34 | Agent personas and role types |
| Agent Bundles | [`agent-bundles/`](agent-bundles/) | 15 | Pre-configured agent groups |
| Argumentation Patterns | [`agent-argumentation-patterns/`](agent-argumentation-patterns/) | 12 | Prompt variants for debate roles |
| LLM Profiles | [`llm-profiles/`](llm-profiles/) | 21 | LLM provider configurations |
| UI Translations | [`ui-translations/`](ui-translations/) | 57 | Language packs (57 locales) |
| Workflows | [`workflows/`](workflows/) | 8 | Multi-agent workflow templates |
| Tone Profiles | [`agent-tone-profiles/`](agent-tone-profiles/) | 3 | Debate tone and style presets |
| Prompt Modifiers | [`agent-prompt-modifiers/`](agent-prompt-modifiers/) | 2 | Output formatting modifiers |
| Interactive Templates | [`interactive-action-templates/`](interactive-action-templates/) | 1 | Default action templates for interactive mode |
| Synthesizer Patterns | [`synthesizer-patterns/`](synthesizer-patterns/) | 1 | Synthesizer pattern modules |
| Kitsune Assistant | [`kitsune-assistant/`](kitsune-assistant/) | 1 | Kitsune assistant system prompts |

## Installation

Modules can be installed directly from this repository via the Danwa UI (Build → Modules → GitHub)
or via the API:

```
POST /api/v1/modules/install-from-repo
{
  "source": "github",
  "repo": "asb-42/danwa-modules",
  "module_id": "bundle-critic",
  "version": "1.0.0"
}
```

## Module Structure

Each module lives in its own directory under its category:

```
{category}/{module-name}/
├── manifest.json    # Module metadata and schema
└── profile.{yaml,json,md}  # Module content
```

### Manifest Schema

All modules use `manifest.json` following the [v3.0.0 schema](schemas/module-manifest.json).

Key fields:
- `module_id` — unique identifier (e.g. `ac-{uuid}`)
- `version` — semantic version (`MAJOR.MINOR.PATCH`)
- `type` — module type (e.g. `agent-persona`, `workflow-template`)
- `compatibility` — Danwa version requirements
- `repository` — source repository reference

## Available Modules

The catalog of all available modules with download links is published as [`index.json`](index.json) with each release.

## Development

### Validation

All manifests are validated against the schema on every push and PR:

```bash
# Local validation (requires Python 3.11+)
python scripts/validate.py
```

### Index Generation

```bash
# Regenerate index.json from all module manifests
python scripts/generate_index.py
```

### Publishing

Releases are published automatically when a `v*` tag is pushed:

```bash
git tag v1.0.0
git push origin v1.0.0
```

This triggers the [publish workflow](.github/workflows/publish.yml) which:
1. Validates all manifests
2. Builds ZIP archives for each module
3. Generates `index.json` with checksums and download URLs
4. Creates a GitHub Release with all assets

## Translation Limitations

The following UI translation locales currently use English fallback values (no translation file exists). These languages require expert review or an external translation service before they can be considered production-ready:

| Locale | Language | Script | Status |
|--------|----------|--------|--------|
| `iu` | Inuktitut (ᐃᓄᒃᑎᑐᑦ) | Canadian Aboriginal Syllabics | No translation file — English fallback |
| `te` | Telugu (తెలుగు) | Telugu script | No translation file — English fallback |

**Why English fallback?** Languages with complex morphological systems (polysynthetic languages like Inuktitut) or specialized scripts cannot be reliably translated by general-purpose LLMs. Producing incorrect translations in such languages would be worse than presenting the interface in English. If you are a native speaker of any listed language and would like to contribute translations, please open a pull request.

## License

All modules in this repository are licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) unless stated otherwise
in an individual module's `manifest.json`.

## Contributing

1. Fork this repository
2. Create a module following the structure above
3. Ensure your `manifest.json` passes validation (`python scripts/validate.py`)
4. Submit a pull request

See [schemas/migration-guide.md](schemas/migration-guide.md) for detailed guidelines.
