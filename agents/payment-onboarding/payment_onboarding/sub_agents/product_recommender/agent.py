# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Validate Business agent. Finds and verifies a business using name and location"""
import base64
import os
from io import BytesIO
from typing import Optional

import PIL.Image
from google.adk.agents import Agent
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import ToolContext, load_artifacts
from google.adk.tools.agent_tool import AgentTool
from google.genai import Client, types
from PIL import Image

from payment_onboarding.tools.salesforce import (
    get_opportunity_details,
    update_opportunity_stage,
    update_opportunity_with_comment,
)
from payment_onboarding.tools.search import google_search_grounding

# Only Vertex AI supports image generation for now.
client = Client()


from payment_onboarding.shared_libraries.types import (
    BusinessSuggestions,
    json_response_config,
)
from payment_onboarding.sub_agents.product_recommender import prompt, vaisearch
from payment_onboarding.tools.places import map_tool


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
                "pos_in_store_image.png",
                types.Part.from_bytes(
                    data=part.inline_data.data, mime_type="image/png"
                ),
            )
    return {
        "status": "success",
        "detail": "Image generated successfully and stored in artifacts.",
        "filename": "pos_in_store_image.png",
    }


def identify_pos_model_flash(prompt: str, tool_context: "ToolContext"):
    """Given an image identify the POS model."""
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to the image
    image_path = os.path.join(script_dir, "input_image.jpeg")

    # Now open the image using the absolute path
    image = PIL.Image.open(image_path)

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=[
            """You are an expert in identifying the make and model of a Point of Sale systems in a image. Identify the Point of Sale (POS) make and model in the image.
            If the image is not POS model then do not attempt to idenify it. 
            """,
            image,
        ],
    )
    return response.text


def call_vertex_ai_search(query: str, tool_context: "ToolContext"):

    # get the GOOGLE_CLOUD_PROJECT from .env
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("VERTEX_AI_SEARCH_LOCATION")
    engine_id = os.getenv("VERTEX_AI_SEARCH_ENGINE_ID")
    result = vaisearch.vertex_ai_search(project_id, location, engine_id, query)
    return result


def after_agent_callback(callback_context: ToolContext):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to the image
    image_path = os.path.join("file://", script_dir, "handheld_terminal_image.png")

    image_artifact = types.Part.from_uri(image_path, mime_type="image/png")
    callback_context.save_artifact(
        "handheld_terminal_image.png", artifact=image_artifact
    )


""" 
image_editor_agent = Agent(
    model="gemini-2.0-flash-001",
    name="image_editor_agent",
    description="An agent that edits images.",
    instruction="You are an agent whose job is to replace the POS system in the image with the recommended one.",
    tools=[generate_image_flash],
) """

""" identify_pos_model = Agent(
    model="gemini-2.0-flash-001",
    name="identify_pos_model",
    description="An agent that identifies the POS model in the images.",
    instruction="Given an image call the `identify_pos_model_flash` tool to identify the Point of Sale Terminal make and model.",
    tools=[identify_pos_model_flash, load_artifacts],
) """

knowledgebase_search_agent = Agent(
    # model="gemini-2.0-flash-001",
    model="gemini-2.5-pro-preview-03-25",
    name="knowledgebase_search_agent",
    description="A agent who searches Knowledgebase for Point of Sale (POS) products",
    instruction="""You are responsible for searching the datastore for technical information using `call_vertex_ai_search` about each of the Global Payments POS terminals.
    Show the summary followed by the  links in the document_links array from the result object in a table format.
    """,
    tools=[call_vertex_ai_search],
)

search_agent = Agent(
    # model="gemini-2.0-flash",
    model="gemini-2.5-pro-preview-03-25",
    name="search_agent",
    description="Searches for general information about Global Payments",
    instruction=prompt.SEARCH_AGENT_INSTR,
    tools=[google_search_grounding],
)

upsell_agent = Agent(
    model="gemini-2.0-flash",
    name="upsell_agent",
    description="Offers other products or services that may be useful to the customer",
    instruction="""If the user selects the Restaurant POS solution, tell the user the following 
    "Based on your Google product reviews there tends to be long lines at peak times. 
    A Handheld terminal would help to reduce the long lines. Would you be interested in adding that?  
""",
    after_agent_callback=after_agent_callback,
)


product_recommender_agent = Agent(
    model="gemini-2.0-flash-001",
    name="product_recommender_agent",
    description="A agent who recommends a POS solution based on the needs of the business owner",
    instruction=prompt.PRODUCT_RECOMENDER_AGENT_INSTR,
    tools=[
        AgentTool(agent=knowledgebase_search_agent),
        AgentTool(agent=search_agent),
        identify_pos_model_flash,
        generate_image_flash,
        get_opportunity_details,
        update_opportunity_with_comment,
        update_opportunity_stage,
    ],
)
