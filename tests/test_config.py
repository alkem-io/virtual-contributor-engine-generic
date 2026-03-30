import pytest


class TestEnv:
    def test_default_values(self, monkeypatch):
        """Test Env loads defaults correctly."""
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        # Re-import to test initialization
        import importlib
        import config
        importlib.reload(config)
        assert config.env.log_level == "INFO"
        assert config.env.history_length == 20

    def test_custom_history_length(self, monkeypatch):
        """Test custom HISTORY_LENGTH."""
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        monkeypatch.setenv("HISTORY_LENGTH", "50")
        import importlib
        import config
        importlib.reload(config)
        assert config.env.history_length == 50

    def test_invalid_log_level(self, monkeypatch):
        """Test assertion on invalid LOG_LEVEL."""
        monkeypatch.setenv("LOG_LEVEL", "INVALID")
        import importlib
        import config
        with pytest.raises(AssertionError):
            importlib.reload(config)
