# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import List
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from api.api_basics import HaivenBaseApi, PromptRequestBody
from llms.chats import ChatManager
from llms.model_config import ModelConfig
from logger import HaivenLogger
from prompts.prompts import PromptList


class TitleContent(BaseModel):
    title: str = None
    content: str = None


class FollowUpPromptInput(BaseModel):
    input: str
    scenarios: List[TitleContent]


class FollowUpRequest(PromptRequestBody):
    previous_promptid: str = None
    scenarios: List[TitleContent] = []
    userContext: str = None


class ExploreRequest(PromptRequestBody):
    previous_promptid: str = None
    previous_framing: str = None
    item: str = None
    first_step_input: str = None


class ApiMultiStep(HaivenBaseApi):
    def _concat_scenarios(self, promptinput: FollowUpRequest):
        return [
            f"**{pair.title}**\n**REVISED BY ME:** {pair.content}"
            for pair in promptinput.scenarios
        ]

    def _build_follow_up_user_input(
        self, prompt_data: FollowUpRequest, output_framing: str
    ) -> str:
        # SECURITY: user input interpolated here — validate/sanitize upstream
        return f"""
                        {prompt_data.userinput}

                        {output_framing}
                        {self._concat_scenarios(prompt_data)}
                    """

    def _build_explore_user_input(
        self, prompt_data: ExploreRequest, title: str, output_framing: str
    ) -> str:
        if prompt_data.previous_promptid:
            # SECURITY: user input interpolated here — validate/sanitize upstream
            return f"""
## Specific task we're working on

{title}

{prompt_data.first_step_input}

## What I have so far
{output_framing}

I want to focus on this item:

{prompt_data.item}

## My follow-up question

{prompt_data.userinput}
                    """
        elif (
            prompt_data.previous_framing is not None
            and prompt_data.previous_framing != ""
        ):
            # For our custom-built pages that don't work with "previous prompt"
            # SECURITY: user input interpolated here — validate/sanitize upstream
            return f"""
## What we're working on
{prompt_data.previous_framing}

## Context
{prompt_data.first_step_input}

## What I have so far
I want to focus on this item:
{prompt_data.item}

## My follow-up question
{prompt_data.userinput}
                    """
        return prompt_data.userinput

    def __init__(
        self,
        app: FastAPI,
        chat_session_memory: ChatManager,
        model_key: ModelConfig,
        prompt_list: PromptList,
    ):
        super().__init__(app, chat_session_memory, model_key, prompt_list)

        # - Input for frontend: a list of promptIds - first step, multiple prompt options for next step?
        # - First step always returns cards, which are then editable in the UI
        # - Other steps always return text
        #       !! could that just be the break-out chat?!
        # 1. call POST api/prompt with the first prompt id to

        @app.post("/api/prompt/follow-up")
        def generate_follow_up(request: Request, prompt_data: FollowUpRequest):
            origin_url = request.headers.get("referer")

            try:
                stream_fn = self.stream_text_chat
                prompts = self.prompt_list

                user_input = prompt_data.userinput
                if prompt_data.previous_promptid is not None:
                    output_framing = prompts.get(
                        prompt_data.previous_promptid
                    ).metadata.get("output_framing", "")
                    user_input = self._build_follow_up_user_input(
                        prompt_data, output_framing
                    )

                rendered_prompt, _ = prompts.render_prompt(
                    prompt_choice=prompt_data.promptid,
                    user_input=user_input,
                )

                return stream_fn(
                    prompt=rendered_prompt,
                    chat_category="follow-up",
                    chat_session_key_value=prompt_data.chatSessionId,
                    document_keys=prompt_data.document,
                    user_identifier=self.get_hashed_user_id(request),
                    origin_url=origin_url,
                    contexts=prompt_data.contexts,
                    userContext=prompt_data.userContext,
                )

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.post("/api/prompt/explore")
        def kick_off_explore(request: Request, prompt_data: ExploreRequest):
            origin_url = request.headers.get("referer")

            try:
                stream_fn = self.stream_text_chat
                prompts = self.prompt_list

                title = ""
                output_framing = ""
                if prompt_data.previous_promptid:
                    prev = prompts.get(prompt_data.previous_promptid)
                    title = prev.metadata["title"]
                    output_framing = prev.metadata.get("output_framing", "")
                user_input = self._build_explore_user_input(
                    prompt_data, title, output_framing
                )

                return stream_fn(
                    prompt=user_input,
                    chat_category="explore",
                    chat_session_key_value=prompt_data.chatSessionId,
                    document_keys=prompt_data.document,
                    user_identifier=self.get_hashed_user_id(request),
                    origin_url=origin_url,
                    contexts=prompt_data.contexts,
                    userContext=prompt_data.userContext,
                )

            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )
