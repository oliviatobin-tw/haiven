# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List

from knowledge_manager import KnowledgeManager
from embeddings.documents import DocumentsUtils
from llms.clients import (
    ChatClient,
    HaivenHumanMessage,
    HaivenSystemMessage,
)
from logger import HaivenLogger


class HaivenBaseChat:
    def __init__(
        self,
        chat_client: ChatClient,
        knowledge_manager: KnowledgeManager,
        contexts: List[str] = None,
        user_context: str = None,
    ):
        self.knowledge_manager = knowledge_manager
        self.system = knowledge_manager.get_system_message()
        aggregatedContext = (
            knowledge_manager.knowledge_base_markdown.aggregate_all_contexts(
                contexts, user_context
            )
        )
        if aggregatedContext:
            self.system += (
                "\n\nMultiple contexts will be given. Consider "
                + "all contexts when responding to the given prompt "
                + aggregatedContext
            )

        self.memory = [HaivenSystemMessage(content=self.system)]
        self.chat_client = chat_client

    def log_run(self, extra={}):
        class_name = self.__class__.__name__
        extra_info = {
            "chat_type": class_name,
            "numberOfMessages": len(self.memory),
        }
        extra_info.update(extra)

        HaivenLogger.get().analytics("Sending message", extra_info)

    def memory_as_text(self):
        return "\n".join([str(message) for message in self.memory])

    def _similarity_query(self, message):
        if len(self.memory) == 1:
            return message

        if len(self.memory) > 5:
            conversation = "\n".join(
                [message.content for message in (self.memory[:2] + self.memory[-4:])]
            )
        else:
            conversation = "\n".join([message.content for message in self.memory])

        system_message = f"""You are a helpful assistant.
        Your task is create a single search query to find relevant information, based on the conversation and the current user message.
        Rules:
        - Search query should find relevant information for the current user message only.
        - Include all important key words and phrases in query that would help to search for relevant information.
        - If the current user message does not need to search for additional information, return NONE.
        - Only return the single standalone search query or NONE. No explanations needed.

        Conversation:
        {conversation}
        """
        prompt = [HaivenSystemMessage(content=system_message)]
        prompt.append(
            HaivenHumanMessage(content=f"Current user message: {message} \n Query:")
        )

        stream = self.chat_client.stream(prompt)
        query = ""
        for chunk in stream:
            query += chunk.get("content", "")

        if "none" in query.lower():
            return None
        elif "query:" in query.lower():
            return query.split("query:")[1].strip()
        else:
            return query

    def _similarity_search_based_on_history(self, message, knowledge_document_keys):
        similarity_query = self._similarity_query(message)
        print("Similarity Query:", similarity_query)
        if similarity_query is None:
            return None, None

        if knowledge_document_keys:
            context_documents = self.knowledge_manager.knowledge_base_documents.similarity_search_on_multiple_documents(
                query=similarity_query,
                document_keys=knowledge_document_keys,
            )
        else:
            return None, None

        context_for_prompt = "\n---".join(
            [f"{document.page_content}" for document in context_documents]
        )
        de_duplicated_sources = DocumentsUtils.get_unique_sources(context_documents)
        sources_markdown = (
            "**These articles might be relevant:**\n"
            + "\n".join(
                [
                    f"- {DocumentsUtils.get_search_result_item(source.metadata)}"
                    for source in de_duplicated_sources
                ]
            )
            + "\n\n"
        )

        return context_for_prompt, sources_markdown
