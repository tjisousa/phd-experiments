"""
Rule Utilities
Utility functions for accessing and managing BPMN rules
"""

from .rules import (
    BaseInstructions,
    BehaviorRules,
    ReasoningRules,
    EventRules,
    ActivityRules,
    GatewayRules,
    SequenceFlowRules,
    DataRules,
    TopologicalRules,
    ValidationRules,
    OptimizationRules,
    CognitiveCapabilities,
)


RULE_CATEGORIES = {
    "event_rules": EventRules,
    "activity_rules": ActivityRules,
    "gateway_rules": GatewayRules,
    "sequence_flow_rules": SequenceFlowRules,
    "data_rules": DataRules,
    "topological_rules": TopologicalRules,
    "validation_rules": ValidationRules,
    "behavior_rules": BehaviorRules,
    "reasoning_rules": ReasoningRules,
    "optimization_rules": OptimizationRules,
    "cognitive_capabilities": CognitiveCapabilities,
}


def get_rule_by_category(category: str) -> dict:
    """
    Get all rules from a specific category.
    
    Args:
        category: Name of the category (e.g., 'event_rules', 'gateway_rules')
    
    Returns:
        Dictionary of rule names to rule text
    """
    if category not in RULE_CATEGORIES:
        return {}
    
    rule_class = RULE_CATEGORIES[category]
    rules = {}
    for attr in dir(rule_class):
        if not attr.startswith('_') and attr.isupper():
            rules[attr] = getattr(rule_class, attr)
    return rules


def get_all_rules() -> dict:
    """
    Get all rules from all categories.
    
    Returns:
        Dictionary of category names to rule dictionaries
    """
    all_rules = {}
    for category in RULE_CATEGORIES:
        all_rules[category] = get_rule_by_category(category)
    return all_rules

