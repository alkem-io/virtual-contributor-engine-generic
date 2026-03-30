import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import SystemMessage, HumanMessage


class TestInvoke:
    @pytest.mark.asyncio
    async def test_invoke_returns_response_on_success(self):
        """Test invoke returns a Response on successful LLM call."""
        mock_input = MagicMock()
        mock_input.display_name = "TestVC"
        mock_input.message = "Hello"
        mock_input.history = []
        mock_input.prompt = ["You are a helpful assistant."]
        mock_input.engine = "openai"
        mock_input.external_config = MagicMock()
        mock_input.external_config.api_key = "test-key"
        mock_input.persona_id = "test-persona"

        mock_response = MagicMock()
        mock_response.content = "Hello back!"

        with patch("ai_adapter.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.invoke.return_value = mock_response
            mock_get_model.return_value = mock_model

            import ai_adapter
            result = await ai_adapter.invoke(mock_input)

            assert result.result == "Hello back!"

    @pytest.mark.asyncio
    async def test_invoke_returns_unavailable_on_error(self):
        """Test invoke returns unavailability message on exception."""
        mock_input = MagicMock()
        mock_input.display_name = "TestVC"
        mock_input.message = "Hello"
        mock_input.history = []
        mock_input.prompt = None
        mock_input.engine = "openai"
        mock_input.external_config = MagicMock()
        mock_input.external_config.api_key = "test-key"

        with patch("ai_adapter.get_model") as mock_get_model:
            mock_get_model.side_effect = Exception("LLM error")

            import ai_adapter
            result = await ai_adapter.invoke(mock_input)

            assert "unavailable" in result.result.lower()

    @pytest.mark.asyncio
    async def test_invoke_with_history_rephrases_question(self):
        """Test that history triggers question rephrasing via condenser."""
        mock_input = MagicMock()
        mock_input.display_name = "TestVC"
        mock_input.message = "born?"
        mock_input.prompt = None
        mock_input.__contains__ = lambda self, key: key == "prompt"
        mock_input.engine = "openai"
        mock_input.external_config = MagicMock()
        mock_input.external_config.api_key = "test-key"

        # history_as_text expects objects with .role and .content (string)
        entry1 = MagicMock()
        entry1.role = "user"
        entry1.content = "who is Maxima?"
        entry2 = MagicMock()
        entry2.role = "assistant"
        entry2.content = "She is the Queen."
        entry3 = MagicMock()
        entry3.role = "user"
        entry3.content = "born?"
        mock_input.history = [entry1, entry2, entry3]

        condenser_response = MagicMock()
        condenser_response.content = "When was Queen Maxima born?"

        final_response = MagicMock()
        final_response.content = "She was born in 1971."

        with patch("ai_adapter.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.invoke.return_value = final_response

            mock_chain = MagicMock()
            mock_chain.invoke.return_value = condenser_response

            with patch("ai_adapter.ChatPromptTemplate") as mock_template_cls:
                mock_prompt = MagicMock()
                mock_prompt.__or__ = MagicMock(return_value=mock_chain)
                mock_template_cls.from_messages.return_value = mock_prompt

                mock_get_model.return_value = mock_model

                import ai_adapter
                result = await ai_adapter.invoke(mock_input)

                assert result.result == "She was born in 1971."
                mock_chain.invoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_invoke_with_prompt_adds_system_messages(self):
        """Test that input.prompt values are added as SystemMessages."""
        mock_input = MagicMock()
        mock_input.display_name = "TestVC"
        mock_input.message = "Hello"
        mock_input.history = []
        mock_input.prompt = ["Be helpful.", "Be concise."]
        mock_input.__contains__ = lambda self, key: key == "prompt"
        mock_input.engine = "openai"
        mock_input.external_config = MagicMock()
        mock_input.external_config.api_key = "test-key"

        mock_response = MagicMock()
        mock_response.content = "Hi!"

        with patch("ai_adapter.get_model") as mock_get_model:
            mock_model = MagicMock()
            mock_model.invoke.return_value = mock_response
            mock_get_model.return_value = mock_model

            import ai_adapter
            result = await ai_adapter.invoke(mock_input)

            assert result.result == "Hi!"
            # Verify model was invoked with system messages + human message
            call_args = mock_model.invoke.call_args[0][0]
            assert isinstance(call_args[0], SystemMessage)
            assert call_args[0].content == "Be helpful."
            assert isinstance(call_args[1], SystemMessage)
            assert call_args[1].content == "Be concise."
            assert isinstance(call_args[2], HumanMessage)
            assert call_args[2].content == "Hello"
