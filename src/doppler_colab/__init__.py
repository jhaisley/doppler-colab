"""
doppler-colab
Seamlessly inject Doppler secrets into Google Colab environments.
"""

import os
from importlib.metadata import PackageNotFoundError, version

import httpx

__all__ = ['load']

try:
    __version__ = version('doppler_colab')
except PackageNotFoundError:
    __version__ = '0.0.0'

# Doppler metadata keys that should not be injected as user secrets
_DOPPLER_METADATA_KEYS = frozenset(
    {
        'DOPPLER_PROJECT',
        'DOPPLER_CONFIG',
        'DOPPLER_ENVIRONMENT',
    }
)

_DEFAULT_API_BASE = 'https://api.doppler.com'
_REQUEST_TIMEOUT = 10.0


def load(*, api_base: str = _DEFAULT_API_BASE):
    """Fetch secrets from Doppler and inject them into os.environ.

    Args:
        api_base: Base URL for the Doppler API. Defaults to the public
            Doppler API. Override for Doppler Enterprise (self-hosted).
    """
    token = _discover_token()
    _validate_token(token)
    secrets_data = _fetch_secrets(token, api_base)
    count = _inject_secrets(secrets_data)

    project_name = secrets_data.get('DOPPLER_PROJECT', 'Unknown Project')
    print(f'✅ Successfully injected {count} secrets from Doppler [Project: {project_name}] into the environment.')


def _discover_token() -> str:
    """Discover the Doppler token from Colab userdata or os.environ."""
    token = None

    # 1. Try Colab userdata
    try:
        from google.colab import userdata

        token = userdata.get('DOPPLER_TOKEN')
    except ImportError:
        pass  # Not running in Colab
    except Exception as e:
        # Surface Colab-specific access errors clearly
        error_name = type(e).__name__
        if error_name == 'NotebookAccessError':
            raise RuntimeError(
                'DOPPLER_TOKEN exists in Colab Secrets but notebook access is not enabled. '
                "Toggle the 'Notebook access' switch on."
            ) from None
        elif error_name == 'SecretNotFoundError':
            pass  # Secret not configured in Colab; fall through to os.environ
        else:
            raise  # Unexpected error; let it propagate

    # 2. Fallback to os.environ
    if not token:
        token = os.environ.get('DOPPLER_TOKEN')

    # 3. Raise helpful exception if no token found
    if not token:
        raise RuntimeError(
            "DOPPLER_TOKEN not found. Please click the 🔑 'Secrets' icon on the left sidebar "
            "in Colab to add your Doppler Service Token, and toggle the 'Notebook access' switch on. "
            'Or, set the DOPPLER_TOKEN environment variable.'
        )

    return token


def _validate_token(token: str) -> None:
    """Validate that the token is a Service Token."""
    if not token.startswith('dp.st.'):
        raise ValueError(
            "Invalid token type. doppler-colab requires a Service Token (starts with 'dp.st.'). "
            'Personal tokens, CLI tokens, and other token types are not supported.'
        )


def _fetch_secrets(token: str, api_base: str) -> dict:
    """Fetch secrets from the Doppler API."""
    try:
        resp = httpx.get(
            f'{api_base}/v3/configs/config/secrets/download',
            auth=(token, ''),
            params={'format': 'json'},
            headers={'User-Agent': 'doppler-colab'},
            timeout=_REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f'Failed to fetch secrets from Doppler API (HTTP {e.response.status_code}).') from None
    except httpx.RequestError:
        raise RuntimeError(f'Doppler API request failed: could not connect to {api_base}') from None


def _inject_secrets(secrets_data: dict) -> int:
    """Inject secrets into os.environ, filtering out Doppler metadata keys."""
    count = 0
    for key, value in secrets_data.items():
        if key in _DOPPLER_METADATA_KEYS:
            continue
        if isinstance(value, str):
            os.environ[key] = value
            count += 1
    return count


# IPython cell magic registration
try:
    from IPython.core.magic import register_line_magic

    @register_line_magic
    def doppler_load(line):
        """IPython magic to load Doppler secrets: %doppler_load"""
        load()
except ImportError:
    pass
