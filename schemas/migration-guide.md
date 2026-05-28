# Migration Guide: Module Manifest v2 → v3

This guide describes the changes from manifest schema v2.0.0 to v3.0.0
and how to migrate existing modules.

## Schema Changes

### New Fields (v3.0.0)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `compatibility` | `object` | No | Danwa version compatibility constraints |
| `compatibility.danwa_min_version` | `string \| null` | No | Minimum compatible Danwa version (semver) |
| `compatibility.danwa_max_version` | `string \| null` | No | Maximum compatible Danwa version (semver) |
| `repository` | `object` | No | Source repository reference |
| `repository.type` | `string` | No | Always `"github"` |
| `repository.url` | `string` | No | Repository URL |
| `repository.ref` | `string` | No | Git ref (tag/branch/commit) |

### Updated Fields

| Field | Change |
|-------|--------|
| `schema_version` | Accepts `"3.0.0"` (in addition to `"1.0.0"`, `"2.0.0"`) |
| `module_id` | Pattern relaxed: no longer requires `danwa-` prefix |
| `type` | New enum values: `prompt-variant`, `prompt-modifier`, `kitsune-assistant` |
| `category` | New enum values: `prompt-modifiers`, `kitsune`, `translations` |
| `dependencies` | Semver pattern relaxed to support `^` and `~` prefixes |

### Removed Fields

None — all v2 fields remain valid in v3.

## Migration Steps

### 1. Update `schema_version`

```json
{
  "schema_version": "3.0.0"
}
```

### 2. Add `compatibility` block

```json
{
  "compatibility": {
    "danwa_min_version": "2.1.0",
    "danwa_max_version": null
  }
}
```

### 3. Add `repository` block

```json
{
  "repository": {
    "type": "github",
    "url": "https://github.com/asb-42/danwa-modules",
    "ref": "v1.0.0"
  }
}
```

### 4. Recalculate checksums

After any manifest changes, recalculate the SHA-256 checksum of the profile file:

```bash
sha256sum profile.yaml
```

Update the `checksum` field with the new hash.

### 5. Verify

Run the validation script:

```bash
python scripts/validate.py
```

## New Module Types

### `prompt-variant`
Argumentation pattern prompts (e.g., Kantian, Dialectic, Steiner).
Previously mapped to `argumentation-pattern`.

### `prompt-modifier`
Output formatting modifiers (e.g., text-only for TTS).
New type in v3.

### `kitsune-assistant`
System prompts for the Danwa Kitsune assistant.
New type in v3.

## Directory Structure

Modules are organized by category directory:

```
danwa-modules/
├── agent-argumentation-patterns/   → type: prompt-variant
├── agent-bundles/                  → type: bundle
├── agent-cores/                    → type: agent-persona or role-type
├── agent-prompt-modifiers/         → type: prompt-modifier
├── agent-tone-profiles/            → type: tone-profile
├── kitsune-assistant/              → type: kitsune-assistant
├── llm-profiles/                   → type: llm-profile
├── ui-translations/                → type: language-pack
└── workflows/                      → type: workflow-template
```

## Creating a New Module

1. Choose the appropriate category directory
2. Create a subdirectory with a descriptive name (lowercase, hyphens)
3. Add your profile file (`profile.yaml`, `profile.json`, or `profile.md`)
4. Create `manifest.json` following the v3.0.0 schema
5. Run `python scripts/validate.py` to verify
6. Submit a pull request

### Example manifest.json

```json
{
  "schema_version": "3.0.0",
  "module_id": "my-custom-agent",
  "name": {
    "en": "My Custom Agent",
    "de": "Mein eigener Agent"
  },
  "description": {
    "en": "A custom agent persona for specialized debates."
  },
  "version": "1.0.0",
  "type": "agent-persona",
  "category": "agents",
  "author": {
    "name": "Your Name"
  },
  "license": "CC-BY-4.0",
  "tags": ["custom", "specialized"],
  "language": "en",
  "profile_file": "profile.md",
  "profile_format": "markdown",
  "compatibility": {
    "danwa_min_version": "2.1.0",
    "danwa_max_version": null
  },
  "repository": {
    "type": "github",
    "url": "https://github.com/asb-42/danwa-modules",
    "ref": "v1.0.0"
  }
}
```
