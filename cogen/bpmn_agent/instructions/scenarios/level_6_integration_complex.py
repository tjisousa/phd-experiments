"""
Level 6: Integration and Complex Scenarios
Tests multiple rules simultaneously in realistic, complex processes

Focus: Multi-rule integration, real-world complexity, combined constraints
Difficulty: 6 (Hardest)
"""

from ..rules import (
    BaseInstructions,
    EventRules,
    ActivityRules,
    GatewayRules,
    TopologicalRules,
)


LEVEL_6_SCENARIOS = [
    {
        "scenario_name": "l6_order_fulfillment_complex",
        "category": "integration",
        "difficulty_level": 6,
        "test_type": "positive",
        "description": "Generate complete order fulfillment with parallel gateways, error handling, and proper structure",
        "rules_tested": [
            "ONE_START_EVENT", "AT_LEAST_ONE_END_EVENT",
            "GATEWAY_BRANCHING_RULE", "PATH_SYMMETRY_RULE",
            "NO_CONSECUTIVE_SERVICE_TASKS", "MAX_TASKS_IN_A_ROW",
            "NO_UNREACHABLE_NODES", "PATH_TO_END"
        ],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
            ActivityRules.NO_CONSECUTIVE_SERVICE_TASKS,
            ActivityRules.MAX_TASKS_IN_A_ROW,
            GatewayRules.GATEWAY_BRANCHING_RULE,
            GatewayRules.PARALLEL_GATEWAY_BEHAVIOR,
            TopologicalRules.PATH_SYMMETRY_RULE,
            TopologicalRules.NO_UNREACHABLE_NODES,
            TopologicalRules.PATH_TO_END,
        ]),
        "prompt": "Create a comprehensive order fulfillment: start → validate order (user) → parallel split (check inventory (service) AND process payment (service)) → parallel join → exclusive gateway checks results → if success: prepare shipment (user) → ship (service) → end; if failure: cancel order (user) → end"
    },
    {
        "scenario_name": "l6_loan_approval_with_loop",
        "category": "integration",
        "difficulty_level": 6,
        "test_type": "positive",
        "description": "Generate loan approval with exclusive gateways, loop for resubmission, and intermediate events",
        "rules_tested": [
            "ONE_START_EVENT", "AT_LEAST_ONE_END_EVENT",
            "EXCLUSIVE_GATEWAY_BEHAVIOR", "VALID_LOOP_STRUCTURE_RULE",
            "INTERMEDIATE_MUST_CONNECT", "PATH_SYMMETRY_RULE"
        ],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
            EventRules.INTERMEDIATE_MUST_CONNECT,
            GatewayRules.EXCLUSIVE_GATEWAY_BEHAVIOR,
            GatewayRules.GATEWAY_BRANCHING_RULE,
            TopologicalRules.VALID_LOOP_STRUCTURE_RULE,
            TopologicalRules.PATH_SYMMETRY_RULE,
        ]),
        "prompt": "Create loan approval process: start → submit application (user) → check credit (service) → decision gateway → if approved: generate offer (service) → end; if review needed: wait for docs (intermediate catch event) → re-evaluate (user) → loop back to decision gateway; if rejected: notify rejection (service) → end"
    },
    {
        "scenario_name": "l6_multi_violation_complex",
        "category": "integration",
        "difficulty_level": 6,
        "test_type": "negative",
        "description": "Generate complex process violating multiple rules (invalid)",
        "rules_tested": [
            "MAX_TASKS_IN_A_ROW", "NO_CONSECUTIVE_SERVICE_TASKS",
            "GATEWAY_BRANCHING_RULE", "PATH_SYMMETRY_RULE"
        ],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a complex process that violates MULTIPLE rules: exceed task limit, consecutive service tasks, and asymmetric gateways."
        ]),
        "prompt": "Create a deliberately invalid complex process: start → task1 (service) → task2 (service) → task3 (user) → task4 (service) → task5 (service) → split gateway → path1: end1, path2: end2 (multiple violations: consecutive service tasks, too many sequential tasks, asymmetric split)"
    },
    {
        "scenario_name": "l6_multi_path_with_events",
        "category": "integration",
        "difficulty_level": 6,
        "test_type": "positive",
        "description": "Generate multi-path process with intermediate events and proper convergence",
        "rules_tested": [
            "INTERMEDIATE_MUST_CONNECT", "PATH_SYMMETRY_RULE",
            "NO_UNREACHABLE_NODES", "GATEWAY_BRANCHING_RULE"
        ],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
            EventRules.INTERMEDIATE_MUST_CONNECT,
            GatewayRules.GATEWAY_BRANCHING_RULE,
            TopologicalRules.PATH_SYMMETRY_RULE,
            TopologicalRules.NO_UNREACHABLE_NODES,
        ]),
        "prompt": "Create a customer support escalation: start → receive ticket (user) → priority gateway (exclusive) → high priority: immediate response (user) → end; normal priority: wait for assignment (intermediate timer) → assign agent (service) → process (user) → satisfaction check gateway → if satisfied: close → end; if not: escalate (user) → manager review (user) → end"
    },
    {
        "scenario_name": "l6_mixed_violations",
        "category": "integration",
        "difficulty_level": 6,
        "test_type": "negative",
        "description": "Generate process with mixed syntax and structural violations (invalid)",
        "rules_tested": [
            "START_NO_INCOMING", "MANDATORY_ERROR_HANDLING_FOR_SCRIPTS",
            "PATH_TO_END", "GATEWAY_CANNOT_BE_BOTH"
        ],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a process with MIXED violations: loop to start event, script without error handling, dead end, and improper gateway."
        ]),
        "prompt": "Create a deliberately broken process: start → prepare (user) → transform (script task, no error handling) → gateway (multiple in, multiple out) → path1: loops back to start (invalid); path2: dead-end task with no path to end"
    },
]

