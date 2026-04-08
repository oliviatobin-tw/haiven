# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
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


class StreamingChat(HaivenBaseChat):
    def __init__(
        self,
        chat_client: ChatClient,
        knowledge_manager: KnowledgeManager,
        stream_in_chunks: bool = False,
        contexts: List[str] = None,
        user_context: str = None,
    ):
        super().__init__(chat_client, knowledge_manager, contexts, user_context)
        self.stream_in_chunks = stream_in_chunks

    def run(self, message: str, user_query: str = None):
        """Run streaming chat with unified event system"""
        self.memory.append(HaivenHumanMessage(content=message))

        try:
            for i, chunk in enumerate(self.chat_client.stream(self.memory)):
                if i == 0:
                    if user_query:
                        self.memory[-1].content = user_query
                    self.memory.append(HaivenAIMessage(content=""))

                # Convert raw chunks to standardized events
                event = self._convert_chunk_to_event(chunk)
                if event:
                    # Format event for streaming chat
                    yield ChatEventFormatter.format_for_streaming(event)

                    # Update memory for content events
                    if isinstance(event, ContentEvent):
                        self.memory[-1].content += event.content

        except Exception as error:
            error_msg = (
                str(error).strip() or "Error while the model was processing the input"
            )
            print(f"[ERROR]: {error_msg}")
            error_event = create_error_event(error_msg)
            yield ChatEventFormatter.format_for_streaming(error_event)

    def _convert_chunk_to_event(self, chunk) -> ChatEvent:
        """Convert raw chunk from chat client to standardized event"""
        if "content" in chunk:
            return create_content_event(chunk.get("content", ""))
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
        return None

    def _build_document_context(self, knowledge_document_keys, message):
        """Retrieve context and sources for document-grounded prompting"""
        return self._similarity_search_based_on_history(message, knowledge_document_keys)

    def _build_prompt_with_context(self, user_request: str, context_for_prompt: str) -> str:
        if context_for_prompt:
            return (
                f"\n                {user_request}"
                f"\n                ---- Here is some additional CONTEXT that might be relevant to this:"
                f"\n                {context_for_prompt} "
                f"\n                -------"
                f"\n                Do not provide any advice that is outside of the CONTEXT I provided."
                f"\n                "
            )
        return user_request

    def run_with_document(
        self,
        knowledge_document_keys: List[str],
        message: str = None,
    ):
        """Run streaming chat with document context"""
        try:
            context_for_prompt, sources_markdown = self._build_document_context(
                knowledge_document_keys, message
            )
            user_request = (
                message
                or "Based on our conversation so far, what do you think is relevant to me with the CONTEXT information I gathered?"
            )
            prompt = self._build_prompt_with_context(user_request, context_for_prompt)

            for event_str in self.run(prompt, user_request):
                yield event_str, sources_markdown

            if sources_markdown:
                sources_event = create_content_event("\n\n" + sources_markdown)
                yield ChatEventFormatter.format_for_streaming(sources_event), sources_markdown

        except Exception as error:
            error_msg = str(error).strip() or "Error while the model was processing the input"
            print(f"[ERROR]: {error_msg}")
            error_event = create_error_event(error_msg)
            yield ChatEventFormatter.format_for_streaming(error_event), ""
