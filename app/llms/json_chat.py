# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json
from typing import List

from knowledge_manager import KnowledgeManager
from llms.base_chat import HaivenBaseChat
from llms.clients import (
    ChatClient,
    HaivenAIMessage,
    HaivenHumanMessage,
)
from llms.chat_events import (
    ChatEvent,
    ContentEvent,
    ChatEventFormatter,
    create_content_event,
    create_metadata_event,
    create_token_usage_event,
    create_error_event,
)


class JSONChat(HaivenBaseChat):
    def __init__(
        self,
        chat_client: ChatClient,
        knowledge_manager: KnowledgeManager,
        contexts: List[str] = None,
        user_context: str = None,
    ):
        super().__init__(chat_client, knowledge_manager, contexts, user_context)

    def stream_from_model(self, new_message):
        """Stream raw events from the model"""
        try:
            self.memory.append(HaivenHumanMessage(content=new_message))
            stream = self.chat_client.stream(self.memory)

            for chunk in stream:
                event = self._convert_chunk_to_event(chunk)
                if event:
                    yield event

        except Exception as error:
            error_msg = (
                str(error).strip() or "Error while the model was processing the input"
            )
            print(f"[ERROR]: {error_msg}")
            yield create_error_event(error_msg)

    def run(self, message: str):
        """Run JSON chat with unified event system"""

        def create_data_chunk(chunk):
            message = json.dumps({"data": chunk})
            return f"{message}\n\n"

        try:
            for event in self.stream_from_model(message):
                if isinstance(event, ContentEvent):
                    # Update memory for content events
                    if not hasattr(self, "_first_chunk"):
                        self.memory.append(HaivenAIMessage(content=""))
                        self._first_chunk = True
                    self.memory[-1].content += event.content

                # Format event for JSON chat - all formatting handled by ChatEventFormatter
                formatted_event = ChatEventFormatter.format_for_json(event)
                yield formatted_event

        except Exception as error:
            error_msg = (
                str(error).strip() or "Error while the model was processing the input"
            )
            print(f"[ERROR]: {error_msg}")
            error_event = create_error_event(error_msg)
            yield ChatEventFormatter.format_for_json(error_event) + "\n\n"

    def _convert_chunk_to_event(self, chunk) -> ChatEvent:
        """Convert raw chunk from chat client to standardized event"""
        if "content" in chunk:
            content = chunk.get("content", "")
            # Skip empty content chunks to avoid invalid JSON
            if content.strip():
                return create_content_event(content)
        elif "metadata" in chunk:
            metadata = chunk["metadata"]
            citations = (
                metadata.get("citations", []) if isinstance(metadata, dict) else []
            )
            return create_metadata_event(citations=citations, metadata=metadata)
        elif "usage" in chunk:
            usage_data = chunk["usage"]
            if isinstance(usage_data, dict):
                return create_token_usage_event(
                    prompt_tokens=usage_data.get("prompt_tokens", 0),
                    completion_tokens=usage_data.get("completion_tokens", 0),
                    total_tokens=usage_data.get("total_tokens", 0),
                    model=usage_data.get("model", "unknown"),
                )
        elif isinstance(chunk, str):
            # Handle pre-formatted JSON strings from mocks
            if chunk.startswith('{"data":') and chunk.endswith("}"):
                return create_content_event(chunk)
            else:
                # Skip empty string chunks to avoid invalid JSON
                if chunk.strip():
                    return create_content_event(chunk)
        return None
