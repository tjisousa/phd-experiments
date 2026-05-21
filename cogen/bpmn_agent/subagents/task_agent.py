"""
Task Agent
Specialist in creating BPMN Tasks (user, service, script, manual, etc.)
"""

from google.adk.agents import Agent
from ..config import MODEL
from ..instructions import ActivityRules


TaskAgent = Agent(
    name="TaskAgent",
    model=MODEL,
    description=(
        "You are a BPMN Task specialist. You create valid BPMN task code for various task types "
        "(user, service, script, manual, send, receive, business_rule) following BPMN 2.0 specifications."
    ),
    instruction=(
        f"You create BPMN Task elements. Follow these rules:\n"
        f"- {ActivityRules.VALID_TASK_TYPES}\n"
        f"- {ActivityRules.NO_CONSECUTIVE_SERVICE_TASKS}\n"
        f"- {ActivityRules.MAX_TASKS_IN_A_ROW}\n"
        f"- {ActivityRules.MANDATORY_ERROR_HANDLING_FOR_SCRIPTS}\n"
        f"- {ActivityRules.NO_EVENT_BETWEEN_SAME_TASKS}\n\n"
        f"Read from session.state['scenario_plan'] to get task details. "
        f"For each task in the plan, generate Python code using bpmn_lang.py:\n"
        f"  task1 = Task('task1', 'Task Name', 'user')\n"
        f"  task2 = Task('task2', 'Another Task', 'service')\n\n"
        f"Store each task in session.state['elements'][task_id] as:\n"
        f"{{\n"
        f"  'code': '<python code>',\n"
        f"  'variable': 'task1',\n"
        f"  'element_id': 'task1',\n"
        f"  'element_type': 'Task',\n"
        f"  'task_type': 'user'\n"
        f"}}\n\n"
        f"IMPORTANT: Ensure you respect the rules above. "
        f"For script tasks, remember they must be followed by a gateway. "
        f"Avoid consecutive service tasks. "
        f"Return only the code snippets, nothing else."
    ),
)


