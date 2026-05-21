from google.adk.agents import Agent, SequentialAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types
from google.adk.models.lite_llm import LiteLlm
from .config import MODEL, BENCHMARK_NAME
from .instructions import BehaviorRules
from .tools import (
    validate_process,
    suggest_improvements,
    get_bpmn_examples,
)
# Import existing specialized subagents
from .subagents import (
    ScenarioParserAgent,
    StartEventAgent,
    EndEventAgent,
    TaskAgent,
    GatewayAgent,
    CollectorAgent,
)

instruction = \
    BehaviorRules.POST_CODE_GEN_NO_SUGGEST + " " \
    + BehaviorRules.ITERATIVE_REFINEMENT + " " \
    + BehaviorRules.NEVER_FINISH_UNTIL_VALID


def create_bpmn_multi_agent():
    """
    Creates a multi-agent BPMN system using SequentialAgent with existing specialized subagents.
    
    The architecture follows the original design:
    - ScenarioParser: Parses natural language into structured BPMN plan
    - StartEventAgent: Generates start event code
    - TaskAgent: Generates task code (user, service, script, etc.)
    - GatewayAgent: Generates gateway code (if needed)
    - EndEventAgent: Generates end event code
    - CollectorAgent: Assembles all elements and validates
    - RepairAgent: Fixes validation errors (if needed)
    
    These subagents were already created in bpmn_agent/subagents/
    """
    
    final_validator = Agent(
        name="FinalValidator",
        model=MODEL,
        description=(
            "You perform final validation and refinement of the assembled BPMN code."
        ),
        instruction=(
            f"{BehaviorRules.POST_CODE_GEN_NO_SUGGEST}\n"
            f"{BehaviorRules.ITERATIVE_REFINEMENT}\n"
            f"{BehaviorRules.NEVER_FINISH_UNTIL_VALID}\n\n"
            "Review the complete BPMN code from the previous agents:\n\n"
            "STEP 1: Extract the complete Python code\n"
            "STEP 2: Use validate_process tool to verify correctness\n"
            "STEP 3: If validation fails:\n"
            "  - Analyze the error messages\n"
            "  - Fix the specific issues\n"
            "  - Validate again\n"
            "  - REPEAT until validation succeeds (valid=True)\n"
            "  - DO NOT STOP after a fixed number of attempts\n"
            "  - Keep iterating until the validate_process tool returns success\n"
            "STEP 4: Output the final validated code ONLY when validation succeeds\n\n"
            "CRITICAL: You MUST continue fixing and validating until you receive valid=True from validate_process.\n"
            "Do not finish, do not give up, do not stop after N attempts. Continue until success.\n\n"
            "Common fixes:\n"
            "- Invalid task types (must be: abstract, user, service, manual, script, send, receive, business_rule)\n"
            "- Missing connections\n"
            "- Wrong SequenceFlow API (no id parameter!)\n"
            "Utilize the following tools to ensure high-quality results:\n"
            "- get_bpmn_examples: Reference example BPMN processes for inspiration or guidance.\n"
            "- validate_process: Check the validity of your BPMN code and address any issues found.\n"
            "- suggest_improvements: Recommend enhancements or optimizations to the process.\n"
            "IMPORTANT: Always call the validate_process tool to check the validity of your BPMN code.\n"
            "IMPORTANT: Do not stop until the validate_process tool returns valid=True\n"
        ),
        tools=[validate_process, get_bpmn_examples, suggest_improvements],
    )
    
    return SequentialAgent(
        name="BPMNMultiAgent",
        description=(
            "Multi-agent system with specialized subagents for each BPMN element type. "
            "Uses session.state for inter-agent communication. "
            "Flow: ScenarioParser -> StartEvent -> Task -> Gateway -> EndEvent -> Collector -> Validator"
        ),
        sub_agents=[
            ScenarioParserAgent,     # Agent instance - parses scenario
            StartEventAgent,         # Agent instance - generates start events
            TaskAgent,               # Agent instance - generates tasks
            GatewayAgent,            # Agent instance - generates gateways (if needed)
            EndEventAgent,           # Agent instance - generates end events
            CollectorAgent(),        # Custom BaseAgent - assembles & validates
            final_validator,         # Agent instance - final validation & iterative repair
        ],
    )


bpmn_multi_agent = create_bpmn_multi_agent()

object.__setattr__(bpmn_multi_agent, 'tools', [validate_process, get_bpmn_examples, suggest_improvements])
object.__setattr__(bpmn_multi_agent, 'benchmark_name', BENCHMARK_NAME)

root_agent = bpmn_multi_agent


# Default export
__all__ = [
    "root_agent",
    "bpmn_multi_agent",
    "create_bpmn_multi_agent",
]