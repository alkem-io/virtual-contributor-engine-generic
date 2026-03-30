import importlib
from unittest.mock import patch, MagicMock


class TestGetModel:
    def test_get_model_returns_configured_model(self):
        """Test get_model creates a ChatOpenAI instance with correct params."""
        mock_chat_openai = MagicMock()

        with patch("models.ChatOpenAI", mock_chat_openai):
            import models
            importlib.reload(models)
            models.models_map["generic-openai"] = mock_chat_openai

            result = models.get_model("generic-openai", "test-api-key")

            mock_chat_openai.assert_called_once()
            call_kwargs = mock_chat_openai.call_args[1]
            assert call_kwargs["model"] == "gpt-4o"
            assert call_kwargs["temperature"] == 0
            assert call_kwargs["max_retries"] == 2
            assert result == mock_chat_openai.return_value


class TestVerboseModels:
    def test_verbose_models_true_when_debug(self, monkeypatch):
        """Test verbose_models is True when LOG_LEVEL is DEBUG."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        import config
        importlib.reload(config)
        import models
        importlib.reload(models)
        assert models.verbose_models is True

    def test_verbose_models_false_when_info(self, monkeypatch):
        """Test verbose_models is False when LOG_LEVEL is INFO."""
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        import config
        importlib.reload(config)
        import models
        importlib.reload(models)
        assert models.verbose_models is False
