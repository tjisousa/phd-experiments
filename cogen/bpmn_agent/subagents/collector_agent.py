"""
Collector Agent
Assembles BPMN code from subagent outputs and validates the complete process
"""

from google.adk.agents import BaseAgent
from ..tools.assembly_tools import assemble_bpmn_code, extract_code_from_agent_output
from ..tools.process_tools import validate_process
from ..tools.orchestration_tools import map_validation_errors_to_elements


class CollectorAgent(BaseAgent):
    """
    Collector Agent that assembles all BPMN elements and validates the process.
    """
    
    def __init__(self):
        super().__init__(
            name="CollectorAgent",
            description=(
                "I assemble BPMN code from all subagent outputs and validate the complete process. "
                "I identify any validation errors and map them to specific elements."
            )
        )
    
    async def _run_async_impl(self, ctx):
        """
        Assemble and validate BPMN process.
        """
        # Get scenario plan
        scenario_plan = ctx.session.state.get("scenario_plan", {})
        
        # Get all elements from session state
        elements = ctx.session.state.get("elements", {})
        
        if not elements:
            ctx.session.state["collector_error"] = "No elements found in session state"
            return
            yield  # Make this an async generator
        
        # Extract and clean code from each element
        cleaned_elements = {}
        for elem_id, elem_data in elements.items():
            if isinstance(elem_data, dict) and "code" in elem_data:
                code = elem_data["code"]
                if isinstance(code, str):
                    cleaned_code = extract_code_from_agent_output(code)
                    cleaned_elements[elem_id] = {
                        **elem_data,
                        "code": cleaned_code
                    }
                else:
                    cleaned_elements[elem_id] = elem_data
            else:
                cleaned_elements[elem_id] = elem_data
        
        # Get flows from scenario plan
        flows = scenario_plan.get("plan", {}).get("flows", [])
        
        # Assemble complete BPMN code
        process_name = scenario_plan.get("description", "Generated Process")[:50]
        full_code = assemble_bpmn_code(cleaned_elements, flows, process_name)
        
        # Store the assembled code
        ctx.session.state["assembled_code"] = full_code
        
        # Validate the process
        validation_result = validate_process(full_code)
        
        # Store validation result
        ctx.session.state["validation_result"] = validation_result
        ctx.session.state["is_valid"] = validation_result.get("valid", False)
        
        # If validation failed, map errors to elements
        if not validation_result.get("valid", False):
            validation_output = validation_result.get("output", "")
            element_list = [
                {"id": elem_id, **elem_data} 
                for elem_id, elem_data in cleaned_elements.items()
            ]
            error_map = map_validation_errors_to_elements(validation_output, element_list)
            ctx.session.state["error_map"] = error_map
            ctx.session.state["collector_status"] = "validation_failed"
        else:
            # Validation passed
            ctx.session.state["final_bpmn"] = full_code
            ctx.session.state["collector_status"] = "success"
        
        return
        yield  # Make this an async generator

