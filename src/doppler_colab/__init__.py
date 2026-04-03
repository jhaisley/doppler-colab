"""
doppler-colab
Seamlessly inject Doppler secrets into Google Colab environments.
"""

import os
import httpx
import warnings

def load():
    token = None
    
    # 1. Try Colab userdata
    try:
        from google.colab import userdata
        token = userdata.get('DOPPLER_TOKEN')
    except (ImportError, Exception):
        pass

    # 2. Fallback to os.environ
    if not token:
        token = os.environ.get('DOPPLER_TOKEN')

    # 3. Raise helpful exception if no token
    if not token:
        raise RuntimeError("DOPPLER_TOKEN not found. Please click the 🔑 'Secrets' icon on the left sidebar in Colab to add your Doppler Service Token, and toggle the 'Notebook access' switch on. Or, set the DOPPLER_TOKEN environment variable.")

    # 4. Enforce Service Token
    if not token.startswith('dp.st.'):
        raise ValueError("Invalid token type. doppler-colab requires a Service Token (starts with 'dp.st.').")

    # 5. Check Token Capabilities for write access warnings
    try:
        whoami_resp = httpx.get(
            'https://api.doppler.com/v3/auth/whoami',
            auth=(token, ''),
            headers={"User-Agent": "doppler-colab"}
        )
        whoami_resp.raise_for_status()
        capabilities = whoami_resp.json().get('token', {}).get('capabilities', [])
        if 'write' in capabilities:
            warnings.warn("Security Warning: Your Doppler Service Token has 'write' access. In ephemeral environments like Colab, it is highly recommended to use a 'read-only' Service Token.")
    except httpx.HTTPError:
        pass # Ignore failure and proceed to fetch secrets

    # 6. Fetch Secrets
    try:
        resp = httpx.get(
            'https://api.doppler.com/v3/configs/config/secrets/download',
            auth=(token, ''),
            params={'format': 'json'},
            headers={"User-Agent": "doppler-colab"}
        )
        resp.raise_for_status()
        secrets_data = resp.json()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Failed to fetch secrets from Doppler API: {e.response.text}") from e
    except httpx.RequestError as e:
        raise RuntimeError(f"Doppler API request failed: {e}") from e

    # 7. Inject into os.environ
    count = 0
    for key, value in secrets_data.items():
        if isinstance(value, str):
            os.environ[key] = value
            count += 1
            
    # 8. Print safe confirmation
    project_name = secrets_data.get('DOPPLER_PROJECT', 'Unknown Project')
    print(f"✅ Successfully injected {count} secrets from Doppler [Project: {project_name}] into the environment.")

# IPython cell magic registration
try:
    from IPython.core.magic import register_line_magic
    
    @register_line_magic
    def doppler_load(line):
        load()
except ImportError:
    pass
