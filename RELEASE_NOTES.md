# doppler-colab v0.4.0

> **Major Release** — `doppler-env` has been renamed and rebuilt from the ground up as `doppler-colab`, purpose-built for Google Colab notebooks.

## ⚡ What's New

### Native Colab Integration

Secrets are now discovered automatically from Colab's built-in 🔑 Secrets panel via `google.colab.userdata` — no CLI installation, no `.env` files. Just add your Doppler Service Token as `DOPPLER_TOKEN` in the Colab sidebar and go.

### Two Ways to Load

```python
# Python API
import doppler_colab
doppler_colab.load()

# Or use the cell magic
import doppler_colab
%doppler_load
```

### Configurable API Base

Doppler Enterprise (self-hosted) users can now pass a custom API endpoint:

```python
doppler_colab.load(api_base="https://doppler.internal.corp")
```

## 🔒 Security

- **Token enforcement** — Only scoped Service Tokens (`dp.st.*`) are accepted. Personal tokens, CLI tokens, and other types are rejected with a clear error.
- **Silent payloads** — Secret values and tokens are never printed. Output is limited to a safe confirmation: `✅ Successfully injected [NUM] secrets from Doppler [Project: my-project] into the environment.`
- **Sanitized tracebacks** — API errors strip authentication headers before re-raising, preventing token leakage in notebook output cells.

## 🔧 Breaking Changes

- **Package renamed**: `doppler-env` → `doppler-colab`. Update your `pip install` and imports.
- **CLI no longer required**: The Doppler CLI dependency and `.pth` path hook injection have been removed entirely.
- **Service Tokens only**: Personal and CLI tokens are no longer supported. Generate a Service Token in your Doppler dashboard.
- **Python ≥ 3.10**: Minimum Python version bumped from 3.6 to 3.10 (matches Colab's runtime).

## 📋 Full Changelog

- Removed legacy `.pth` background-boot injection mechanics
- Added native Google Colab `userdata` keychain integration
- Dropped `urllib` and `python-dotenv` in favor of `httpx`
- Introduced `%doppler_load` IPython cell magic
- Filtered Doppler metadata keys (`DOPPLER_PROJECT`, `DOPPLER_CONFIG`, `DOPPLER_ENVIRONMENT`) from injection and count
- Added 10-second request timeouts to prevent kernel hangs
- Added `__version__` and `__all__` module exports
- Added `pytest` test suite with 38 tests covering token discovery, validation, API fetching, injection, and security

## Installation

```
pip install doppler-colab
```

## Setup

1. Generate a **Service Token** in your [Doppler dashboard](https://dashboard.doppler.com)
2. In Colab, click 🔑 **Secrets** → add `DOPPLER_TOKEN` → paste your token (`dp.st...`)
3. Toggle **Notebook access** on

*Fallback: Outside Colab, the package reads `DOPPLER_TOKEN` from `os.environ`.*
