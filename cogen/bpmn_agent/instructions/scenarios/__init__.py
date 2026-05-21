"""
BPMN Test Scenarios Module - Level-Based Structure
Exports all test scenario categories organized by difficulty levels
"""

from .level_1_basic_syntax import LEVEL_1_SCENARIOS
from .level_2_static_semantics import LEVEL_2_SCENARIOS
from .level_3_event_rules import LEVEL_3_SCENARIOS
from .level_4_structural_rules import LEVEL_4_SCENARIOS
from .level_5_topological_reachability import LEVEL_5_SCENARIOS
from .level_6_integration_complex import LEVEL_6_SCENARIOS

__all__ = [
    "LEVEL_1_SCENARIOS",
    "LEVEL_2_SCENARIOS",
    "LEVEL_3_SCENARIOS",
    "LEVEL_4_SCENARIOS",
    "LEVEL_5_SCENARIOS",
    "LEVEL_6_SCENARIOS",
]
