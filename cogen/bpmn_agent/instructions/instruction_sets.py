"""
Instruction Sets
Pre-configured instruction sets combining different rules for various scenarios
"""

from .rules import (
    BaseInstructions,
    BehaviorRules,
    ReasoningRules,
    EventRules,
    ActivityRules,
    GatewayRules,
    SequenceFlowRules,
    TopologicalRules,
    ValidationRules,
)


default_instructions = " ".join([
    BaseInstructions.INTRO,
    BaseInstructions.BPMN_ELEMENTS_OVERVIEW,
    BehaviorRules.PRE_CODE_GEN,
    ReasoningRules.STEP_BY_STEP_REASONING,
    BehaviorRules.POST_CODE_GEN,
    BehaviorRules.ITERATIVE_REFINEMENT,
    BehaviorRules.NEVER_FINISH_UNTIL_VALID,
    ValidationRules.VALIDATION_ORDER,
    ValidationRules.SYNTAX_VALIDATION_ERROR,
    ValidationRules.STATIC_SEMANTICS_VALIDATION_ERROR,
    ValidationRules.STRUCTURAL_VALIDATION_ERROR,
    ValidationRules.TOPOLOGICAL_VALIDATION_ERROR,
    ValidationRules.INVALID_PROCESS_SUGGESTIONS,
    ValidationRules.VALID_PROCESS,
    ValidationRules.NO_SUGGEST_IF_VALID,
])


comprehensive_instructions = " ".join([
    BaseInstructions.INTRO,
    BaseInstructions.BPMN_ELEMENTS_OVERVIEW,
    BehaviorRules.PRE_CODE_GEN,
    ReasoningRules.STEP_BY_STEP_REASONING,
    
    # Element-specific rules
    EventRules.ONE_START_EVENT,
    EventRules.AT_LEAST_ONE_END_EVENT,
    EventRules.START_NO_INCOMING,
    EventRules.END_NO_OUTGOING,
    ActivityRules.VALID_TASK_TYPES,
    ActivityRules.NO_CONSECUTIVE_SERVICE_TASKS,
    ActivityRules.MAX_TASKS_IN_A_ROW,
    ActivityRules.MANDATORY_ERROR_HANDLING_FOR_SCRIPTS,
    ActivityRules.NO_EVENT_BETWEEN_SAME_TASKS,
    GatewayRules.VALID_GATEWAY_TYPES,
    GatewayRules.GATEWAY_BRANCHING_RULE,
    GatewayRules.GATEWAY_CANNOT_BE_BOTH,
    SequenceFlowRules.ALL_OBJECTS_CONNECTED,
    SequenceFlowRules.VALID_CONNECTIONS,
    
    # Topological rules
    TopologicalRules.PATH_SYMMETRY_RULE,
    TopologicalRules.VALID_LOOP_STRUCTURE_RULE,
    TopologicalRules.NO_UNREACHABLE_NODES,
    
    # Validation
    BehaviorRules.POST_CODE_GEN,
    BehaviorRules.ITERATIVE_REFINEMENT,
    BehaviorRules.NEVER_FINISH_UNTIL_VALID,
    ValidationRules.VALIDATION_ORDER,
    ValidationRules.INVALID_PROCESS_SUGGESTIONS,
    ValidationRules.VALID_PROCESS,
    ValidationRules.NO_SUGGEST_IF_VALID,
])


structural_only_instructions = " ".join([
    BehaviorRules.PRE_CODE_GEN,
    ActivityRules.NO_CONSECUTIVE_SERVICE_TASKS,
    ActivityRules.MAX_TASKS_IN_A_ROW,
    ActivityRules.MANDATORY_ERROR_HANDLING_FOR_SCRIPTS,
    GatewayRules.GATEWAY_BRANCHING_RULE,
    ActivityRules.NO_EVENT_BETWEEN_SAME_TASKS,
    TopologicalRules.PATH_SYMMETRY_RULE,
    TopologicalRules.VALID_LOOP_STRUCTURE_RULE,
])

