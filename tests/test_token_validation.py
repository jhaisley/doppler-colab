"""Tests for _validate_token(): prefix enforcement and /v3/me access level checks."""

import warnings

import httpx
import pytest
import respx

from doppler_colab import _DEFAULT_API_BASE, _validate_token

ME_URL = f'{_DEFAULT_API_BASE}/v3/me'


class TestTokenPrefix:
    """Service token prefix validation."""

    def test_rejects_personal_token(self):
        with pytest.raises(ValueError, match="starts with 'dp.st.'"):
            _validate_token('dp.pt.sometoken', _DEFAULT_API_BASE)

    def test_rejects_cli_token(self):
        with pytest.raises(ValueError, match='Service Token'):
            _validate_token('dp.ct.sometoken', _DEFAULT_API_BASE)

    def test_rejects_arbitrary_string(self):
        with pytest.raises(ValueError):
            _validate_token('not-a-doppler-token', _DEFAULT_API_BASE)

    def test_rejects_empty_string(self):
        with pytest.raises(ValueError):
            _validate_token('', _DEFAULT_API_BASE)

    def test_accepts_valid_service_token_prefix(self):
        with respx.mock:
            respx.get(ME_URL).mock(return_value=httpx.Response(200, json={'access': 'read'}))
            # Should not raise
            _validate_token('dp.st.dev.VALIDTOKEN', _DEFAULT_API_BASE)


class TestAccessLevelCheck:
    """/v3/me access level checking."""

    @respx.mock
    def test_readonly_token_no_warning(self, valid_token):
        respx.get(ME_URL).mock(return_value=httpx.Response(200, json={'access': 'read'}))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            _validate_token(valid_token, _DEFAULT_API_BASE)
            security_warnings = [x for x in w if 'write' in str(x.message).lower()]
            assert len(security_warnings) == 0

    @respx.mock
    def test_readwrite_token_emits_warning(self, valid_token):
        respx.get(ME_URL).mock(return_value=httpx.Response(200, json={'access': 'read/write'}))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            _validate_token(valid_token, _DEFAULT_API_BASE)
            security_warnings = [x for x in w if 'write' in str(x.message).lower()]
            assert len(security_warnings) == 1
            assert 'read-only' in str(security_warnings[0].message).lower()

    @respx.mock
    def test_missing_access_field_emits_warning(self, valid_token):
        """If the response doesn't have an 'access' field, warn (treat as non-read)."""
        respx.get(ME_URL).mock(return_value=httpx.Response(200, json={}))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            _validate_token(valid_token, _DEFAULT_API_BASE)
            security_warnings = [x for x in w if 'write' in str(x.message).lower()]
            assert len(security_warnings) == 1


class TestAuthFailures:
    """/v3/me should fail fast on auth errors."""

    @respx.mock
    def test_401_raises_runtime_error(self, valid_token):
        respx.get(ME_URL).mock(return_value=httpx.Response(401, json={'error': 'unauthorized'}))
        with pytest.raises(RuntimeError, match='HTTP 401'):
            _validate_token(valid_token, _DEFAULT_API_BASE)

    @respx.mock
    def test_403_raises_runtime_error(self, valid_token):
        respx.get(ME_URL).mock(return_value=httpx.Response(403, json={'error': 'forbidden'}))
        with pytest.raises(RuntimeError, match='HTTP 403'):
            _validate_token(valid_token, _DEFAULT_API_BASE)

    @respx.mock
    def test_auth_error_does_not_leak_token(self, valid_token):
        respx.get(ME_URL).mock(return_value=httpx.Response(401, json={'error': 'unauthorized'}))
        with pytest.raises(RuntimeError) as exc_info:
            _validate_token(valid_token, _DEFAULT_API_BASE)
        assert valid_token not in str(exc_info.value)
        assert exc_info.value.__cause__ is None


class TestNetworkFailures:
    """Network errors should warn but not block secret fetching."""

    @respx.mock
    def test_500_warns_and_continues(self, valid_token):
        respx.get(ME_URL).mock(return_value=httpx.Response(500, text='Internal Server Error'))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            _validate_token(valid_token, _DEFAULT_API_BASE)  # Should not raise
            assert any('HTTP 500' in str(x.message) for x in w)

    @respx.mock
    def test_connection_error_warns_and_continues(self, valid_token):
        respx.get(ME_URL).mock(side_effect=httpx.ConnectError('connection refused'))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            _validate_token(valid_token, _DEFAULT_API_BASE)  # Should not raise
            assert any('could not reach' in str(x.message).lower() for x in w)


class TestCustomApiBase:
    """Validate that custom api_base is used for /v3/me."""

    @respx.mock
    def test_uses_custom_base_url(self, valid_token):
        custom_base = 'https://doppler.internal.corp'
        route = respx.get(f'{custom_base}/v3/me').mock(return_value=httpx.Response(200, json={'access': 'read'}))
        _validate_token(valid_token, custom_base)
        assert route.called
