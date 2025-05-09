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

"""Generates dummy sales contract"""

from google.adk.agents import Agent
from google.adk.tools import load_artifacts

from payment_onboarding.tools.salesforce import (
    get_opportunity_details,
    update_opportunity_stage,
    update_opportunity_with_comment,
)

generate_contract = Agent(
    model="gemini-2.0-flash-001",
    name="generate_contract",
    description=""""An agent that generates a contract to purchase Point of Sale systems from Clover""",
    instruction="""You an agent that generates a contract for Clover Point of Sale systems. 
    - As the user if they would like to generate a Show the user a personalized url with their business name of the format "https://clover.com/buynow/<business_name>" where they can view the contract and purchase the POS system. 
    - Show the phone number and contact details for Clover Sales after showing the url.
    - Call `update_opportunity_stage` with new_stage as "Proposal/Negotiating".
    - Do not mention agent names or being transferred. Just do the tasks.

""",
    tools=[update_opportunity_stage],
)
