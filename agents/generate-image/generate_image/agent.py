import base64
import os
from io import BytesIO

import PIL.Image
from google.adk import Agent
from google.adk.tools import ToolContext, load_artifacts
from google.genai import Client, types
from PIL import Image

# Only Vertex AI supports image generation for now.
client = Client()


def generate_image(prompt: str, tool_context: "ToolContext"):
    """Generates an image based on the prompt."""
    response = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
    )
    if not response.generated_images:
        return {"status": "failed"}
    image_bytes = response.generated_images[0].image.image_bytes
    tool_context.save_artifact(
        "image.png",
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
    )
    return {
        "status": "success",
        "detail": "Image generated successfully and stored in artifacts.",
        "filename": "image.png",
    }


def generate_image_flash(prompt: str, tool_context: "ToolContext"):
    """Generates an image based on the prompt using Gemini Flash 2.0 Image generation model."""

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to the image
    image_path = os.path.join(script_dir, "input_image.jpeg")

    # Now open the image using the absolute path
    image = PIL.Image.open(image_path)

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[prompt, image],
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            tool_context.save_artifact(
                "image.png",
                types.Part.from_bytes(
                    data=part.inline_data.data, mime_type="image/png"
                ),
            )
    return {
        "status": "success",
        "detail": "Image generated successfully and stored in artifacts.",
        "filename": "image.png",
    }


def load_image(prompt: str, tool_context: "ToolContext"):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to the image
    image_path = os.path.join(script_dir, "handheld_terminal_image.png")
    image = PIL.Image.open(image_path)
    image_artifact = types.Part.from_bytes(
        data=image.tobytes("raw", "RGB"), mime_type="image/png"
    )
    tool_context.save_artifact(
        "handheld_terminal_image.png",
        types.Part.from_bytes(data=image.tobytes(), mime_type="image/png"),
    )


root_agent = Agent(
    model="gemini-2.0-flash",
    name="root_agent",
    description="Offers other products or services that may be useful to the customer",
    instruction="""
    -Call load_image
    - Tell the user the following 
    "Based on your Google product reviews there tends to be long lines at peak times. 
    A Handheld terminal would help to reduce the long lines. Would you be interested in adding that?"  
""",
    tools=[load_image],
)

# root_agent = Agent(
#    model="gemini-2.0-flash-001",
#    name="root_agent",
#    description="""An agent that edits images.""",
#    instruction="""You are an agent whose job is to generate or edit an image based on the user's prompt.
# """,
#    tools=[generate_image_flash, load_artifacts],
# )
