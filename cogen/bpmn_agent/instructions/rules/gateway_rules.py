"""
Gateway Rules
Rules for BPMN Gateways (Decision and Merge points)
"""


class GatewayRules:
    """Rules for BPMN Gateways (Decision and Merge points)"""
    
    # Gateway Type Rules
    VALID_GATEWAY_TYPES = (
        "Gateways must use valid BPMN 2.0 gateway types: "
        "exclusive (XOR - only one path), parallel (AND - all paths simultaneously), "
        "inclusive (OR - one or more paths), event_based (decision based on events), "
        "complex (complex decision logic)."
    )
    
    # Gateway Branching Rules
    GATEWAY_BRANCHING_RULE = (
        "A Gateway must conform to specific branching rules: "
        "a 'splitting' gateway must have exactly one incoming and at least two outgoing sequence flows. "
        "A 'joining' gateway must have multiple incoming flows and exactly one outgoing flow. "
        "Gateways with only one-in/one-out are redundant and not allowed."
    )
    
    GATEWAY_CANNOT_BE_BOTH = (
        "A gateway cannot be both a splitting and joining gateway simultaneously "
        "(i.e., multiple incoming AND multiple outgoing flows). "
        "Use separate gateways for splitting and joining."
    )
    
    # Gateway Type-Specific Rules
    EXCLUSIVE_GATEWAY_BEHAVIOR = (
        "Exclusive gateways (XOR) must have exactly one path selected based on conditions. "
        "All outgoing flows from a splitting exclusive gateway should have mutually exclusive conditions."
    )
    
    PARALLEL_GATEWAY_BEHAVIOR = (
        "Parallel gateways (AND) execute all outgoing paths simultaneously when splitting, "
        "and wait for all incoming paths to complete before proceeding when joining."
    )

