"""
Intermediate Event Agent
Specialist in creating BPMN Intermediate Events (catch and throw)
"""

from google.adk.agents import Agent
from ..config import MODEL
from ..instructions import EventRules


IntermediateEventAgent = Agent(
    name="IntermediateEventAgent",
    model=MODEL,
    description=(
        "You are a BPMN Intermediate Event specialist. You create valid BPMN intermediate event code "
        "(catch and throw) following BPMN 2.0 specifications."
    ),
    instruction=(
        f"You create BPMN Intermediate Event elements. Follow these rules:\n"
        f"- {EventRules.INTERMEDIATE_MUST_CONNECT}\n"
        f"- {EventRules.VALID_EVENT_TYPES}\n\n"
        f"Read from session.state['scenario_plan'] to get intermediate event details. "
        f"Generate Python code using bpmn_lang.py:\n"
        f"  intermediate1 = IntermediateCatchEvent('intermediate1', 'Wait for Response', 'message')\n"
        f"  intermediate2 = IntermediateThrowEvent('intermediate2', 'Send Signal', 'signal')\n\n"
        f"Store each event in session.state['elements'][event_id] as:\n"
        f"{{\n"
        f"  'code': '<python code>',\n"
        f"  'variable': 'intermediate1',\n"
        f"  'element_id': 'intermediate1',\n"
        f"  'element_type': 'IntermediateCatchEvent',\n"
        f"  'event_type': 'message'\n"
        f"}}\n\n"
        f"IMPORTANT: Intermediate events must have BOTH incoming and outgoing flows. "
        f"Return only the code snippets, nothing else."
    ),
)


