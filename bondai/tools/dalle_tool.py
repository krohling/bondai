import requests
import openai
from pydantic import BaseModel
from typing import Dict
from bondai.tools import Tool
from bondai.models.openai import OpenAIConnectionParams, DefaultOpenAIConnectionParams

IMAGE_SIZE = "1024x1024"
TOOL_NAME = "text_to_image_tool"
TOOL_DESCRIPTION = (
    "This tool takes in a description and generates an image based on that description. "
    "It then saves the image to the specified filename.\n"
    "\nParameters:\n"
    "- description (required): The text description based on which the image will be generated.\n"
    "- filename (required): The name of the file where the generated image will be saved."
)


class Parameters(BaseModel):
    description: str
    filename: str
    thought: str


class DalleTool(Tool):
    def __init__(self, connection_params: OpenAIConnectionParams | None = None):
        super().__init__(TOOL_NAME, TOOL_DESCRIPTION, parameters=Parameters)
        self._connection_params = (
            connection_params
            if connection_params
            else DefaultOpenAIConnectionParams.dalle_connection_params
        )
        if not self._connection_params:
            raise Exception("Connection parameters not set for DalleTool.")

    def run(self, arguments: Dict) -> str:
        description = arguments.get("description")
        filename = arguments.get("filename")

        if description is None:
            raise Exception("description is required.")
        if filename is None:
            raise Exception("filename is required.")

        params = {"prompt": description, "n": 1, "size": IMAGE_SIZE}

        # Use the OpenAI API to generate an image based on the description
        response = openai.Image.create(**params, **self._connection_params.to_dict())

        # Get the image URL from the response
        image_url = response["data"][0]["url"]

        # Download the image from the URL and save it to the specified filename
        image_content = requests.get(image_url).content
        with open(filename, "wb") as file:
            file.write(image_content)

        return f"Image generated and saved to {filename} successfully."
