# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel

from api.api_base import HaivenBaseApi
from api.api_content import ApiContent
from api.api_image import ApiImage
from config_service import ConfigService
from disclaimer_and_guidelines import DisclaimerAndGuidelinesService
from knowledge_manager import KnowledgeManager
from llms.chats import ChatManager
from llms.image_description_service import ImageDescriptionService
from llms.model_config import ModelConfig
from logger import HaivenLogger
from prompts.inspirations import InspirationsManager
from prompts.prompts import PromptList


class PromptRequestBody(BaseModel):
    userinput: Optional[str] = None
    promptid: Optional[str] = None
    chatSessionId: Optional[str] = None
    contexts: Optional[List[str]] = None
    document: Optional[List[str]] = None
    json: bool = False
    userContext: Optional[str] = None


class IterateRequest(PromptRequestBody):
    scenarios: str
    contexts: Optional[List[str]] = None
    user_context: Optional[str] = None


class ApiBasics(HaivenBaseApi):
    @staticmethod
    def _build_iterate_prompt(userinput: str, scenarios) -> str:
        # SECURITY: user input interpolated here — validate/sanitize upstream
        return (
            f"""

                    My new request:
                    {userinput}
                    """
            + """
                    ### Output format: JSON with at least the "id" property repeated
                    Here is my current working state of the data, iterate on those objects based on that request,
                    and only return your new list of the objects in JSON format, nothing else.
                    Be sure to repeat back to me the JSON that I already have, and only update it with my new request.
                    Definitely repeat back to me the "id" property, so I can track your changes back to my original data.
                    For example, if I give you
                    [ { "title": "Paris", "id": 1 }, { "title": "London", "id": 2 } ]
                    and ask you to add information about what you know about each of these cities, then return to me
                    [ { "summary": "capital of France", "id": 1 }, { "summary": "Capital of the UK", "id": 2 } ]
"""
            + f"""
                    ### Current JSON data
                    {scenarios}
                    Please iterate on this data based on my request. Apply my request to ALL of the objects.
                """
        )

    def __init__(
        self,
        app: FastAPI,
        chat_manager: ChatManager,
        model_config: ModelConfig,
        prompts_guided: PromptList,
        knowledge_manager: KnowledgeManager,
        prompts_chat: PromptList,
        image_service: ImageDescriptionService,
        config_service: ConfigService,
        disclaimer_and_guidelines: DisclaimerAndGuidelinesService,
        inspirations_manager: InspirationsManager,
    ):
        super().__init__(app, chat_manager, model_config, prompts_guided)
        self.knowledge_manager = knowledge_manager
        self.prompts_chat = prompts_chat
        self.config_service = config_service
        self.disclaimer_and_guidelines = disclaimer_and_guidelines
        self.inspirations_manager = inspirations_manager

        ApiContent(
            app,
            knowledge_manager,
            prompts_chat,
            config_service,
            disclaimer_and_guidelines,
            inspirations_manager,
        )
        ApiImage(app, image_service)

        @app.post("/api/prompt")
        @logger.catch(reraise=True)
        def chat(request: Request, prompt_data: PromptRequestBody):
            origin_url = request.headers.get("referer")
            try:
                stream_fn = self.stream_text_chat
                if prompt_data.promptid:
                    prompts = (
                        prompts_guided
                        if prompt_data.promptid.startswith("guided-")
                        else prompts_chat
                    )
                    rendered_prompt, _ = prompts.render_prompt(
                        prompt_choice=prompt_data.promptid,
                        user_input=prompt_data.userinput,
                    )
                    if prompts.produces_json_output(prompt_data.promptid):
                        stream_fn = self.stream_json_chat
                else:
                    rendered_prompt = prompt_data.userinput

                if prompt_data.json is True:
                    stream_fn = self.stream_json_chat

                selected_model_config = self.model_config
                if prompt_data.promptid:
                    prompt_obj = prompts.get(prompt_data.promptid)
                    if prompt_obj and prompt_obj.metadata.get("grounded", True):
                        selected_model_config = ModelConfig(
                            "perplexity", "perplexity", "Perplexity"
                        )

                return stream_fn(
                    prompt=rendered_prompt,
                    model_config=selected_model_config,
                    chat_category="boba-chat",
                    chat_session_key_value=prompt_data.chatSessionId,
                    document_keys=prompt_data.document,
                    prompt_id=prompt_data.promptid,
                    user_identifier=self.get_hashed_user_id(request),
                    contexts=prompt_data.contexts,
                    userContext=prompt_data.userContext,
                    origin_url=origin_url,
                )

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.post("/api/prompt/iterate")
        def iterate(prompt_data: IterateRequest):
            try:
                if prompt_data.chatSessionId is None or prompt_data.chatSessionId == "":
                    raise HTTPException(
                        status_code=400, detail="chatSessionId is required"
                    )

                rendered_prompt = self._build_iterate_prompt(
                    prompt_data.userinput, prompt_data.scenarios
                )

                return self.stream_json_chat(
                    prompt=rendered_prompt,
                    chat_category="boba-chat",
                    chat_session_key_value=prompt_data.chatSessionId,
                    contexts=prompt_data.contexts,
                    userContext=prompt_data.user_context,
                )

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

        @app.post("/api/prompt/render")
        @logger.catch(reraise=True)
        def render_prompt(prompt_data: PromptRequestBody):
            if prompt_data.promptid:
                prompts = (
                    prompts_guided
                    if prompt_data.promptid.startswith("guided-")
                    else prompts_chat
                )
                rendered_prompt, template = prompts.render_prompt(
                    prompt_choice=prompt_data.promptid,
                    user_input=prompt_data.userinput,
                )
                return JSONResponse(
                    {"prompt": rendered_prompt, "template": template.template}
                )
            else:
                raise HTTPException(
                    status_code=500, detail="Server error: promptid is required"
                )
