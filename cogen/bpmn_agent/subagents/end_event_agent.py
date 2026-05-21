"""
End Event Agent
Specialist in creating BPMN End Events
"""

from google.adk.agents import Agent
from ..config import MODEL
from ..instructions import EventRules


EndEventAgent = Agent(
    name="EndEventAgent",
    model=MODEL,
    description=(
        "You are a BPMN End Event specialist. You create valid BPMN end event code "
        "following BPMN 2.0 specifications."
    ),
    instruction=(
        f"You create BPMN End Event elements. Follow these rules:\n"
        f"- {EventRules.AT_LEAST_ONE_END_EVENT}\n"
        f"- {EventRules.END_NO_OUTGOING}\n"
        f"- {EventRules.VALID_EVENT_TYPES}\n\n"
        f"Read from session.state['scenario_plan'] to get the end event details. "
        f"Generate Python code using bpmn_lang.py:\n"
        f"  end = EndEvent('end', 'End Event', event_type='none')\n\n"
        f"Store your output in session.state['elements']['end'] as:\n"
        f"{{\n"
        f"  'code': '<python code>',\n"
        f"  'variable': 'end',\n"
        f"  'element_id': 'end',\n"
        f"  'element_type': 'EndEvent'\n"
        f"}}\n\n"
        f"Return only the code snippet, nothing else."
    ),
)


