"""
Assembly tools for combining BPMN element code snippets
"""

from typing import Dict, List, Any


def assemble_bpmn_code(elements: Dict[str, Dict], flows: List[Dict], process_name: str = "Generated Process") -> str:
    """
    Assemble individual BPMN element code snippets into a complete process.
    
    Args:
        elements: Dictionary mapping element_id to element data (including code)
        flows: List of flow dictionaries with source and target
        process_name: Name for the BPMN process
    
    Returns:
        Complete Python code as string
    """
    lines = []
    
    # Imports
    lines.append("from bpmn_agent.bpmn.bpmn_lang import (")
    lines.append("    Process,")
    lines.append("    StartEvent,")
    lines.append("    EndEvent,")
    lines.append("    Task,")
    lines.append("    Gateway,")
    lines.append("    IntermediateCatchEvent,")
    lines.append("    IntermediateThrowEvent,")
    lines.append("    SequenceFlow,")
    lines.append(")")
    lines.append("")
    
    # Process creation
    lines.append(f'process = Process("{process_name}")')
    lines.append("")
    
    # Add element creation code
    lines.append("# Flow Objects")
    for element_id, element_data in elements.items():
        code = element_data.get("code", "")
        if code:
            lines.append(code)
    
    lines.append("")
    lines.append("# Add elements to process")
    for element_id, element_data in elements.items():
        variable = element_data.get("variable", element_id)
        lines.append(f"process.add({variable})")
    
    lines.append("")
    lines.append("# Sequence Flows")
    for flow in flows:
        source_var = elements.get(flow["source"], {}).get("variable", flow["source"])
        target_var = elements.get(flow["target"], {}).get("variable", flow["target"])
        lines.append(f"process.add(SequenceFlow({source_var}, {target_var}))")
    
    return "\n".join(lines)


def extract_code_from_agent_output(output: str) -> str:
    """
    Extract Python code from agent output that may contain markdown or explanations.
    
    Args:
        output: Agent output string
    
    Returns:
        Extracted Python code
    """
    # Look for code blocks
    if "```python" in output:
        # Extract from markdown code block
        start = output.find("```python") + 9
        end = output.find("```", start)
        if end > start:
            return output[start:end].strip()
    elif "```" in output:
        # Generic code block
        start = output.find("```") + 3
        end = output.find("```", start)
        if end > start:
            return output[start:end].strip()
    
    # Try to extract lines that look like Python code
    lines = output.split("\n")
    code_lines = []
    for line in lines:
        stripped = line.strip()
        # Simple heuristic: lines that look like Python statements
        if (stripped.startswith(("start", "end", "task", "gateway", "intermediate", 
                                "process", "flow")) or 
            "=" in stripped):
            code_lines.append(line)
    
    if code_lines:
        return "\n".join(code_lines)
    
    # Return as-is if no patterns match
    return output.strip()


def generate_element_id(element_type: str, existing_ids: List[str]) -> str:
    """
    Generate a unique element ID.
    
    Args:
        element_type: Type of element (e.g., 'task', 'gateway')
        existing_ids: List of already used IDs
    
    Returns:
        Unique element ID
    """
    counter = 1
    while True:
        new_id = f"{element_type}{counter}"
        if new_id not in existing_ids:
            return new_id
        counter += 1


