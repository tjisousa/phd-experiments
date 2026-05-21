"""
Validation Rules
Rules for validating BPMN processes at different levels
"""


class ValidationRules:
    """Rules for validating BPMN processes at different levels"""
    
    # Validation Order
    VALIDATION_ORDER = (
        "Validation must be performed in this order: "
        "(1) Syntax validation, (2) Static semantics validation, "
        "(3) Structural rules validation, (4) Topological rules validation."
    )
    
    # Syntax Validation
    SYNTAX_VALIDATION_ERROR = (
        "If the process has syntax errors (e.g., missing Start/End Events, unconnected objects), "
        "address them first before checking for static semantic errors."
    )
    
    # Static Semantics Validation
    STATIC_SEMANTICS_VALIDATION_ERROR = (
        "If the process has static semantic errors, address them after resolving any syntax errors. "
        "This includes type checking, such as ensuring 'task_type' for 'Task' objects is one of the allowed BPMN 2.0 types "
        "(abstract, user, service, manual, script, send, receive, business_rule), "
        "ensuring 'gateway_type' for 'Gateway' objects is one of the allowed types "
        "(exclusive, parallel, inclusive, event_based, complex), "
        "and that 'SequenceFlow' sources and targets are valid 'FlowObject' instances."
    )
    
    # Structural Validation
    STRUCTURAL_VALIDATION_ERROR = (
        "Structural validation checks rules like no consecutive service tasks, "
        "maximum task sequences, mandatory error handling, and gateway branching patterns."
    )
    
    # Topological Validation
    TOPOLOGICAL_VALIDATION_ERROR = (
        "Topological validation checks path symmetry (splits must have corresponding joins), "
        "valid loop structures (loops must have exits), and reachability constraints."
    )
    
    # Post-Validation Actions
    VALID_PROCESS = (
        "If the process is valid in syntax, static semantics, structural rules, and topological rules, "
        "verify it corresponds to the user's request."
    )
    
    INVALID_PROCESS_SUGGESTIONS = (
        "If the process is not valid (either syntax, static semantics, structural, or topological), "
        "call the suggest_improvements tool to get suggestions for improvements."
    )
    
    NO_SUGGEST_IF_VALID = (
        "Never call the suggest_improvements tool if the process is already valid "
        "in all validation levels (syntax, static semantics, structural, topological). This is a mistake."
    )

