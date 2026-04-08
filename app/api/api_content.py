# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import json
import re
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger

from auth import auth_util
from config_service import ConfigService
from disclaimer_and_guidelines import DisclaimerAndGuidelinesService
from embeddings.documents import KnowledgeDocument
from knowledge_manager import KnowledgeManager
from logger import HaivenLogger
from prompts.prompts import PromptList, filter_downloadable_prompts
from prompts.inspirations import InspirationsManager


class ApiContent:
    def __init__(
        self,
        app: FastAPI,
        knowledge_manager: KnowledgeManager,
        prompts_chat: PromptList,
        config_service: ConfigService,
        disclaimer_and_guidelines: DisclaimerAndGuidelinesService,
        inspirations_manager: InspirationsManager,
    ):
        @app.get("/api/models")
        @logger.catch(reraise=True)
        def get_models(request: Request):
            try:
                embeddings = config_service.load_embedding_model()
                vision = config_service.get_image_model()
                chat = config_service.get_chat_model()
                return JSONResponse(
                    {
                        "chat": {"id": chat.id, "name": chat.name},
                        "vision": {"id": vision.id, "name": vision.name},
                        "embeddings": {"id": embeddings.id, "name": embeddings.name},
                    }
                )
            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/prompts")
        @logger.catch(reraise=True)
        def get_prompts(request: Request):
            try:
                response_data = prompts_chat.get_prompts_with_follow_ups()
                return JSONResponse(response_data)
            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/disclaimer-guidelines")
        @logger.catch(reraise=True)
        def get_disclaimer_and_guidelines(request: Request):
            try:
                if not disclaimer_and_guidelines.is_enabled:
                    return JSONResponse({"enabled": False, "title": "", "content": ""})

                response_data = json.loads(
                    disclaimer_and_guidelines.fetch_disclaimer_and_guidelines()
                )
                response_data["enabled"] = True
                return JSONResponse(response_data)
            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/knowledge/snippets")
        @logger.catch(reraise=True)
        def get_knowledge_snippets(request: Request):
            try:
                all_contexts = (
                    knowledge_manager.knowledge_base_markdown.get_all_contexts()
                )
                response_data = []
                for key, context_info in all_contexts.items():
                    response_data.append(
                        {
                            "context": key,
                            "title": context_info.metadata["title"],
                            "snippets": {"context": context_info.content},
                        }
                    )
                response_data.sort(key=lambda x: x["context"])
                return JSONResponse(response_data)
            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/knowledge/documents")
        @logger.catch(reraise=True)
        def get_knowledge_documents(request: Request):
            try:
                response_data = []
                documents: List[KnowledgeDocument] = (
                    knowledge_manager.knowledge_base_documents.get_documents()
                )
                for document in documents:
                    response_data.append(
                        {
                            "key": document.key,
                            "title": document.title,
                            "description": document.description,
                            "source": document.get_source_title_link(),
                        }
                    )
                return JSONResponse(response_data)
            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/inspirations")
        @logger.catch(reraise=True)
        def get_inspirations(request: Request):
            try:
                return JSONResponse(inspirations_manager.get_inspirations())
            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/inspirations/{inspiration_id}")
        @logger.catch(reraise=True)
        def get_inspiration_by_id(request: Request, inspiration_id: str):
            try:
                inspiration = inspirations_manager.get_inspiration_by_id(
                    inspiration_id
                )
                if inspiration is None:
                    raise HTTPException(status_code=404, detail="Inspiration not found")
                return JSONResponse(inspiration)
            except HTTPException:
                raise
            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )

        @app.get("/api/download-prompt")
        @logger.catch(reraise=True)
        def download_prompt(
            request: Request, prompt_id: str = None, category: str = None
        ):
            def is_valid_param(val):
                return bool(val) and re.match(r"^[a-zA-Z0-9_-]{1,100}$", val)

            user_id = auth_util.get_hashed_user_id(request)
            source = auth_util.get_request_source(request)

            try:
                if prompt_id is not None:
                    if not is_valid_param(prompt_id):
                        raise HTTPException(status_code=400, detail="Invalid prompt_id")
                    prompt = prompts_chat.get_a_prompt_with_follow_ups(
                        prompt_id, download_prompt=True
                    )
                    if not prompt:
                        raise Exception("Prompt not found")

                    if prompt.get("download_restricted", False):
                        HaivenLogger.get().analytics(
                            "Download restricted prompt attempted",
                            {
                                "user_id": user_id,
                                "prompt_id": prompt_id,
                                "category": "Individual Prompt",
                                "source": source,
                            },
                        )
                        raise HTTPException(
                            status_code=403,
                            detail="This prompt is not available for download",
                        )

                    HaivenLogger.get().analytics(
                        "Download prompt",
                        {
                            "user_id": user_id,
                            "prompt_id": prompt_id,
                            "category": "Individual Prompt",
                            "source": source,
                        },
                    )
                    return JSONResponse([prompt])

                elif category and category.strip():
                    if not is_valid_param(category):
                        raise HTTPException(status_code=400, detail="Invalid category")

                    prompts = prompts_chat.get_prompts_with_follow_ups(
                        download_prompt=True, category=category
                    )
                    downloadable_prompts = filter_downloadable_prompts(prompts)
                    for prompt in downloadable_prompts:
                        HaivenLogger.get().analytics(
                            "Download prompt",
                            {
                                "user_id": user_id,
                                "prompt_id": prompt.get("identifier"),
                                "category": category,
                                "source": source,
                            },
                        )
                    return JSONResponse(downloadable_prompts)

                else:
                    prompts = prompts_chat.get_prompts_with_follow_ups(
                        download_prompt=True
                    )
                    downloadable_prompts = filter_downloadable_prompts(prompts)
                    for prompt in downloadable_prompts:
                        HaivenLogger.get().analytics(
                            "Download prompt",
                            {
                                "user_id": user_id,
                                "prompt_id": prompt.get("identifier"),
                                "category": "all",
                                "source": source,
                            },
                        )
                    return JSONResponse(downloadable_prompts)

            except HTTPException:
                raise
            except Exception as error:
                HaivenLogger.get().error(
                    str(error),
                    extra={
                        "ERROR": "Downloading prompts failed",
                        "user_id": user_id,
                        "prompt_id": prompt_id,
                        "category": category,
                        "source": source,
                    },
                )
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )
