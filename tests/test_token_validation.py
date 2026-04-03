"""Tests for _validate_token(): Service Token prefix enforcement."""

import pytest

from doppler_colab import _validate_token


class TestTokenPrefix:
    """Service token prefix validation."""

    def test_rejects_personal_token(self):
        with pytest.raises(ValueError, match="starts with 'dp.st.'"):
            _validate_token('dp.pt.sometoken')

    def test_rejects_cli_token(self):
        with pytest.raises(ValueError, match='Service Token'):
            _validate_token('dp.ct.sometoken')

    def test_rejects_arbitrary_string(self):
        with pytest.raises(ValueError):
            _validate_token('not-a-doppler-token')

    def test_rejects_empty_string(self):
        with pytest.raises(ValueError):
            _validate_token('')

    def test_accepts_valid_service_token_prefix(self):
        _validate_token('dp.st.dev.VALIDTOKEN')

    def test_accepts_various_service_token_formats(self):
        _validate_token('dp.st.prd.SOMETOKEN')
        _validate_token('dp.st.stg.ANOTHERTOKEN')
        _validate_token('dp.st.dev.short')
