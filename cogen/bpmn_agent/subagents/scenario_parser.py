"""
Scenario Parser Agent
Parses natural language BPMN scenarios into structured plans
"""

from google.adk.agents import Agent
from ..config import MODEL

# Import the BPMN examples tool
from ..tools.utility_tools import get_bpmn_examples

# Tool for scenario parsing
def parse_scenario(scenario_text: str) -> dict:
    """
    Parse a BPMN scenario into a structured plan.
    
    Args:
        scenario_text: Natural language description of the BPMN process
    
    Returns:
        Structured plan with elements and flows
    """
    from ..tools.orchestration_tools import parse_scenario_to_plan
    return {"status": "success", "plan": parse_scenario_to_plan(scenario_text)}


ScenarioParserAgent = Agent(
    name="ScenarioParser",
    model=MODEL,
    description=(
        "You parse natural language BPMN process descriptions into structured plans. "
        "Your job is to identify all BPMN elements (start events, tasks, gateways, end events) "
        "and determine the sequence flows between them. "
        "You have access to example BPMN processes via the get_bpmn_examples tool for inspiration or guidance."
    ),
    instruction=(
        "Parse the user's scenario description and call the parse_scenario tool. "
        "Store the parsed plan in session.state['scenario_plan']. "
        "Ensure you identify: task types (user, service, script), gateway types (exclusive, parallel), "
        "and the proper sequence of elements. "
        "You may use the get_bpmn_examples tool to reference example BPMN processes if needed. "
        "Return a confirmation that parsing is complete."
    ),
    tools=[parse_scenario, get_bpmn_examples],
)
