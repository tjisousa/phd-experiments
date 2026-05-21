"""
Gateway Agent
Specialist in creating BPMN Gateways (exclusive, parallel, inclusive, event-based, complex)
"""

from google.adk.agents import Agent
from ..config import MODEL
from ..instructions import GatewayRules, TopologicalRules


GatewayAgent = Agent(
    name="GatewayAgent",
    model=MODEL,
    description=(
        "You are a BPMN Gateway specialist. You create valid BPMN gateway code for various types "
        "(exclusive, parallel, inclusive, event-based, complex) following BPMN 2.0 specifications."
    ),
    instruction=(
        f"You create BPMN Gateway elements. Follow these rules:\n"
        f"- {GatewayRules.VALID_GATEWAY_TYPES}\n"
        f"- {GatewayRules.GATEWAY_BRANCHING_RULE}\n"
        f"- {GatewayRules.GATEWAY_CANNOT_BE_BOTH}\n"
        f"- {GatewayRules.EXCLUSIVE_GATEWAY_BEHAVIOR}\n"
        f"- {GatewayRules.PARALLEL_GATEWAY_BEHAVIOR}\n"
        f"- {TopologicalRules.PATH_SYMMETRY_RULE}\n\n"
        f"Read from session.state['scenario_plan'] to get gateway details. "
        f"For each gateway in the plan, generate Python code using bpmn_lang.py:\n"
        f"  gateway1 = Gateway('gateway1', 'Decision Gateway', 'exclusive')\n"
        f"  gateway2 = Gateway('gateway2', 'Merge Gateway', 'exclusive')\n\n"
        f"Store each gateway in session.state['elements'][gateway_id] as:\n"
        f"{{\n"
        f"  'code': '<python code>',\n"
        f"  'variable': 'gateway1',\n"
        f"  'element_id': 'gateway1',\n"
        f"  'element_type': 'Gateway',\n"
        f"  'gateway_type': 'exclusive'\n"
        f"}}\n\n"
        f"IMPORTANT: Remember splitting gateways need corresponding joining gateways. "
        f"A gateway cannot be both a splitter and joiner simultaneously. "
        f"Return only the code snippets, nothing else."
    ),
)


