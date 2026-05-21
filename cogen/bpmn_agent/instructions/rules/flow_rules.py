"""
Sequence Flow Rules
Rules for BPMN Sequence Flows (connecting flow objects)
"""


class SequenceFlowRules:
    """Rules for BPMN Sequence Flows (connecting flow objects)"""
    
    ALL_OBJECTS_CONNECTED = (
        "All flow objects must be connected to at least one sequence flow. "
        "Unconnected objects create dead ends or unreachable paths."
    )
    
    VALID_CONNECTIONS = (
        "Sequence flows must connect valid FlowObject instances "
        "(Events, Tasks, Gateways). Both source and target must be valid flow objects."
    )
    
    NO_FLOW_BETWEEN_EVENTS = (
        "Avoid direct sequence flows between events without intermediate tasks or gateways, "
        "unless there is a clear semantic reason (e.g., Start Event to Intermediate Event in event-based patterns)."
    )

