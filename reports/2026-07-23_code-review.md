# Code Review: danwa-modules

**Date:** 2026-07-23  
**Reviewer:** Principal Staff Engineer  
**Scope:** Module schemas, validation scripts, LLM profiles, ZIP builder, action templates

---

## 1. Executive Summary

danwa-modules is a content repository (YAML/JSON module manifests, no executable code in production paths). The schemas are well-designed with proper JSON Schema validation, checksum verification, and semantic versioning constraints. The most notable issues are: (1) several **LLM profiles hardcode a private IP address** (`192.168.178.200`) as the `api_base`, leaking the developer's internal network topology into a public repository; (2) the validation script has a **path traversal vulnerability** via untrusted `profile_file` values that mirrors the same bug in danwa-core's installer; and (3) the `build_zips.py` script produces ZIPs without path sanitisation, which are then consumed by the vulnerable `install_from_url` in danwa-core (the Zip Slip vector identified in that repo's review).

---

## 2. Critical & High Severity Issues (Must Fix)

### 2.1 Hardcoded Private IP in LLM Profiles — [Security/Information Disclosure]

- **Location:** Multiple `llm-profiles/*/profile.yaml` files — at least 7 profiles contain `api_base: http://192.168.178.200:1234/v1`
- **The Problem:** A private LAN IP address (`192.168.178.200`) is hardcoded in committed profile files in a public GitHub repository. This discloses the developer's internal network layout to anyone who can read the repo. While this doesn't directly enable an attack, it's an information disclosure that aids targeted attacks (an attacker who compromises the deployment now knows the internal IP of the LLM inference server).
- **The Fix:** Replace with a placeholder or environment variable reference:

```yaml
# Before:
api_base: http://192.168.178.200:1234/v1

# After:
api_base: ${DANWA_LOCAL_LLM_BASE_URL:http://localhost:1234/v1}
# Or simply:
api_base: http://localhost:1234/v1
```

If these profiles are only meant for the developer's local setup, they should be moved to a private fork or a `local-profiles/` directory excluded from the public repo.

### 2.2 Path Traversal in Validation Script — [Security]

- **Location:** `scripts/validate.py:67` — `profile_path = module_dir / profile_file`
- **The Problem:** The `profile_file` field from the manifest is joined against `module_dir` without path validation. A malicious manifest with `"profile_file": "../../../etc/passwd"` would cause the validation script to check for the existence of a file outside the module directory. While `validate.py` only checks existence and size (not content), the same pattern in danwa-core's installer (`_register_in_db`) reads and stores the file content. This is the supply-side vector for the path traversal bug identified in the danwa-core review.
- **The Fix:**

```python
def _safe_profile_path(module_dir: Path, profile_file: str) -> Path:
    """Resolve profile_file, rejecting path traversal."""
    base = module_dir.resolve()
    resolved = (base / profile_file).resolve()
    if not str(resolved).startswith(str(base) + os.sep) and resolved != base:
        raise ValueError(f"Path traversal in profile_file: '{profile_file}'")
    return resolved
```

---

## 3. Architectural & Design Improvements (Should Fix)

### 3.1 `build_zips.py` Does Not Sanitise Archive Paths — [Security/Architecture]

- **Location:** `scripts/build_zips.py:53-56` — `build_zip()`
- **The Problem:** The ZIP builder writes `arcname = f.relative_to(module_dir).as_posix()` without checking that `arcname` doesn't contain `..` segments. While `rglob("*")` typically returns safe paths, a symlink or specially-named file in the module directory could produce an `arcname` that, when extracted by the vulnerable `install_from_url` in danwa-core, writes outside the target directory. This is the supply-side complement to the Zip Slip vulnerability.
- **The Fix:** Validate arcnames before writing:

```python
def build_zip(module_dir: Path, module_id: str, releases_dir: Path) -> Path:
    zip_path = releases_dir / f"{module_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(module_dir.rglob("*")):
            if f.is_file():
                arcname = f.relative_to(module_dir).as_posix()
                # Reject path traversal in archive names
                if ".." in arcname.split("/"):
                    print(f"  WARN: Skipping path-traversal entry: {arcname}", file=sys.stderr)
                    continue
                zf.write(f, arcname)
    return zip_path
```

### 3.2 Checksum Validation Is Optional — [Architecture]

- **Location:** `schemas/module-manifest.json:175-178` and `scripts/validate.py:74-75`
- **The Problem:** The `checksum` field in the manifest schema is optional (`"pattern": "^([a-f0-9]{64})?$"` — the `?` makes it accept empty string). The validation script only verifies checksums `"if checksum and profile_file"` — i.e. an empty checksum skips verification entirely. This means a tampered module with no checksum will pass validation and install without any integrity check. For a content repository that feeds into a module installer with file-write capabilities, checksums should be mandatory.
- **The Fix:** Make `checksum` a required field in the schema for v2.0.0+ manifests, and fail validation when it's empty:

```json
"checksum": {
  "type": "string",
  "pattern": "^[a-f0-9]{64}$",
  "description": "SHA-256 of the profile file content. Required."
}
```

---

## 4. Performance & Resilience Optimizations (Nice to Have)

- **`validate.py` reads each manifest file twice:** Lines 52 and 95 both call `manifest_path.read_text()` and `json.loads()` — once in `validate_manifest()` and once in `check_uniqueness()`. For a repo with 100+ modules, this doubles the I/O. Pass the parsed manifest through the pipeline instead of re-reading.

- **`find_manifests` uses `rglob` without depth limit:** `ROOT.rglob("manifest.json")` recurses into any subdirectory. If the repo ever accumulates `node_modules/` or `.venv/` directories (from tooling), the scan will descend into them. Add a depth guard or exclude common dependency directories.

---

## 5. Clarifying Questions for the Author

1. **Are the `192.168.178.200` LLM profiles intended for public consumption?** If they're developer-local profiles, should they be in a separate `local-profiles/` directory excluded from the public repo via `.gitignore`?
2. **Should checksums be mandatory for published modules?** The current schema makes them optional, which means a supply-chain attack could publish a tampered module without any integrity check failing.
3. **What is the trust model for module ZIPs?** The `build_zips.py` output is consumed by `install_from_url` in danwa-core. Is there a signing step planned, or is checksum verification the only integrity guarantee?
