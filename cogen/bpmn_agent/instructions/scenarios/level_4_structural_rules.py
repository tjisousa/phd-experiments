"""
Level 4: Structural Rules Scenarios
Tests structural constraints from bpmn_lang.py:193-256 (validate_structural_rules & validate_advanced_structural_rules)

Focus: Task sequencing limits, service task constraints, script error handling, gateway constraints
Difficulty: 4
"""

from ..rules import (
    BaseInstructions,
    EventRules,
    ActivityRules,
    GatewayRules,
    TopologicalRules,
)


LEVEL_4_SCENARIOS = [
    {
        "scenario_name": "l4_exceed_max_tasks",
        "category": "structural",
        "difficulty_level": 4,
        "test_type": "negative",
        "description": "Generate process with 5+ consecutive tasks (exceeds limit, invalid)",
        "rules_tested": ["MAX_TASKS_IN_A_ROW"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a sequence of FIVE or more consecutive tasks to test the limit."
        ]),
        "prompt": "Create a document processing workflow with too many sequential tasks: start → scan (user) → extract (service) → validate (user) → format (service) → archive (user) → end (this violates the 4-task limit)"
    },
    {
        "scenario_name": "l4_max_tasks_at_limit",
        "category": "structural",
        "difficulty_level": 4,
        "test_type": "positive",
        "description": "Generate process with exactly 4 consecutive tasks (at limit, valid)",
        "rules_tested": ["MAX_TASKS_IN_A_ROW"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            ActivityRules.MAX_TASKS_IN_A_ROW,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
        ]),
        "prompt": "Create a data pipeline with exactly 4 sequential tasks: start → collect data (service) → transform data (service) → validate data (user) → store data (service) → end"
    },
    {
        "scenario_name": "l4_consecutive_service_tasks",
        "category": "structural",
        "difficulty_level": 4,
        "test_type": "negative",
        "description": "Generate consecutive service tasks (invalid)",
        "rules_tested": ["NO_CONSECUTIVE_SERVICE_TASKS"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create TWO consecutive service tasks to test validation."
        ]),
        "prompt": "Create an API workflow with consecutive service tasks: start → call API 1 (service task) → call API 2 (service task) → end"
    },
    {
        "scenario_name": "l4_alternating_task_types",
        "category": "structural",
        "difficulty_level": 4,
        "test_type": "positive",
        "description": "Generate process with properly alternating task types",
        "rules_tested": ["NO_CONSECUTIVE_SERVICE_TASKS"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            ActivityRules.NO_CONSECUTIVE_SERVICE_TASKS,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
        ]),
        "prompt": "Create a balanced workflow: start → gather requirements (user) → process data (service) → review results (user) → generate report (service) → end"
    },
    {
        "scenario_name": "l4_script_without_error_handling",
        "category": "structural",
        "difficulty_level": 4,
        "test_type": "negative",
        "description": "Generate script task without mandatory error handling gateway (invalid)",
        "rules_tested": ["MANDATORY_ERROR_HANDLING_FOR_SCRIPTS"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a script task NOT followed by a gateway to test validation."
        ]),
        "prompt": "Create a process with script task but no error handling: start → prepare data (user) → run transformation script (script task) → save results (service) → end"
    },
    {
        "scenario_name": "l4_script_with_error_handling",
        "category": "structural",
        "difficulty_level": 4,
        "test_type": "positive",
        "description": "Generate script task with proper error handling gateway",
        "rules_tested": ["MANDATORY_ERROR_HANDLING_FOR_SCRIPTS"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            ActivityRules.MANDATORY_ERROR_HANDLING_FOR_SCRIPTS,
            GatewayRules.GATEWAY_BRANCHING_RULE,
            TopologicalRules.PATH_SYMMETRY_RULE,
        ]),
        "prompt": "Create a data processing workflow: start → load data (user) → transform data (script) → error check gateway (exclusive) → if success: save (service) → end; if error: log error (user) → end"
    },
    {
        "scenario_name": "l4_redundant_gateway",
        "category": "structural",
        "difficulty_level": 4,
        "test_type": "negative",
        "description": "Generate redundant gateway with one incoming and one outgoing (invalid)",
        "rules_tested": ["GATEWAY_BRANCHING_RULE"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a gateway with ONLY one incoming and one outgoing flow to test validation."
        ]),
        "prompt": "Create a process with redundant gateway: start → task1 → redundant gateway (1 in, 1 out) → task2 → end"
    },
    {
        "scenario_name": "l4_gateway_split_and_join",
        "category": "structural",
        "difficulty_level": 4,
        "test_type": "negative",
        "description": "Generate gateway that both splits and joins (multiple in, multiple out - invalid)",
        "rules_tested": ["GATEWAY_CANNOT_BE_BOTH"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a single gateway with MULTIPLE incoming AND MULTIPLE outgoing flows to test validation."
        ]),
        "prompt": "Create a process with a gateway that splits and joins: task1 and task2 both flow into gateway → gateway outputs to task3 and task4 (this violates the rule requiring separate split/join gateways)"
    },
]

