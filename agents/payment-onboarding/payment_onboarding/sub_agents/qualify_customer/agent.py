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

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from payment_onboarding.shared_libraries.types import (
    BusinessSuggestions,
    json_response_config,
)
from payment_onboarding.sub_agents.qualify_customer import prompt
from payment_onboarding.tools.places import map_tool

lookup_agent = Agent(
    model="gemini-2.5-flash-preview-04-17",
    name="lookup_agent",
    description="This agent looks up business listings",
    instruction=prompt.LOOKUP_AGENT_INSTR,
    # disallow_transfer_to_parent=True,
    # disallow_transfer_to_peers=True,
    output_schema=BusinessSuggestions,
    output_key="poi",
    generate_content_config=json_response_config,
)

qualify_customer_agent = Agent(
    model="gemini-2.5-pro-preview-03-25",
    name="qualify_customer_agent",
    description="A validate business agent who helps users verify their business listing using business name and location",
    instruction=prompt.VERIFY_BUSINESS_AGENT_INSTR,
    tools=[AgentTool(agent=lookup_agent), map_tool],
)
