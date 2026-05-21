"""
Level 3: Event Rules Scenarios
Tests event-specific validation from bpmn_lang.py:156-191 (validate_event_rules)

Focus: Start/end event flow constraints, intermediate event connectivity
Difficulty: 3
"""

from ..rules import (
    BaseInstructions,
    EventRules,
)


LEVEL_3_SCENARIOS = [
    {
        "scenario_name": "l3_start_with_incoming",
        "category": "event_rules",
        "difficulty_level": 3,
        "test_type": "negative",
        "description": "Generate start event with incoming flow (invalid)",
        "rules_tested": ["START_NO_INCOMING"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a process where the start event has an INCOMING flow to test validation."
        ]),
        "prompt": "Create a process with a loop back to start: start → process task → decision gateway → if retry: flow back to start event (invalid), if done: end"
    },
    {
        "scenario_name": "l3_end_with_outgoing",
        "category": "event_rules",
        "difficulty_level": 3,
        "test_type": "negative",
        "description": "Generate end event with outgoing flow (invalid)",
        "rules_tested": ["END_NO_OUTGOING"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a process where an end event has an OUTGOING flow to test validation."
        ]),
        "prompt": "Create a process where end event incorrectly continues: start → complete task → end event → (invalid outgoing flow) → cleanup task"
    },
    {
        "scenario_name": "l3_intermediate_catch_valid",
        "category": "event_rules",
        "difficulty_level": 3,
        "test_type": "positive",
        "description": "Generate process with properly connected intermediate catch event",
        "rules_tested": ["INTERMEDIATE_MUST_CONNECT"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            EventRules.INTERMEDIATE_MUST_CONNECT,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
        ]),
        "prompt": "Create a support ticket process: start → receive ticket (user task) → wait for customer response (intermediate message catch event) → process response (user task) → end"
    },
    {
        "scenario_name": "l3_intermediate_no_incoming",
        "category": "event_rules",
        "difficulty_level": 3,
        "test_type": "negative",
        "description": "Generate intermediate event without incoming flow (invalid)",
        "rules_tested": ["INTERMEDIATE_MUST_CONNECT"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create an intermediate event with NO INCOMING flow to test validation."
        ]),
        "prompt": "Create a process with disconnected intermediate event: start → process data → intermediate timer event (with no incoming flow) → finalize → end"
    },
    {
        "scenario_name": "l3_intermediate_no_outgoing",
        "category": "event_rules",
        "difficulty_level": 3,
        "test_type": "negative",
        "description": "Generate intermediate event without outgoing flow (invalid)",
        "rules_tested": ["INTERMEDIATE_MUST_CONNECT"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create an intermediate event with NO OUTGOING flow to test validation."
        ]),
        "prompt": "Create a process with dead-end intermediate event: start → send request → wait for response (intermediate message catch event with no outgoing flow)"
    },
    {
        "scenario_name": "l3_intermediate_throw_valid",
        "category": "event_rules",
        "difficulty_level": 3,
        "test_type": "positive",
        "description": "Generate process with properly connected intermediate throw event",
        "rules_tested": ["INTERMEDIATE_MUST_CONNECT"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            EventRules.INTERMEDIATE_MUST_CONNECT,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
        ]),
        "prompt": "Create a notification workflow: start → prepare notification (user task) → send notification signal (intermediate throw event) → log completion (service task) → end"
    },
]

