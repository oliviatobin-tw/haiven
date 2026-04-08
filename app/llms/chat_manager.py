# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List

from pydantic import BaseModel
from config_service import ConfigService
from knowledge_manager import KnowledgeManager
from llms.clients import ChatClientFactory, ModelConfig
from llms.session_memory import ServerChatSessionMemory
from llms.streaming_chat import StreamingChat
from llms.json_chat import JSONChat


class ChatOptions(BaseModel):
    category: str = None
    in_chunks: bool = False
    user_identifier: str = None


class ChatManager:
    def __init__(
        self,
        config_service: ConfigService,
        chat_session_memory: ServerChatSessionMemory,
        llm_chat_factory: ChatClientFactory,
        knowledge_manager: KnowledgeManager,
    ):
        self.config_service = config_service
        self.chat_session_memory = chat_session_memory
        self.llm_chat_factory = llm_chat_factory
        self.knowledge_manager = knowledge_manager

    def clear_session(self, session_id: str):
        self.chat_session_memory.delete_entry(session_id)

    def get_session(self, chat_session_key_value):
        return self.chat_session_memory.get_chat(chat_session_key_value)

    def streaming_chat(
        self,
        model_config: ModelConfig,
        session_id: str = None,
        options: ChatOptions = None,
        contexts: List[str] = None,
        user_context: str = None,
    ):
        def create_chat():
            return StreamingChat(
                self.llm_chat_factory.new_chat_client(model_config),
                self.knowledge_manager,
                stream_in_chunks=options.in_chunks if options else False,
                contexts=contexts,
                user_context=user_context,
            )

        return self.chat_session_memory.get_or_create_chat(
            create_chat,
            session_id,
            options.category if options else "streaming",
            options.user_identifier if options else "unknown",
        )

    def json_chat(
        self,
        model_config: ModelConfig,
        session_id: str = None,
        options: ChatOptions = None,
        contexts: List[str] = None,
        user_context: str = None,
    ):
        def create_chat():
            return JSONChat(
                self.llm_chat_factory.new_chat_client(model_config),
                self.knowledge_manager,
                contexts=contexts,
                user_context=user_context,
            )

        return self.chat_session_memory.get_or_create_chat(
            create_chat,
            session_id,
            options.category if options else "json",
            options.user_identifier if options else "unknown",
        )
