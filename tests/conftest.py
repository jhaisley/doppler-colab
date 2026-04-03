import os
import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Remove DOPPLER_* keys from os.environ before and after every test."""
    doppler_keys = [k for k in os.environ if k.startswith('DOPPLER_')]
    for k in doppler_keys:
        monkeypatch.delenv(k, raising=False)
    yield
    # monkeypatch auto-restores after the test


@pytest.fixture()
def _no_colab(monkeypatch):
    """Ensure google.colab is not importable."""
    monkeypatch.setitem(sys.modules, 'google', None)
    monkeypatch.setitem(sys.modules, 'google.colab', None)
    monkeypatch.setitem(sys.modules, 'google.colab.userdata', None)


@pytest.fixture()
def _mock_colab_userdata(monkeypatch):
    """Provide a mock google.colab.userdata module that returns a valid service token."""
    userdata = MagicMock()
    userdata.get = MagicMock(return_value='dp.st.dev.TESTTOKEN123')

    # Build the nested module hierarchy
    colab = MagicMock()
    colab.userdata = userdata

    google = MagicMock()
    google.colab = colab

    monkeypatch.setitem(sys.modules, 'google', google)
    monkeypatch.setitem(sys.modules, 'google.colab', colab)
    monkeypatch.setitem(sys.modules, 'google.colab.userdata', userdata)

    return userdata


@pytest.fixture()
def valid_token():
    """A valid Doppler service token for testing."""
    return 'dp.st.dev.TESTTOKEN123'


@pytest.fixture()
def sample_secrets():
    """A realistic Doppler API response payload."""
    return {
        'DATABASE_URL': 'postgres://localhost:5432/mydb',
        'API_KEY': 'sk-test-abc123',
        'SECRET_VALUE': 'supersecret',
        'DOPPLER_PROJECT': 'my-project',
        'DOPPLER_CONFIG': 'dev',
        'DOPPLER_ENVIRONMENT': 'development',
    }
