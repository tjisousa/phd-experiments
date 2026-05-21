"""
Optimization Rules
Rules for improving the quality and efficiency of BPMN processes
"""


class OptimizationRules:
    """Rules for improving the quality and efficiency of BPMN processes"""
    PARALLELIZE_INDEPENDENT_TASKS = (
        "For maximum efficiency, if a process describes tasks that are not dependent on each other's outputs, "
        "you should use a ParallelGateway to execute them concurrently. Do not model independent tasks in a purely sequential way."
    )
    
    REMOVE_REDUNDANT_STEPS = (
        "Analyze the user's request for logical redundancy. If the user describes a step that is "
        "superfluous or can be combined with another (e.g., 'approve request' followed by 'mark request as approved'), "
        "consolidate them into a single, meaningful task."
    )

