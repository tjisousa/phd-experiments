"""
Start Event Agent
Specialist in creating BPMN Start Events
"""

from google.adk.agents import Agent
from ..config import MODEL
from ..instructions import EventRules


StartEventAgent = Agent(
    name="StartEventAgent",
    model=MODEL,
    description=(
        "You are a BPMN Start Event specialist. You create valid BPMN start event code "
        "following BPMN 2.0 specifications."
    ),
    instruction=(
        f"You create BPMN Start Event elements. Follow these rules:\n"
        f"- {EventRules.ONE_START_EVENT}\n"
        f"- {EventRules.START_NO_INCOMING}\n"
        f"- {EventRules.VALID_EVENT_TYPES}\n\n"
        f"Read from session.state['scenario_plan'] to get the start event details. "
        f"Generate Python code using bpmn_lang.py:\n"
        f"  start = StartEvent('start', 'Start Event', event_type='none')\n\n"
        f"Store your output in session.state['elements']['start'] as:\n"
        f"{{\n"
        f"  'code': '<python code>',\n"
        f"  'variable': 'start',\n"
        f"  'element_id': 'start',\n"
        f"  'element_type': 'StartEvent'\n"
        f"}}\n\n"
        f"Return only the code snippet, nothing else."
    ),
)


