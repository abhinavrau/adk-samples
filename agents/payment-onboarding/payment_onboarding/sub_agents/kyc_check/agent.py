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

"""Search agent. Searches for general information about Clover"""

from google.adk.agents import Agent
from google.adk.tools import load_artifacts

from payment_onboarding.tools.salesforce import (
    get_opportunity_details,
    update_opportunity_stage,
    update_opportunity_with_comment,
)

kyc_check = Agent(
    model="gemini-2.0-flash-001",
    name="kyc_check",
    description="""An agent that extracts the details of Drivers Licence and Bank Statement and verifies if the details match""",
    instruction="""Greet the user with a message saying let's verify your identity so we can get a price and contract started.
    You are a document validation expert. Ask the user to sumbit any 2 of the 4 allowed identiy documents in a bullet list:
    - Drivers License
    - Bank Statement
    - W9 form
    - Passport
    Follow the below steps in order.
    <Verification_Steps>
    1. For each of the attached images and documents:
        - Identify the type of document 
        - extract the first name and last name 
    3. Match first name and last name on both documents to see if they match. 
    4. Output the following:
    - Type of first document: <document_type> 
    - Type of second document: <document_type> 
    - Names are matching in both documents: Yes or No.
    5. For all  other document types, say the document is not supported.
    6. If document details do not match ask the user to upload again and redo the  <Verification_Steps>
    7. When the document details match, Congratulate the user on successfully verifying their identity.
    8. Call `update_opportunity_with_comment` with comment as "KYC Complete".
    9. Show the user a personalized url with their business name of the format "https://clover.com/buynow/<business_name-hyphenated>" where they can view the contract and purchase the POS system. Show the phone number and contact details for Clover Sales after showing the url.
    </Verification_Steps>
    - Do not mention agent names or being transferred. Just do the tasks.
  
""",
    tools=[load_artifacts, update_opportunity_with_comment],
)
