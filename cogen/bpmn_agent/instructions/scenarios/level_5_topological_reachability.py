"""
Level 5: Topological and Reachability Scenarios
Tests topology and reachability from bpmn_lang.py:258-353 (validate_topological_rules & validate_reachability)

Focus: Loops, path symmetry, reachability, dead ends
Difficulty: 5
"""

from ..rules import (
    BaseInstructions,
    EventRules,
    GatewayRules,
    TopologicalRules,
)


LEVEL_5_SCENARIOS = [
    {
        "scenario_name": "l5_valid_loop_with_task",
        "category": "topological",
        "difficulty_level": 5,
        "test_type": "positive",
        "description": "Generate valid loop structure with task and exit path",
        "rules_tested": ["VALID_LOOP_STRUCTURE_RULE"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            TopologicalRules.VALID_LOOP_STRUCTURE_RULE,
            GatewayRules.GATEWAY_BRANCHING_RULE,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
        ]),
        "prompt": "Create a retry mechanism: start → attempt task (user) → check result gateway (exclusive) → if success: exit to end; if failure: loop back to attempt task (max 3 retries implied by exit path)"
    },
    {
        "scenario_name": "l5_loop_without_task",
        "category": "topological",
        "difficulty_level": 5,
        "test_type": "negative",
        "description": "Generate loop without any tasks (invalid)",
        "rules_tested": ["VALID_LOOP_STRUCTURE_RULE"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a loop that contains NO tasks, only gateways."
        ]),
        "prompt": "Create a process with an empty loop: start → task1 → gateway1 splits → gateway2 loops back to gateway1 (no task in loop) → other path to end"
    },
    {
        "scenario_name": "l5_infinite_loop",
        "category": "topological",
        "difficulty_level": 5,
        "test_type": "negative",
        "description": "Generate loop without exit path (infinite loop, invalid)",
        "rules_tested": ["VALID_LOOP_STRUCTURE_RULE"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a loop with NO exit path to test validation."
        ]),
        "prompt": "Create a process with infinite loop: start → process task → check gateway always loops back to process task with no exit path to end"
    },
    {
        "scenario_name": "l5_path_symmetry_valid",
        "category": "topological",
        "difficulty_level": 5,
        "test_type": "positive",
        "description": "Generate splitting gateway with corresponding joining gateway",
        "rules_tested": ["PATH_SYMMETRY_RULE"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            TopologicalRules.PATH_SYMMETRY_RULE,
            GatewayRules.GATEWAY_BRANCHING_RULE,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
        ]),
        "prompt": "Create a symmetric branching process: start → split gateway (exclusive) → path1: approve task, path2: reject task → join gateway (exclusive) → notify (service) → end"
    },
    {
        "scenario_name": "l5_split_without_join",
        "category": "topological",
        "difficulty_level": 5,
        "test_type": "negative",
        "description": "Generate splitting gateway without corresponding joining gateway (invalid)",
        "rules_tested": ["PATH_SYMMETRY_RULE"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a splitting gateway where paths do NOT converge at a joining gateway."
        ]),
        "prompt": "Create asymmetric process: start → split gateway → path1: task1 → end1, path2: task2 → end2 (no joining gateway, paths diverge to separate ends)"
    },
    {
        "scenario_name": "l5_all_reachable",
        "category": "topological",
        "difficulty_level": 5,
        "test_type": "positive",
        "description": "Generate complex process with all nodes reachable from start",
        "rules_tested": ["NO_UNREACHABLE_NODES"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            TopologicalRules.NO_UNREACHABLE_NODES,
            TopologicalRules.PATH_TO_END,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
        ]),
        "prompt": "Create a comprehensive order workflow: start → receive order → parallel split (process payment AND prepare shipment) → join → quality check gateway → if pass: ship → end; if fail: return to prepare shipment"
    },
    {
        "scenario_name": "l5_unreachable_node",
        "category": "topological",
        "difficulty_level": 5,
        "test_type": "negative",
        "description": "Generate process with unreachable node (invalid)",
        "rules_tested": ["NO_UNREACHABLE_NODES"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a task that is NOT reachable from the start event."
        ]),
        "prompt": "Create a process with isolated task: start → task1 → end, and separately add task2 → task3 (not connected to start, making them unreachable)"
    },
    {
        "scenario_name": "l5_dead_end_path",
        "category": "topological",
        "difficulty_level": 5,
        "test_type": "negative",
        "description": "Generate process with path that cannot reach end (dead end, invalid)",
        "rules_tested": ["PATH_TO_END"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a task that has NO path to any end event."
        ]),
        "prompt": "Create a process with dead end: start → gateway splits → path1: task1 → end; path2: task2 (no connection to end, creating a dead end)"
    },
]

