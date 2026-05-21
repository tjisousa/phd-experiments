"""
Scenario Utilities
Utility functions for accessing and managing test scenarios with new level-based structure
"""

from .scenarios import (
    LEVEL_1_SCENARIOS,
    LEVEL_2_SCENARIOS,
    LEVEL_3_SCENARIOS,
    LEVEL_4_SCENARIOS,
    LEVEL_5_SCENARIOS,
    LEVEL_6_SCENARIOS,
)


ALL_SCENARIOS = {
    "level_1_basic_syntax": LEVEL_1_SCENARIOS,
    "level_2_static_semantics": LEVEL_2_SCENARIOS,
    "level_3_event_rules": LEVEL_3_SCENARIOS,
    "level_4_structural_rules": LEVEL_4_SCENARIOS,
    "level_5_topological_reachability": LEVEL_5_SCENARIOS,
    "level_6_integration_complex": LEVEL_6_SCENARIOS,
}


def get_scenarios_by_category(category: str) -> list:
    """
    Get all scenarios from a specific level category.
    
    Args:
        category: One of 'level_1_basic_syntax', 'level_2_static_semantics', 
                  'level_3_event_rules', 'level_4_structural_rules', 
                  'level_5_topological_reachability', 'level_6_integration_complex'
    
    Returns:
        List of scenario dictionaries
    """
    return ALL_SCENARIOS.get(category, [])


def get_scenarios_by_validation_category(validation_category: str) -> list:
    """
    Get all scenarios from a specific validation category.
    
    Args:
        validation_category: One of 'syntax', 'semantics', 'event_rules', 
                            'structural', 'topological', 'integration'
    
    Returns:
        List of scenario dictionaries matching the validation category
    """
    scenarios = []
    for level_scenarios in ALL_SCENARIOS.values():
        for scenario in level_scenarios:
            if scenario.get("category") == validation_category:
                scenarios.append(scenario)
    return scenarios


def get_scenarios_by_difficulty_level(level: int) -> list:
    """
    Get all scenarios at a specific difficulty level.
    
    Args:
        level: Difficulty level (1-6)
    
    Returns:
        List of scenario dictionaries at that difficulty level
    """
    scenarios = []
    for level_scenarios in ALL_SCENARIOS.values():
        for scenario in level_scenarios:
            if scenario.get("difficulty_level") == level:
                scenarios.append(scenario)
    return scenarios


def get_scenarios_by_test_type(test_type: str) -> list:
    """
    Get all scenarios of a specific test type.
    
    Args:
        test_type: Either 'positive' or 'negative'
    
    Returns:
        List of scenario dictionaries matching the test type
    """
    scenarios = []
    for level_scenarios in ALL_SCENARIOS.values():
        for scenario in level_scenarios:
            if scenario.get("test_type") == test_type:
                scenarios.append(scenario)
    return scenarios


def get_complexity_progression() -> list:
    """
    Get all scenarios ordered by difficulty level for scaling analysis.
    
    Returns:
        List of all scenarios sorted by difficulty_level (1-6)
    """
    all_scenarios_list = []
    for level_scenarios in ALL_SCENARIOS.values():
        all_scenarios_list.extend(level_scenarios)
    
    return sorted(all_scenarios_list, key=lambda x: x.get("difficulty_level", 0))


def get_all_scenarios() -> dict:
    """
    Get all scenarios from all categories.
    
    Returns:
        Dictionary of category names to scenario lists
    """
    return ALL_SCENARIOS


def count_scenarios() -> dict:
    """
    Count scenarios by various dimensions.
    
    Returns:
        Dictionary with scenario counts
    """
    total = sum(len(scenarios) for scenarios in ALL_SCENARIOS.values())
    
    # Count by validation category
    by_validation_category = {}
    for val_cat in ['syntax', 'semantics', 'event_rules', 'structural', 'topological', 'integration']:
        by_validation_category[val_cat] = len(get_scenarios_by_validation_category(val_cat))
    
    # Count by test type
    by_test_type = {
        'positive': len(get_scenarios_by_test_type('positive')),
        'negative': len(get_scenarios_by_test_type('negative'))
    }
    
    # Count by difficulty level
    by_difficulty = {
        level: len(get_scenarios_by_difficulty_level(level))
        for level in range(1, 7)
    }
    
    return {
        'total': total,
        'by_level': {k: len(v) for k, v in ALL_SCENARIOS.items()},
        'by_validation_category': by_validation_category,
        'by_test_type': by_test_type,
        'by_difficulty': by_difficulty,
    }
