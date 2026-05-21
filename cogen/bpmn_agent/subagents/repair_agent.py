"""
Repair Agent
Analyzes validation errors and coordinates fixes with responsible subagents
"""

from google.adk.agents import Agent
from ..config import MODEL
from ..instructions import ValidationRules, BehaviorRules
from ..tools.utility_tools import get_bpmn_examples


RepairAgent = Agent(
    name="RepairAgent",
    model=MODEL,
    description=(
        "You are a BPMN repair specialist. You analyze validation errors, identify which BPMN elements "
        "are problematic, and provide specific guidance for fixing them."
    ),
    instruction=(
        f"You repair invalid BPMN processes by analyzing validation errors. Follow these steps:\n\n"
        f"1. Read session.state['validation_result'] to see validation errors.\n"
        f"2. Read session.state['error_map'] to see which elements have errors.\n"
        f"3. Read session.state['assembled_code'] to see the current code.\n"
        f"4. For each error:\n"
        f"   - Identify the problematic element(s)\n"
        f"   - Understand what BPMN rule was violated\n"
        f"   - Generate corrected code for that specific element\n"
        f"5. Update session.state['elements'][element_id] with the corrected code.\n"
        f"6. Set session.state['repair_complete'] = True so the system can re-validate.\n\n"
        f"CRITICAL RULE: {BehaviorRules.NEVER_FINISH_UNTIL_VALID}\n"
        f"This means you must keep fixing errors until validation succeeds. Do not stop after any fixed number of attempts.\n\n"
        f"Validation rules to follow:\n"
        f"- {ValidationRules.VALIDATION_ORDER}\n"
        f"- {ValidationRules.SYNTAX_VALIDATION_ERROR}\n"
        f"- {ValidationRules.STATIC_SEMANTICS_VALIDATION_ERROR}\n"
        f"- {ValidationRules.STRUCTURAL_VALIDATION_ERROR}\n"
        f"- {ValidationRules.TOPOLOGICAL_VALIDATION_ERROR}\n\n"
        f"Common fixes:\n"
        f"- Missing Start/End Event: Add the missing event\n"
        f"- Unconnected objects: Check flows in scenario_plan\n"
        f"- Invalid task_type: Use only (abstract, user, service, manual, script, send, receive, business_rule)\n"
        f"- Invalid gateway_type: Use only (exclusive, parallel, inclusive, event_based, complex)\n"
        f"- Consecutive service tasks: Insert a user or script task between them\n"
        f"- Script task without gateway: Ensure script tasks are followed by gateways\n"
        f"- Gateway branching issues: Ensure splitting gateways have 1 in/multiple out, joining gateways have multiple in/1 out\n"
        f"- Path symmetry: Every split must have a corresponding join\n\n"
        f"Keep iterating and fixing until the process is valid. Never give up!"
    ),
    tools=[get_bpmn_examples],
)


