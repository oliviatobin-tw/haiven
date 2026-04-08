# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import io

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image

from api.api_base import streaming_headers, streaming_media_type
from llms.image_description_service import ImageDescriptionService
from logger import HaivenLogger


class ApiImage:
    def __init__(self, app: FastAPI, image_service: ImageDescriptionService):
        @app.post("/api/prompt/image")
        async def describe_image(prompt: str = Form(...), file: UploadFile = File(...)):
            try:

                def chat_with_yield(image, prompt):
                    for chunk in image_service.prompt_with_image(image, prompt):
                        yield chunk

                contents = await file.read()
                image = Image.open(io.BytesIO(contents))

                return StreamingResponse(
                    chat_with_yield(image, prompt),
                    media_type=streaming_media_type(),
                    headers=streaming_headers(None),
                )
            except Exception as error:
                HaivenLogger.get().error(str(error))
                raise HTTPException(
                    status_code=500, detail=f"Server error: {str(error)}"
                )
