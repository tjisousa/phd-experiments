"""
BPMN process management tools.
Supports BPMN 2.0.2 elements.
"""

import io
import sys
from ..bpmn.bpmn_lang import (
    Process,
    StartEvent,
    EndEvent,
    Task,
    Gateway,
    IntermediateCatchEvent,
    IntermediateThrowEvent,
    SequenceFlow,
    DataObject,
    DataStore,
)


def run_process_code(code: str) -> Process:
    """Executes the provided code and returns the 'process' object defined within it.

    Args:
        code (str): Python code that defines a BPMN process and assigns it to a variable named 'process'.

    Returns:
        Process: The BPMN Process object created by the executed code.
    """
    # Rewrite imports if needed for user-provided snippets
    code = code.replace("from bpmn_lang import", "from bpmn_agent.bpmn.bpmn_lang import")
    code = code.replace("from bpmn.bpmn_lang import", "from bpmn_agent.bpmn.bpmn_lang import")
    local_vars = {}
    exec(
        code,
        {
            "Process": Process,
            "StartEvent": StartEvent,
            "EndEvent": EndEvent,
            "Task": Task,
            "Gateway": Gateway,
            "IntermediateCatchEvent": IntermediateCatchEvent,
            "IntermediateThrowEvent": IntermediateThrowEvent,
            "SequenceFlow": SequenceFlow,
            "DataObject": DataObject,
            "DataStore": DataStore,
        },
        local_vars,
    )
    return local_vars["process"]


def validate_process(code: str) -> dict:
    """Validates a BPMN process defined in the provided code string.

    Args:
        code (str): Python code that defines a BPMN process and assigns it to a variable named 'process'.

    Returns:
        dict: status, validation result, and output or error message.
    """
    try:
        process = run_process_code(code)
        buf = io.StringIO()
        sys.stdout = buf
        valid = process.validate()
        sys.stdout = sys.__stdout__
        return {"status": "success", "valid": valid, "output": buf.getvalue()}
    except Exception as e:
        sys.stdout = sys.__stdout__
        return {"status": "error", "error_message": str(e)}


def suggest_improvements(code: str) -> dict:
    """Suggests improvements for a BPMN process defined in the provided code string.

    Args:
        code (str): Python code that defines a BPMN process and assigns it to a variable named 'process'.

    Returns:
        dict: status and suggestions or error message.
    """
    try:
        process = run_process_code(code)
        buf = io.StringIO()
        sys.stdout = buf
        process.suggest_improvements()
        sys.stdout = sys.__stdout__
        return {"status": "success", "suggestions": buf.getvalue()}
    except Exception as e:
        sys.stdout = sys.__stdout__
        return {"status": "error", "error_message": str(e)}
