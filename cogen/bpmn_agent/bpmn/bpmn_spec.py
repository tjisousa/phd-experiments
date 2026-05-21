from typing import List, Dict

"""
BPMN 2.0.2 Specification Constants
Based on the Object Management Group (OMG) BPMN 2.0.2 standard
"""

# Define allowed task types for BPMN Tasks (BPMN 2.0 standard)
ALLOWED_TASK_TYPES: List[str] = [
    "abstract",      # Generic task with no specific type
    "user",          # Task performed by a human user
    "service",       # Automated task performed by a web service or application
    "manual",        # Physical task performed outside the process engine
    "script",        # Task executed by a process engine's script engine
    "send",          # Task that sends a message to an external participant
    "receive",       # Task that waits for a message from an external participant
    "business_rule"  # Task that executes business rules
]

# Define allowed gateway types (BPMN 2.0 standard)
ALLOWED_GATEWAY_TYPES: List[str] = [
    "exclusive",     # XOR gateway - only one path is chosen (default behavior)
    "parallel",      # AND gateway - all paths are executed simultaneously
    "inclusive",     # OR gateway - one or more paths are chosen
    "event_based",   # Gateway where the decision is based on events
    "complex"        # Gateway with complex decision logic
]

# Define allowed event types (BPMN 2.0 standard)
ALLOWED_EVENT_TYPES: Dict[str, List[str]] = {
    "start": ["none", "message", "timer", "conditional", "signal", "multiple", "parallel_multiple"],
    "end": ["none", "message", "error", "escalation", "cancel", "compensation", "signal", "terminate", "multiple"],
    "intermediate_catch": ["message", "timer", "conditional", "link", "signal", "multiple", "parallel_multiple"],
    "intermediate_throw": ["none", "message", "escalation", "link", "compensation", "signal", "multiple"],
    "boundary": ["message", "timer", "error", "escalation", "cancel", "compensation", "conditional", "signal", "multiple", "parallel_multiple"]
}

# BPMN Element Categories (for organizational purposes)
FLOW_OBJECTS = ["Event", "Activity", "Gateway"]
CONNECTING_OBJECTS = ["SequenceFlow", "MessageFlow", "Association"]
SWIMLANES = ["Pool", "Lane"]
ARTIFACTS = ["DataObject", "Group", "Annotation"]
