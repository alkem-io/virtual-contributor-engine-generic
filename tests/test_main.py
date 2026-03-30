import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestMainSetup:
    def test_engine_registers_handler(self):
        """Test that the engine registers the on_request handler."""
        mock_engine_instance = MagicMock()
        mock_engine_class = MagicMock(return_value=mock_engine_instance)

        mock_module = MagicMock()
        mock_module.AlkemioVirtualContributorEngine = mock_engine_class
        mock_module.Input = MagicMock()
        mock_module.Response = MagicMock()
        mock_module.setup_logger = MagicMock(return_value=MagicMock())

        with patch.dict(
            sys.modules,
            {"alkemio_virtual_contributor_engine": mock_module}
        ), patch("asyncio.run"):
            import importlib
            import main
            importlib.reload(main)

            # reload may trigger additional calls; verify at least one
            assert mock_engine_instance.register_handler.call_count >= 1
            # Verify the handler argument is a callable
            args = mock_engine_instance.register_handler.call_args
            assert callable(args[0][0])


class TestOnRequest:
    @pytest.mark.asyncio
    async def test_on_request_calls_ai_adapter_and_returns_result(self):
        """Test that on_request delegates to ai_adapter.invoke."""
        mock_input = MagicMock()
        mock_input.persona_id = "test-persona"
        mock_input.display_name = "TestVC"
        mock_input.model_dump.return_value = {"test": "data"}

        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"result": "Hello!"}

        mock_engine_instance = MagicMock()
        mock_engine_class = MagicMock(return_value=mock_engine_instance)

        mock_module = MagicMock()
        mock_module.AlkemioVirtualContributorEngine = mock_engine_class
        mock_module.Input = MagicMock()
        mock_module.Response = MagicMock()
        mock_module.setup_logger = MagicMock(return_value=MagicMock())

        with patch.dict(
            sys.modules,
            {"alkemio_virtual_contributor_engine": mock_module}
        ), patch("asyncio.run"), \
                patch(
                    "ai_adapter.invoke", new_callable=AsyncMock
                ) as mock_invoke:
            mock_invoke.return_value = mock_response

            import importlib
            import main
            importlib.reload(main)

            result = await main.on_request(mock_input)

            mock_invoke.assert_called_once_with(mock_input)
            assert result == mock_response
