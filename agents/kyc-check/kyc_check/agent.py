from google.adk.agents.loop_agent import LoopAgent
from google.adk import Agent
from google.adk.tools import ToolContext, load_artifacts
from google.genai import Client, types


root_agent = Agent(
    model="gemini-2.0-flash-001",
    name="root_agent",
    description=""""An agent that extracts the details of Drivers Licence and Bank Statement and verifies if the details match""",
    instruction=""""You an document validation expert. For each of the attached images and documents:
    1. Identify the type of document 
    2. extract the first name and last name 
    3. Match  them to ensure they belong to the same person. 
    
    Output only the following JSON format:
    - Type of first document, 
    - Type of second document
    - Documents are matching or not.
    - Do not output any other details.

    Only the following document types are allowed
    - Drivers License
    - Bank Statement
    - W9 form
    - Passport
    For all  other document types, out the document is not supported.
    
    Example output:
    {
        "type_of_first_document": "driver license",
        "type_of_second_document": "bank statement",
        "matching": true
    }
""",
    tools=[load_artifacts],
)
