"""Tests for _fetch_secrets() and _inject_secrets()."""

import os

import httpx
import pytest
import respx

from doppler_colab import _DEFAULT_API_BASE, _DOPPLER_METADATA_KEYS, _fetch_secrets, _inject_secrets

SECRETS_URL = f'{_DEFAULT_API_BASE}/v3/configs/config/secrets/download'


class TestFetchSecrets:
    """API secret fetching."""

    @respx.mock
    def test_returns_parsed_json(self, valid_token, sample_secrets):
        respx.get(SECRETS_URL).mock(return_value=httpx.Response(200, json=sample_secrets))
        result = _fetch_secrets(valid_token, _DEFAULT_API_BASE)
        assert result == sample_secrets

    @respx.mock
    def test_sends_correct_params(self, valid_token, sample_secrets):
        route = respx.get(SECRETS_URL).mock(return_value=httpx.Response(200, json=sample_secrets))
        _fetch_secrets(valid_token, _DEFAULT_API_BASE)
        request = route.calls[0].request
        assert b'format=json' in request.url.raw_path

    @respx.mock
    def test_sends_user_agent(self, valid_token, sample_secrets):
        route = respx.get(SECRETS_URL).mock(return_value=httpx.Response(200, json=sample_secrets))
        _fetch_secrets(valid_token, _DEFAULT_API_BASE)
        request = route.calls[0].request
        assert request.headers['User-Agent'] == 'doppler-colab'

    @respx.mock
    def test_http_error_raises_runtime_error(self, valid_token):
        respx.get(SECRETS_URL).mock(return_value=httpx.Response(400, text='Bad Request'))
        with pytest.raises(RuntimeError, match='HTTP 400'):
            _fetch_secrets(valid_token, _DEFAULT_API_BASE)

    @respx.mock
    def test_http_error_does_not_leak_token(self, valid_token):
        respx.get(SECRETS_URL).mock(return_value=httpx.Response(403, text='Forbidden'))
        with pytest.raises(RuntimeError) as exc_info:
            _fetch_secrets(valid_token, _DEFAULT_API_BASE)
        assert valid_token not in str(exc_info.value)
        assert exc_info.value.__cause__ is None

    @respx.mock
    def test_network_error_raises_runtime_error(self, valid_token):
        respx.get(SECRETS_URL).mock(side_effect=httpx.ConnectError('connection refused'))
        with pytest.raises(RuntimeError, match='could not connect'):
            _fetch_secrets(valid_token, _DEFAULT_API_BASE)

    @respx.mock
    def test_network_error_does_not_leak_token(self, valid_token):
        respx.get(SECRETS_URL).mock(side_effect=httpx.ConnectError('refused'))
        with pytest.raises(RuntimeError) as exc_info:
            _fetch_secrets(valid_token, _DEFAULT_API_BASE)
        assert valid_token not in str(exc_info.value)

    @respx.mock
    def test_uses_custom_api_base(self, valid_token, sample_secrets):
        custom_base = 'https://doppler.internal.corp'
        custom_url = f'{custom_base}/v3/configs/config/secrets/download'
        route = respx.get(custom_url).mock(return_value=httpx.Response(200, json=sample_secrets))
        result = _fetch_secrets(valid_token, custom_base)
        assert route.called
        assert result == sample_secrets


class TestInjectSecrets:
    """Environment variable injection and metadata filtering."""

    def test_injects_user_secrets(self, sample_secrets, monkeypatch):
        count = _inject_secrets(sample_secrets)
        assert os.environ['DATABASE_URL'] == 'postgres://localhost:5432/mydb'
        assert os.environ['API_KEY'] == 'sk-test-abc123'
        assert os.environ['SECRET_VALUE'] == 'supersecret'
        assert count == 3

    def test_filters_doppler_metadata_keys(self, sample_secrets):
        _inject_secrets(sample_secrets)
        for key in _DOPPLER_METADATA_KEYS:
            assert key not in os.environ, f'{key} should not be injected into os.environ'

    def test_count_excludes_metadata_keys(self, sample_secrets):
        count = _inject_secrets(sample_secrets)
        # sample_secrets has 6 keys total, 3 are metadata
        assert count == 3

    def test_skips_non_string_values(self):
        secrets = {
            'VALID': 'string_value',
            'NUMERIC': 42,
            'LIST': ['a', 'b'],
            'NONE': None,
        }
        count = _inject_secrets(secrets)
        assert count == 1
        assert os.environ['VALID'] == 'string_value'

    def test_empty_payload(self):
        count = _inject_secrets({})
        assert count == 0

    def test_overwrites_existing_env_vars(self, monkeypatch):
        monkeypatch.setenv('API_KEY', 'old_value')
        _inject_secrets({'API_KEY': 'new_value'})
        assert os.environ['API_KEY'] == 'new_value'
