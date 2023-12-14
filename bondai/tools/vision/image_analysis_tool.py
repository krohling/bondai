import base64
from pydantic import BaseModel
from typing import Dict, Optional
from bondai.tools import Tool
from bondai.models.openai.openai_wrapper import get_completion
from bondai.models.openai.openai_connection_params import GPT_4_CONNECTION_PARAMS

TOOL_NAME = "image_analysis"
TOOL_DESCRIPTION = "This tool analyzes the contents of an image. Provide either an image URL or a base64 encoded image as well as a description of the analysis you would like to perform on the image."


class Parameters(BaseModel):
    analysis_description: str
    image_url: Optional[str] = None
    image_file_path: Optional[str] = None


class ImageAnalysisTool(Tool):
    def __init__(self, max_tokens=300):
        super(ImageAnalysisTool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, Parameters)
        self._max_tokens = max_tokens

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _analyze_image(self, image_data, analysis_description):
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": analysis_description},
                    {"type": "image_url", "image_url": {"url": image_data}},
                ],
            }
        ]

        response, _ = get_completion(
            messages=messages,
            model="gpt-4-vision-preview",
            connection_params=GPT_4_CONNECTION_PARAMS,
            max_tokens=self._max_tokens,
        )

        return response

    def run(
        self,
        analysis_description: str,
        image_url: str = None,
        image_file_path: str = None,
    ) -> str:
        if image_url is not None:
            return self._analyze_image(image_url, analysis_description)
        elif image_file_path is not None:
            base64_image = self._encode_image(image_file_path)
            return self._analyze_image(
                f"data:image/jpeg;base64,{base64_image}", analysis_description
            )
        else:
            raise Exception(
                "Either image_url or image_file_path is required. Neither were provided."
            )
