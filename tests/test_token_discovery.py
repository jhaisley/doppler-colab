"""Tests for _discover_token(): Colab userdata → os.environ → RuntimeError."""

import sys
from unittest.mock import MagicMock

import pytest

from doppler_colab import _discover_token


class TestColabUserdata:
    """Token discovery via google.colab.userdata."""

    def test_returns_token_from_colab_userdata(self, _mock_colab_userdata):
        token = _discover_token()
        assert token == 'dp.st.dev.TESTTOKEN123'

    def test_colab_userdata_called_with_correct_key(self, _mock_colab_userdata):
        _discover_token()
        _mock_colab_userdata.get.assert_called_once_with('DOPPLER_TOKEN')

    def test_colab_notebook_access_error_raises_clear_message(self, monkeypatch):
        """NotebookAccessError should produce a user-friendly RuntimeError."""

        class NotebookAccessError(Exception):
            pass

        userdata = MagicMock()
        userdata.get = MagicMock(side_effect=NotebookAccessError('access not enabled'))
        userdata.NotebookAccessError = NotebookAccessError

        colab = MagicMock()
        colab.userdata = userdata
        google = MagicMock()
        google.colab = colab

        monkeypatch.setitem(sys.modules, 'google', google)
        monkeypatch.setitem(sys.modules, 'google.colab', colab)
        monkeypatch.setitem(sys.modules, 'google.colab.userdata', userdata)

        with pytest.raises(RuntimeError, match='notebook access is not enabled'):
            _discover_token()

    def test_colab_secret_not_found_falls_through_to_env(self, monkeypatch):
        """SecretNotFoundError should silently fall through to os.environ."""

        class SecretNotFoundError(Exception):
            pass

        userdata = MagicMock()
        userdata.get = MagicMock(side_effect=SecretNotFoundError('not found'))
        userdata.SecretNotFoundError = SecretNotFoundError

        colab = MagicMock()
        colab.userdata = userdata
        google = MagicMock()
        google.colab = colab

        monkeypatch.setitem(sys.modules, 'google', google)
        monkeypatch.setitem(sys.modules, 'google.colab', colab)
        monkeypatch.setitem(sys.modules, 'google.colab.userdata', userdata)

        monkeypatch.setenv('DOPPLER_TOKEN', 'dp.st.dev.ENVTOKEN')
        token = _discover_token()
        assert token == 'dp.st.dev.ENVTOKEN'

    def test_unexpected_colab_error_propagates(self, monkeypatch):
        """Unknown exceptions from userdata.get should not be swallowed."""
        userdata = MagicMock()
        userdata.get = MagicMock(side_effect=ConnectionError('something weird'))

        colab = MagicMock()
        colab.userdata = userdata
        google = MagicMock()
        google.colab = colab

        monkeypatch.setitem(sys.modules, 'google', google)
        monkeypatch.setitem(sys.modules, 'google.colab', colab)
        monkeypatch.setitem(sys.modules, 'google.colab.userdata', userdata)

        with pytest.raises(ConnectionError, match='something weird'):
            _discover_token()


class TestEnvFallback:
    """Token discovery via os.environ when Colab is unavailable."""

    def test_returns_token_from_env_when_no_colab(self, _no_colab, monkeypatch):
        monkeypatch.setenv('DOPPLER_TOKEN', 'dp.st.dev.FROMENV')
        token = _discover_token()
        assert token == 'dp.st.dev.FROMENV'

    def test_env_fallback_when_colab_returns_none(self, monkeypatch):
        """If Colab userdata returns None/empty, fall through to env."""
        userdata = MagicMock()
        userdata.get = MagicMock(return_value=None)

        colab = MagicMock()
        colab.userdata = userdata
        google = MagicMock()
        google.colab = colab

        monkeypatch.setitem(sys.modules, 'google', google)
        monkeypatch.setitem(sys.modules, 'google.colab', colab)
        monkeypatch.setitem(sys.modules, 'google.colab.userdata', userdata)

        monkeypatch.setenv('DOPPLER_TOKEN', 'dp.st.dev.FALLBACK')
        token = _discover_token()
        assert token == 'dp.st.dev.FALLBACK'


class TestNoTokenFound:
    """Error when no token is available anywhere."""

    def test_raises_runtime_error_with_helpful_message(self, _no_colab):
        with pytest.raises(RuntimeError, match='DOPPLER_TOKEN not found'):
            _discover_token()

    def test_error_mentions_colab_secrets(self, _no_colab):
        with pytest.raises(RuntimeError, match='Secrets'):
            _discover_token()
