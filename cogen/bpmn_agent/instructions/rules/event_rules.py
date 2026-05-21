"""
Event Rules
Rules for BPMN Events (Start, End, Intermediate)
"""


class EventRules:
    """Rules for BPMN Events (Start, End, Intermediate)"""
    
    # Syntax Rules
    ONE_START_EVENT = "A valid BPMN process must have exactly one Start Event."
    AT_LEAST_ONE_END_EVENT = "A valid BPMN process must have at least one End Event."
    
    # Semantic Rules
    START_NO_INCOMING = "A Start Event must not have incoming sequence flows."
    END_NO_OUTGOING = "An End Event must not have outgoing sequence flows."
    INTERMEDIATE_MUST_CONNECT = "Intermediate Events must have both incoming and outgoing sequence flows."
    
    # Event Type Rules
    VALID_EVENT_TYPES = (
        "Events must use valid BPMN 2.0 event types: "
        "Start events can be: none, message, timer, conditional, signal, multiple, parallel_multiple. "
        "End events can be: none, message, error, escalation, cancel, compensation, signal, terminate, multiple. "
        "Intermediate catch events can be: message, timer, conditional, link, signal, multiple, parallel_multiple. "
        "Intermediate throw events can be: none, message, escalation, link, compensation, signal, multiple."
    )

