"""
Central instructions package for agents.
Exports BPMN 2.0.2 aligned instruction sets and test scenarios.
"""

from .instruction_sets import (
    default_instructions,
    comprehensive_instructions,
    structural_only_instructions,
)
from .rules import (
    EventRules,
    ActivityRules,
    GatewayRules,
    SequenceFlowRules,
    DataRules,
    TopologicalRules,
    ValidationRules,
    BehaviorRules,
    ReasoningRules,
    BaseInstructions,
    OptimizationRules,
    CognitiveCapabilities,
)
from .rule_utilities import (
    RULE_CATEGORIES,
    get_rule_by_category,
    get_all_rules,
)
from .scenarios import (
    LEVEL_1_SCENARIOS,
    LEVEL_2_SCENARIOS,
    LEVEL_3_SCENARIOS,
    LEVEL_4_SCENARIOS,
    LEVEL_5_SCENARIOS,
    LEVEL_6_SCENARIOS,
)
from .scenario_utilities import (
    ALL_SCENARIOS,
    get_scenarios_by_category,
    get_scenarios_by_validation_category,
    get_scenarios_by_difficulty_level,
    get_scenarios_by_test_type,
    get_complexity_progression,
    get_all_scenarios,
    count_scenarios,
)

__all__ = [
    "default_instructions",
    "comprehensive_instructions",
    "structural_only_instructions",
    # Rule classes
    "EventRules",
    "ActivityRules",
    "GatewayRules",
    "SequenceFlowRules",
    "DataRules",
    "TopologicalRules",
    "ValidationRules",
    "BehaviorRules",
    "ReasoningRules",
    "BaseInstructions",
    "OptimizationRules",
    "CognitiveCapabilities",
    # Rule utilities
    "RULE_CATEGORIES",
    "get_rule_by_category",
    "get_all_rules",
    # Scenarios
    "LEVEL_1_SCENARIOS",
    "LEVEL_2_SCENARIOS",
    "LEVEL_3_SCENARIOS",
    "LEVEL_4_SCENARIOS",
    "LEVEL_5_SCENARIOS",
    "LEVEL_6_SCENARIOS",
    "ALL_SCENARIOS",
    "get_scenarios_by_category",
    "get_scenarios_by_validation_category",
    "get_scenarios_by_difficulty_level",
    "get_scenarios_by_test_type",
    "get_complexity_progression",
    "get_all_scenarios",
    "count_scenarios",
]
