# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.4.x   | ✅ Current          |
| < 0.4   | ❌ Not supported    |

## Reporting a Vulnerability

If you discover a security vulnerability in `doppler-colab`, **please do not open a public issue.**

Instead, report it privately via the following:

- **GitHub Security Advisories**: [Report a vulnerability](https://github.com/jhaisley/doppler-colab/security/advisories/new)


Please include:

- A description of the vulnerability
- Steps to reproduce
- The potential impact
- Any suggested fix (if applicable)

You should receive an initial response within **48 hours**. Once the issue is confirmed, a fix will be prioritized and released as a patch version.

## Security Design

`doppler-colab` handles sensitive credentials and is designed with the following principles:

### Token Handling

- **Service Tokens only** — The package rejects Personal Tokens, CLI Tokens, and any non-`dp.st.*` token types at load time.
- **No token logging** — Tokens are never printed, logged, or included in confirmation output.
- **Sanitized tracebacks** — All exceptions re-raise with `from None` to strip `httpx` request objects that contain `Authorization` headers, preventing token leakage in notebook output cells.

### Secret Handling

- **No secret logging** — Secret values are never printed. Output is limited to a count and project name.
- **Doppler metadata filtered** — Internal keys (`DOPPLER_PROJECT`, `DOPPLER_CONFIG`, `DOPPLER_ENVIRONMENT`) are excluded from `os.environ` injection.

### Network

- **HTTPS only** — All API communication uses HTTPS to `api.doppler.com`.
- **10-second timeouts** — Requests enforce timeouts to prevent indefinite hangs in notebook kernels.
- **No local storage** — Secrets are injected directly into `os.environ` and are never written to disk.

## Dependency Policy

`doppler-colab` has a single runtime dependency:

| Dependency | Purpose              | Pinned        |
|------------|----------------------|---------------|
| `httpx`    | HTTP client for API  | `>=0.24`      |

Dependencies are reviewed for known vulnerabilities before each release.
