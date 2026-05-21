"""
Utility tools for BPMN agent operations.
"""


def get_bpmn_examples() -> dict:
    """
    Provides comprehensive example BPMN process code snippets using the bpmn_lang.py language.
    
    Examples cover all major BPMN element types and patterns:
    - Simple linear processes
    - Exclusive gateways (XOR decision points)
    - Parallel gateways (AND concurrent execution)
    - Script tasks with error handling
    - Inclusive gateways (OR one or more paths)
    - Complex multi-gateway processes
    - Anti-patterns (intentionally invalid examples showing common mistakes)

    Returns:
        dict: status and a list of 8 example code strings (6 valid, 2 anti-patterns).
    """
    examples = [
        '''
# Example 1: Simple Linear Process (VALID)
# Demonstrates: Basic process structure with user and service tasks
# Rules followed: ONE_START_EVENT, AT_LEAST_ONE_END_EVENT, ALL_OBJECTS_CONNECTED
from bpmn_agent.bpmn.bpmn_lang import Process, StartEvent, EndEvent, Task, SequenceFlow

p = Process("Simple Approval Process")
start = StartEvent("start", "Start")
t1 = Task("task1", "Submit Request", "user")
t2 = Task("task2", "Validate Request", "service")
t3 = Task("task3", "Review Application", "user")
end = EndEvent("end", "End")

p.add(start)
p.add(t1)
p.add(t2)
p.add(t3)
p.add(end)

p.add(SequenceFlow(start, t1))
p.add(SequenceFlow(t1, t2))
p.add(SequenceFlow(t2, t3))
p.add(SequenceFlow(t3, end))
''',
        '''
# Example 2: Exclusive Gateway (XOR) - Decision Process (VALID)
# Demonstrates: Branching and merging with exclusive gateway
# Rules followed: GATEWAY_BRANCHING_RULE, PATH_SYMMETRY_RULE, EXCLUSIVE_GATEWAY_BEHAVIOR
from bpmn_agent.bpmn.bpmn_lang import Process, StartEvent, EndEvent, Task, Gateway, SequenceFlow

p = Process("Loan Approval Process")
start = StartEvent("start", "Start")
t1 = Task("task1", "Submit Application", "user")
t2 = Task("task2", "Check Credit Score", "service")
gw1 = Gateway("gw1", "Credit Decision", "exclusive")  # Splitting gateway
t3 = Task("task3", "Approve Loan", "user")
t4 = Task("task4", "Reject Application", "user")
gw2 = Gateway("gw2", "Merge", "exclusive")  # Joining gateway
t5 = Task("task5", "Notify Customer", "service")
end = EndEvent("end", "End")

p.add(start)
p.add(t1)
p.add(t2)
p.add(gw1)
p.add(t3)
p.add(t4)
p.add(gw2)
p.add(t5)
p.add(end)

# Main flow
p.add(SequenceFlow(start, t1))
p.add(SequenceFlow(t1, t2))
p.add(SequenceFlow(t2, gw1))
# Branching paths
p.add(SequenceFlow(gw1, t3))  # Good credit path
p.add(SequenceFlow(gw1, t4))  # Bad credit path
# Merging paths
p.add(SequenceFlow(t3, gw2))
p.add(SequenceFlow(t4, gw2))
# Continue after merge
p.add(SequenceFlow(gw2, t5))
p.add(SequenceFlow(t5, end))
''',
        '''
# Example 3: Parallel Gateway (AND) - Concurrent Execution (VALID)
# Demonstrates: Parallel execution of tasks that must all complete
# Rules followed: PARALLEL_GATEWAY_BEHAVIOR, PATH_SYMMETRY_RULE
from bpmn_agent.bpmn.bpmn_lang import Process, StartEvent, EndEvent, Task, Gateway, SequenceFlow

p = Process("Order Fulfillment Process")
start = StartEvent("start", "Start")
t1 = Task("task1", "Receive Order", "user")
gw1 = Gateway("gw1", "Parallel Split", "parallel")  # Splitting gateway
t2 = Task("task2", "Prepare Shipment", "service")
t3 = Task("task3", "Generate Invoice", "service")
t4 = Task("task4", "Update Inventory", "service")
gw2 = Gateway("gw2", "Parallel Join", "parallel")  # Joining gateway
t5 = Task("task5", "Send Notification", "user")
end = EndEvent("end", "End")

p.add(start)
p.add(t1)
p.add(gw1)
p.add(t2)
p.add(t3)
p.add(t4)
p.add(gw2)
p.add(t5)
p.add(end)

# Main flow
p.add(SequenceFlow(start, t1))
p.add(SequenceFlow(t1, gw1))
# Three parallel paths
p.add(SequenceFlow(gw1, t2))
p.add(SequenceFlow(gw1, t3))
p.add(SequenceFlow(gw1, t4))
# All paths converge
p.add(SequenceFlow(t2, gw2))
p.add(SequenceFlow(t3, gw2))
p.add(SequenceFlow(t4, gw2))
# Continue after join
p.add(SequenceFlow(gw2, t5))
p.add(SequenceFlow(t5, end))
''',
        '''
# Example 4: Script Task with Error Handling (VALID)
# Demonstrates: Mandatory error handling for script tasks
# Rules followed: MANDATORY_ERROR_HANDLING_FOR_SCRIPTS
from bpmn_agent.bpmn.bpmn_lang import Process, StartEvent, EndEvent, Task, Gateway, SequenceFlow

p = Process("Data Processing Workflow")
start = StartEvent("start", "Start")
t1 = Task("task1", "Load Data", "user")
t2 = Task("task2", "Transform Data", "script")  # Script task
gw1 = Gateway("gw1", "Check Result", "exclusive")  # Error handling gateway (required!)
t3 = Task("task3", "Save Results", "service")
t4 = Task("task4", "Log Error", "user")
gw2 = Gateway("gw2", "Merge", "exclusive")
end = EndEvent("end", "End")

p.add(start)
p.add(t1)
p.add(t2)
p.add(gw1)
p.add(t3)
p.add(t4)
p.add(gw2)
p.add(end)

p.add(SequenceFlow(start, t1))
p.add(SequenceFlow(t1, t2))
p.add(SequenceFlow(t2, gw1))  # Script task MUST be followed by gateway
# Error handling paths
p.add(SequenceFlow(gw1, t3))  # Success path
p.add(SequenceFlow(gw1, t4))  # Error path
# Merge and end
p.add(SequenceFlow(t3, gw2))
p.add(SequenceFlow(t4, gw2))
p.add(SequenceFlow(gw2, end))
''',
        '''
# Example 5: Complex Multi-Gateway Process (VALID)
# Demonstrates: Multiple decision points with proper path convergence
from bpmn_agent.bpmn.bpmn_lang import Process, StartEvent, EndEvent, Task, Gateway, SequenceFlow

p = Process("Expense Approval Process")
start = StartEvent("start", "Start")
t1 = Task("task1", "Submit Expense", "user")
gw1 = Gateway("gw1", "Amount Check", "exclusive")
t2 = Task("task2", "Auto Approve", "service")
t3 = Task("task3", "Manager Review", "user")
gw2 = Gateway("gw2", "Manager Decision", "exclusive")
t4 = Task("task4", "Approve", "user")
t5 = Task("task5", "Reject", "user")
gw3 = Gateway("gw3", "Merge All", "exclusive")  # Merges all paths
t6 = Task("task6", "Notify Employee", "service")
end = EndEvent("end", "End")

p.add(start)
p.add(t1)
p.add(gw1)
p.add(t2)
p.add(t3)
p.add(gw2)
p.add(t4)
p.add(t5)
p.add(gw3)
p.add(t6)
p.add(end)

p.add(SequenceFlow(start, t1))
p.add(SequenceFlow(t1, gw1))
# First branch: amount-based
p.add(SequenceFlow(gw1, t2))  # < $100
p.add(SequenceFlow(gw1, t3))  # >= $100
# Second branch: manager decision
p.add(SequenceFlow(t3, gw2))
p.add(SequenceFlow(gw2, t4))  # Approved
p.add(SequenceFlow(gw2, t5))  # Rejected
# Merge all paths
p.add(SequenceFlow(t2, gw3))
p.add(SequenceFlow(t4, gw3))
p.add(SequenceFlow(t5, gw3))
# Final notification
p.add(SequenceFlow(gw3, t6))
p.add(SequenceFlow(t6, end))
''',
        '''
# Example 6: ANTI-PATTERN - Consecutive Service Tasks (INVALID)
# This violates: NO_CONSECUTIVE_SERVICE_TASKS
# Use this to understand what NOT to do
from bpmn_agent.bpmn.bpmn_lang import Process, StartEvent, EndEvent, Task, SequenceFlow

p = Process("Invalid - Consecutive Service Tasks")
start = StartEvent("start", "Start")
t1 = Task("task1", "Call API", "service")
t2 = Task("task2", "Process Response", "service")  # ERROR: service after service!
end = EndEvent("end", "End")

p.add(start)
p.add(t1)
p.add(t2)
p.add(end)

p.add(SequenceFlow(start, t1))
p.add(SequenceFlow(t1, t2))  # This will fail validation
p.add(SequenceFlow(t2, end))

# FIX: Insert a user or script task between them, or use a gateway
''',
        '''
# Example 7: ANTI-PATTERN - Script Task Without Gateway (INVALID)
# This violates: MANDATORY_ERROR_HANDLING_FOR_SCRIPTS
from bpmn_agent.bpmn.bpmn_lang import Process, StartEvent, EndEvent, Task, SequenceFlow

p = Process("Invalid - Script Without Error Handling")
start = StartEvent("start", "Start")
t1 = Task("task1", "Run Validation", "script")
t2 = Task("task2", "Continue", "user")  # ERROR: script not followed by gateway!
end = EndEvent("end", "End")

p.add(start)
p.add(t1)
p.add(t2)
p.add(end)

p.add(SequenceFlow(start, t1))
p.add(SequenceFlow(t1, t2))  # This will fail validation
p.add(SequenceFlow(t2, end))

# FIX: Add a gateway after the script task for error handling
''',
        '''
# Example 8: Inclusive Gateway (OR) - One or More Paths (VALID)
# Demonstrates: Inclusive gateway where one or more paths can be taken
from bpmn_agent.bpmn.bpmn_lang import Process, StartEvent, EndEvent, Task, Gateway, SequenceFlow

p = Process("Multi-Channel Notification Process")
start = StartEvent("start", "Start")
t1 = Task("task1", "Process Event", "service")
gw1 = Gateway("gw1", "Notification Channels", "inclusive")  # Splitting OR gateway
t2 = Task("task2", "Send Email", "send")
t3 = Task("task3", "Send SMS", "send")
t4 = Task("task4", "Send Push Notification", "send")
gw2 = Gateway("gw2", "Wait for All", "inclusive")  # Joining OR gateway
t5 = Task("task5", "Log Notifications", "service")
end = EndEvent("end", "End")

p.add(start)
p.add(t1)
p.add(gw1)
p.add(t2)
p.add(t3)
p.add(t4)
p.add(gw2)
p.add(t5)
p.add(end)

p.add(SequenceFlow(start, t1))
p.add(SequenceFlow(t1, gw1))
# Multiple paths (one or more can be taken)
p.add(SequenceFlow(gw1, t2))
p.add(SequenceFlow(gw1, t3))
p.add(SequenceFlow(gw1, t4))
# Join the active paths
p.add(SequenceFlow(t2, gw2))
p.add(SequenceFlow(t3, gw2))
p.add(SequenceFlow(t4, gw2))
# Continue
p.add(SequenceFlow(gw2, t5))
p.add(SequenceFlow(t5, end))
'''
    ]
    return {"status": "success", "examples": examples}
