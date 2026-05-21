"""
Activity Rules
Rules for BPMN Activities (Tasks and Subprocesses)
"""


class ActivityRules:
    """Rules for BPMN Activities (Tasks and Subprocesses)"""
    
    # Task Type Rules (BPMN 2.0.2 standard)
    VALID_TASK_TYPES = (
        "Tasks must use valid BPMN 2.0 task types: "
        "abstract (generic task), user (human-performed), service (automated service), "
        "manual (physical task outside system), script (script execution), "
        "send (message sending), receive (message receiving), business_rule (business rules execution)."
    )
    
    # Task Sequencing Rules
    NO_CONSECUTIVE_SERVICE_TASKS = (
        "A 'service' task cannot be directly followed by another 'service' task. "
        "There must be an intermediate 'user' task, 'script' task, or a gateway between them."
    )
    
    MAX_TASKS_IN_A_ROW = (
        "No more than four tasks of any type should be chained in a sequence "
        "without an intermediate event or gateway."
    )
    
    # Error Handling Rules
    MANDATORY_ERROR_HANDLING_FOR_SCRIPTS = (
        "Every 'script' task must be followed by a decision gateway to handle potential script failures."
    )
    
    # Task-Event Interaction Rules
    NO_EVENT_BETWEEN_SAME_TASKS = (
        "An IntermediateCatchEvent cannot be placed between two Tasks of the same 'task_type'. "
        "For example, a sequence like User Task -> Intermediate Event -> User Task is forbidden."
    )

