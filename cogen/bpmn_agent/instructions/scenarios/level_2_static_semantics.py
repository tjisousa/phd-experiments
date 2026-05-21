"""
Level 2: Static Semantics Scenarios
Tests type checking and ID uniqueness from bpmn_lang.py:419-467 (validate_static_semantics)

Focus: Valid task types, gateway types, unique IDs
Difficulty: 2
"""

from ..rules import (
    BaseInstructions,
    EventRules,
    ActivityRules,
    GatewayRules,
)


LEVEL_2_SCENARIOS = [
    {
        "scenario_name": "l2_valid_task_types",
        "category": "semantics",
        "difficulty_level": 2,
        "test_type": "positive",
        "description": "Generate process using multiple valid BPMN 2.0 task types",
        "rules_tested": ["VALID_TASK_TYPES"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            ActivityRules.VALID_TASK_TYPES,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
        ]),
        "prompt": "Create a document workflow: start → scan document (user task) → extract data (service task) → send notification (send task) → manual filing (manual task) → end"
    },
    {
        "scenario_name": "l2_invalid_task_type",
        "category": "semantics",
        "difficulty_level": 2,
        "test_type": "negative",
        "description": "Generate task with invalid task_type not in BPMN 2.0 spec (invalid)",
        "rules_tested": ["VALID_TASK_TYPES"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a task with an INVALID task type like 'custom' or 'special' to test validation."
        ]),
        "prompt": "Create a process with an invalid task type: start → prepare (user task) → execute (task_type='custom') → end"
    },
    {
        "scenario_name": "l2_valid_gateway_types",
        "category": "semantics",
        "difficulty_level": 2,
        "test_type": "positive",
        "description": "Generate process using multiple valid BPMN 2.0 gateway types",
        "rules_tested": ["VALID_GATEWAY_TYPES"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            GatewayRules.VALID_GATEWAY_TYPES,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
        ]),
        "prompt": "Create a loan process: start → submit application → exclusive gateway checks credit → if good: parallel gateway (process docs AND verify income) → join → approve → end; if bad: reject → end"
    },
    {
        "scenario_name": "l2_invalid_gateway_type",
        "category": "semantics",
        "difficulty_level": 2,
        "test_type": "negative",
        "description": "Generate gateway with invalid gateway_type not in BPMN 2.0 spec (invalid)",
        "rules_tested": ["VALID_GATEWAY_TYPES"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a gateway with an INVALID type like 'conditional' or 'custom_gateway' to test validation."
        ]),
        "prompt": "Create a process with invalid gateway: start → collect data → custom decision gateway (gateway_type='conditional') → path1: approve → end, path2: reject → end"
    },
    {
        "scenario_name": "l2_unique_ids",
        "category": "semantics",
        "difficulty_level": 2,
        "test_type": "positive",
        "description": "Generate process ensuring all elements have unique IDs",
        "rules_tested": ["UNIQUE_IDS"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "All process elements must have unique IDs.",
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
        ]),
        "prompt": "Create an invoice processing workflow: start → receive invoice → validate invoice → process payment → archive invoice → end (ensure all elements have unique IDs)"
    },
    {
        "scenario_name": "l2_duplicate_ids",
        "category": "semantics",
        "difficulty_level": 2,
        "test_type": "negative",
        "description": "Generate process with duplicate IDs across elements (invalid)",
        "rules_tested": ["UNIQUE_IDS"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create TWO elements with the SAME ID to test validation (e.g., both tasks with id='task1')."
        ]),
        "prompt": "Create a process where two tasks deliberately share the same ID: start → task A (id='task1') → task B (id='task1') → end"
    },
]

