"""Integration tests for the public load() function."""

import os

import httpx
import pytest
import respx

from doppler_colab import _DEFAULT_API_BASE, load

WHOAMI_URL = f'{_DEFAULT_API_BASE}/v3/auth/whoami'
SECRETS_URL = f'{_DEFAULT_API_BASE}/v3/configs/config/secrets/download'


class TestLoadEndToEnd:
    """Full load() orchestration tests."""

    @respx.mock
    def test_full_happy_path(self, _no_colab, monkeypatch, sample_secrets, whoami_readonly_response, capsys):
        monkeypatch.setenv('DOPPLER_TOKEN', 'dp.st.dev.TESTTOKEN')
        respx.get(WHOAMI_URL).mock(return_value=httpx.Response(200, json=whoami_readonly_response))
        respx.get(SECRETS_URL).mock(return_value=httpx.Response(200, json=sample_secrets))

        load()

        assert os.environ['DATABASE_URL'] == 'postgres://localhost:5432/mydb'
        assert os.environ['API_KEY'] == 'sk-test-abc123'
        # Metadata keys should NOT be in env
        assert 'DOPPLER_PROJECT' not in os.environ

        captured = capsys.readouterr()
        assert '✅' in captured.out
        assert 'my-project' in captured.out

    @respx.mock
    def test_prints_correct_secret_count(
        self, _no_colab, monkeypatch, sample_secrets, whoami_readonly_response, capsys
    ):
        monkeypatch.setenv('DOPPLER_TOKEN', 'dp.st.dev.TESTTOKEN')
        respx.get(WHOAMI_URL).mock(return_value=httpx.Response(200, json=whoami_readonly_response))
        respx.get(SECRETS_URL).mock(return_value=httpx.Response(200, json=sample_secrets))

        load()

        captured = capsys.readouterr()
        # 6 total keys - 3 metadata keys = 3 user secrets
        assert '3 secrets' in captured.out

    @respx.mock
    def test_prints_unknown_project_when_metadata_missing(
        self, _no_colab, monkeypatch, whoami_readonly_response, capsys
    ):
        monkeypatch.setenv('DOPPLER_TOKEN', 'dp.st.dev.TESTTOKEN')
        respx.get(WHOAMI_URL).mock(return_value=httpx.Response(200, json=whoami_readonly_response))
        respx.get(SECRETS_URL).mock(return_value=httpx.Response(200, json={'MY_SECRET': 'value'}))

        load()

        captured = capsys.readouterr()
        assert 'Unknown Project' in captured.out

    @respx.mock
    def test_custom_api_base(self, _no_colab, monkeypatch, sample_secrets, whoami_readonly_response):
        custom_base = 'https://doppler.internal.corp'
        monkeypatch.setenv('DOPPLER_TOKEN', 'dp.st.dev.TESTTOKEN')
        whoami_route = respx.get(f'{custom_base}/v3/auth/whoami').mock(
            return_value=httpx.Response(200, json=whoami_readonly_response)
        )
        secrets_route = respx.get(f'{custom_base}/v3/configs/config/secrets/download').mock(
            return_value=httpx.Response(200, json=sample_secrets)
        )

        load(api_base=custom_base)

        assert whoami_route.called
        assert secrets_route.called

    def test_no_token_raises(self, _no_colab):
        with pytest.raises(RuntimeError, match='DOPPLER_TOKEN not found'):
            load()

    def test_invalid_token_type_raises(self, _no_colab, monkeypatch):
        monkeypatch.setenv('DOPPLER_TOKEN', 'dp.pt.personaltoken')
        with pytest.raises(ValueError, match='Service Token'):
            load()

    @respx.mock
    def test_api_failure_raises(self, _no_colab, monkeypatch, whoami_readonly_response):
        monkeypatch.setenv('DOPPLER_TOKEN', 'dp.st.dev.TESTTOKEN')
        respx.get(WHOAMI_URL).mock(return_value=httpx.Response(200, json=whoami_readonly_response))
        respx.get(SECRETS_URL).mock(return_value=httpx.Response(500, text='Server Error'))

        with pytest.raises(RuntimeError, match='HTTP 500'):
            load()


class TestLoadSecurity:
    """Security-focused integration tests."""

    @respx.mock
    def test_token_never_in_stdout(self, _no_colab, monkeypatch, sample_secrets, whoami_readonly_response, capsys):
        token = 'dp.st.dev.SUPERSECRETTOKEN'
        monkeypatch.setenv('DOPPLER_TOKEN', token)
        respx.get(WHOAMI_URL).mock(return_value=httpx.Response(200, json=whoami_readonly_response))
        respx.get(SECRETS_URL).mock(return_value=httpx.Response(200, json=sample_secrets))

        load()

        captured = capsys.readouterr()
        assert token not in captured.out
        assert token not in captured.err

    @respx.mock
    def test_secret_values_never_in_stdout(
        self, _no_colab, monkeypatch, sample_secrets, whoami_readonly_response, capsys
    ):
        monkeypatch.setenv('DOPPLER_TOKEN', 'dp.st.dev.TESTTOKEN')
        respx.get(WHOAMI_URL).mock(return_value=httpx.Response(200, json=whoami_readonly_response))
        respx.get(SECRETS_URL).mock(return_value=httpx.Response(200, json=sample_secrets))

        load()

        captured = capsys.readouterr()
        # Only check actual user secrets, not Doppler metadata (project name is intentionally displayed)
        from doppler_colab import _DOPPLER_METADATA_KEYS

        for key, value in sample_secrets.items():
            if key in _DOPPLER_METADATA_KEYS:
                continue
            assert value not in captured.out, f'Secret value for "{key}" leaked to stdout'
