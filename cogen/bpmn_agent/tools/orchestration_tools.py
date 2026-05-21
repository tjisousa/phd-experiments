"""
Orchestration tools for multi-agent BPMN system
Handles scenario parsing and error mapping
"""

import re
from typing import List, Dict, Any, Optional


def parse_scenario_to_plan(scenario_text: str) -> Dict[str, Any]:
    """
    Parse a natural language scenario into a structured BPMN plan.
    
    Args:
        scenario_text: Natural language description of the BPMN process
    
    Returns:
        Dictionary with elements and flows structure
    """
    plan = {
        "elements": [],
        "flows": [],
        "description": scenario_text
    }
    
    # Extract elements from scenario text
    # Pattern: "task_name (task_type)" or "task_name"
    # Common keywords: start, end, gateway, decision, split, merge
    
    words = scenario_text.lower()
    element_id_counter = {"task": 0, "gateway": 0, "event": 0}
    element_map = {}  # name -> id mapping
    
    # Always add start event
    start_id = "start"
    plan["elements"].append({
        "type": "start_event",
        "id": start_id,
        "name": "Start Event",
        "element_type": "StartEvent"
    })
    element_map["start"] = start_id
    
    # Parse for tasks (look for task type indicators)
    task_patterns = [
        (r"([\w\s]+)\s*\(user task\)", "user"),
        (r"([\w\s]+)\s*\(service task\)", "service"),
        (r"([\w\s]+)\s*\(script task\)", "script"),
        (r"([\w\s]+)\s*\(manual task\)", "manual"),
        (r"([\w\s]+)\s*\(user\)", "user"),
        (r"([\w\s]+)\s*\(service\)", "service"),
        (r"([\w\s]+)\s*\(script\)", "script"),
    ]
    
    for pattern, task_type in task_patterns:
        matches = re.finditer(pattern, scenario_text, re.IGNORECASE)
        for match in matches:
            task_name = match.group(1).strip()
            element_id_counter["task"] += 1
            task_id = f"task{element_id_counter['task']}"
            
            plan["elements"].append({
                "type": f"{task_type}_task",
                "id": task_id,
                "name": task_name,
                "task_type": task_type,
                "element_type": "Task"
            })
            element_map[task_name.lower()] = task_id
    
    # Parse for gateways
    gateway_keywords = ["gateway", "decision", "split", "merge", "parallel", "exclusive", "choice"]
    for keyword in gateway_keywords:
        if keyword in words:
            element_id_counter["gateway"] += 1
            gateway_id = f"gateway{element_id_counter['gateway']}"
            
            # Determine gateway type
            gateway_type = "exclusive"  # default
            if "parallel" in words:
                gateway_type = "parallel"
            elif "inclusive" in words or "or" in words:
                gateway_type = "inclusive"
            
            plan["elements"].append({
                "type": "gateway",
                "id": gateway_id,
                "name": f"{keyword.capitalize()} Gateway",
                "gateway_type": gateway_type,
                "element_type": "Gateway"
            })
            element_map[keyword] = gateway_id
    
    # Parse for intermediate events
    if "wait" in words or "timer" in words or "intermediate" in words:
        element_id_counter["event"] += 1
        event_id = f"intermediate{element_id_counter['event']}"
        
        event_type = "timer" if "timer" in words or "wait" in words else "message"
        
        plan["elements"].append({
            "type": "intermediate_catch_event",
            "id": event_id,
            "name": "Intermediate Event",
            "event_type": event_type,
            "element_type": "IntermediateCatchEvent"
        })
        element_map["intermediate"] = event_id
    
    # Always add end event
    end_id = "end"
    plan["elements"].append({
        "type": "end_event",
        "id": end_id,
        "name": "End Event",
        "element_type": "EndEvent"
    })
    element_map["end"] = end_id
    
    # Generate flows (simple sequential flow for now)
    for i in range(len(plan["elements"]) - 1):
        plan["flows"].append({
            "source": plan["elements"][i]["id"],
            "target": plan["elements"][i + 1]["id"]
        })
    
    return plan


def map_validation_errors_to_elements(validation_output: str, elements: List[Dict]) -> Dict[str, List[str]]:
    """
    Map validation errors to specific BPMN elements.
    
    Args:
        validation_output: The validation output string from validate_process
        elements: List of element dictionaries with id and type
    
    Returns:
        Dictionary mapping element_id to list of error messages
    """
    error_map = {}
    
    # Parse validation output for errors
    lines = validation_output.split("\n")
    
    for line in lines:
        if "Error" in line:
            # Try to extract element ID or name from error message
            # Pattern: "Object 'name' (ID: id)"
            id_match = re.search(r"\(ID:\s*([^\)]+)\)", line)
            name_match = re.search(r"Object '([^']+)'", line)
            task_match = re.search(r"task '([^']+)'", line, re.IGNORECASE)
            gateway_match = re.search(r"gateway '([^']+)'", line, re.IGNORECASE)
            event_match = re.search(r"event '([^']+)'", line, re.IGNORECASE)
            
            element_id = None
            
            if id_match:
                element_id = id_match.group(1).strip()
            elif name_match:
                # Find element by name
                name = name_match.group(1).strip()
                for elem in elements:
                    if elem.get("name") == name or elem.get("id") == name:
                        element_id = elem["id"]
                        break
            elif task_match or gateway_match or event_match:
                match = task_match or gateway_match or event_match
                name = match.group(1).strip()
                for elem in elements:
                    if elem.get("name") == name or elem.get("id") == name:
                        element_id = elem["id"]
                        break
            
            # Categorize by error type if no specific element found
            if not element_id:
                if "Start" in line or "StartEvent" in line:
                    element_id = "start"
                elif "End" in line or "EndEvent" in line:
                    element_id = "end"
                elif "Gateway" in line:
                    # Find first gateway
                    for elem in elements:
                        if elem.get("element_type") == "Gateway":
                            element_id = elem["id"]
                            break
                elif "Task" in line or "service" in line or "user" in line:
                    # Generic task error - might need refinement
                    element_id = "tasks_general"
            
            if element_id:
                if element_id not in error_map:
                    error_map[element_id] = []
                error_map[element_id].append(line.strip())
    
    return error_map


def get_element_agent_type(element_type: str) -> str:
    """
    Map element type to responsible agent type.
    
    Args:
        element_type: BPMN element type
    
    Returns:
        Agent type name
    """
    mapping = {
        "StartEvent": "start_event",
        "EndEvent": "end_event",
        "Task": "task",
        "Gateway": "gateway",
        "IntermediateCatchEvent": "intermediate_event",
        "IntermediateThrowEvent": "intermediate_event",
    }
    return mapping.get(element_type, "unknown")


