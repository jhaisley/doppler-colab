# Changelog

## 0.4.0 (April 03, 2026)

- **Major Pivot**: Package renamed and repurposed from `doppler-env` to `doppler-colab`, explicitly targeting ephemeral Google Colab environments.
- Removed legacy `.pth` background-boot injection mechanics.
- Added native Google Colab `userdata` keychain integrations.
- Dropped `urllib` and `python-dotenv` dependencies in favor of native JSON API parsing via `httpx`.
- Introduced `%doppler_load` IPython cell magic for cleaner notebook workflows.
- Implemented aggressive token validation enforcing Service Tokens (`dp.st.*`) and issuing pre-flight read/write permission security warnings.
- Added robust `whoami` validation distinguishing auth failures from network errors.
- Filtered Doppler metadata keys (`DOPPLER_PROJECT`, `DOPPLER_CONFIG`, `DOPPLER_ENVIRONMENT`) from secret injection and count.
- Added 10-second request timeouts to prevent notebook kernel hangs.
- Sanitized error tracebacks to prevent token leakage in notebook output.
- Added `__version__` and `__all__` exports.
- Added configurable `api_base` parameter for Doppler Enterprise support.

## 0.3.1 (December 08, 2022)

- Logging is now disabled by default and can be enabled by setting the `DOPPLER_ENV_LOGGING` environment variable.

## 0.3.0 (June 23, 2022)

- Fetch secrets from Doppler API if `DOPPLER_TOKEN` environment variable set.
- Improved error reporting.
- Check that Doppler CLI is installed.
- Add support for CLI and Personal tokens.
- Improved README.
- Fix paths issue preventing wheel build on Windows.

## 0.2.2 (May 07, 2021)

- Changed supported Python version to >= 3.6.

## 0.2.1 (May 05, 2021)

- README updates.

## 0.2.0 (May 05, 2021)

- README updates.

## 0.1.1 (May 04, 2021)

- Initial release.
