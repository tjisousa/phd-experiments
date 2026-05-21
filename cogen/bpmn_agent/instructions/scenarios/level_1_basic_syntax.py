"""
Level 1: Basic Syntax Scenarios
Tests fundamental syntax validation rules from bpmn_lang.py:118-154 (validate_syntax)

Focus: Basic process structure, start/end events, connectivity
Difficulty: 1 (Easiest)
"""

from ..rules import (
    BaseInstructions,
    EventRules,
    SequenceFlowRules,
)


LEVEL_1_SCENARIOS = [
    {
        "scenario_name": "l1_simple_linear_process",
        "category": "syntax",
        "difficulty_level": 1,
        "test_type": "positive",
        "description": "Generate a simple linear process with proper start, task, and end events",
        "rules_tested": ["ONE_START_EVENT", "AT_LEAST_ONE_END_EVENT", "ALL_OBJECTS_CONNECTED"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
            SequenceFlowRules.ALL_OBJECTS_CONNECTED
        ]),
        "prompt": "Create a simple approval process: start → submit request (user task) → end"
    },
    {
        "scenario_name": "l1_no_start_event",
        "category": "syntax",
        "difficulty_level": 1,
        "test_type": "negative",
        "description": "Attempt to generate a process without a start event (invalid)",
        "rules_tested": ["ONE_START_EVENT"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must generate a process WITHOUT a start event to test validation."
        ]),
        "prompt": "Create a process that deliberately omits the start event and begins directly with: review document (user task) → approve (user task) → end"
    },
    {
        "scenario_name": "l1_multiple_end_events",
        "category": "syntax",
        "difficulty_level": 1,
        "test_type": "positive",
        "description": "Generate a process with multiple valid end events",
        "rules_tested": ["AT_LEAST_ONE_END_EVENT"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
        ]),
        "prompt": "Create a process with two possible outcomes: start → check eligibility (user task) → approve path ends at approval end event, reject path ends at rejection end event"
    },
    {
        "scenario_name": "l1_multiple_start_events",
        "category": "syntax",
        "difficulty_level": 1,
        "test_type": "negative",
        "description": "Attempt to generate a process with multiple start events (invalid)",
        "rules_tested": ["ONE_START_EVENT"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must generate a process WITH TWO START EVENTS to test validation."
        ]),
        "prompt": "Create a process with two start events deliberately: start event 1 → process payment, start event 2 → verify identity, both converge at finalize (user task) → end"
    },
    {
        "scenario_name": "l1_unconnected_objects",
        "category": "syntax",
        "difficulty_level": 1,
        "test_type": "negative",
        "description": "Generate a process with unconnected objects (invalid)",
        "rules_tested": ["ALL_OBJECTS_CONNECTED"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must generate a process with an UNCONNECTED task to test validation."
        ]),
        "prompt": "Create a process where one task is deliberately not connected: start → task1 (user task) → end, and also add an isolated task2 (service task) with no connections"
    },
    {
        "scenario_name": "l1_all_properly_connected",
        "category": "syntax",
        "difficulty_level": 1,
        "test_type": "positive",
        "description": "Generate a process with multiple tasks all properly connected",
        "rules_tested": ["ALL_OBJECTS_CONNECTED"],
        "expected_valid": True,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            EventRules.ONE_START_EVENT,
            EventRules.AT_LEAST_ONE_END_EVENT,
            SequenceFlowRules.ALL_OBJECTS_CONNECTED
        ]),
        "prompt": "Create an order processing workflow: start → receive order (user task) → validate order (service task) → process payment (service task) → ship order (user task) → end"
    },
    {
        "scenario_name": "l1_direct_event_to_event",
        "category": "syntax",
        "difficulty_level": 1,
        "test_type": "negative",
        "description": "Generate direct event-to-event flow without intermediate task/gateway (invalid)",
        "rules_tested": ["NO_DIRECT_EVENT_FLOWS"],
        "expected_valid": False,
        "instructions": " ".join([
            BaseInstructions.INTRO,
            "IMPORTANT: You must create a direct flow from start event to end event to test validation."
        ]),
        "prompt": "Create a minimal process with direct event-to-event connection: start event → (direct flow) → end event, with no tasks or gateways in between"
    },
]

