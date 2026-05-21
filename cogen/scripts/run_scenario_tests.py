"""
Automated BPMN Agent Scenario Testing Script

This script automates testing of the BPMN agent across different scenarios,
tracks performance metrics, and documents results.

Usage:
    python run_scenario_tests.py --scenario simple_linear_process
    python run_scenario_tests.py --category positive
    python run_scenario_tests.py --all
    python run_scenario_tests.py --list
"""

import asyncio
import argparse
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from bpmn_agent.agent import root_agent
from bpmn_agent.instructions import (
    get_scenarios_by_category,
    get_scenarios_by_validation_category,
    get_scenarios_by_difficulty_level,
    get_scenarios_by_test_type,
    get_all_scenarios,
)


class ScenarioTestRunner:
    """Manages automated testing of BPMN agent scenarios"""
    
    def __init__(self, verbose: bool = True, run_id: Optional[str] = None):
        self.verbose = verbose
        self.session_service = None
        self.runner = None
        self.results = []
        # Generate run ID if not provided: model_name_timestamp
        self.run_id = run_id or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.model_name = None
        self.tools_used = []
        
    async def initialize(self):
        """Initialize the session service and runner"""
        self.session_service = InMemorySessionService()
        await self.session_service.create_session(
            app_name="bpmn_test_app",
            user_id="test_user",
            session_id="test_session"
        )
        self.runner = Runner(
            agent=root_agent,
            app_name="bpmn_test_app",
            session_service=self.session_service
        )
        
        # Extract model and tools information
        # Handle both string model names and model objects (like LiteLlm)
        model_obj = getattr(root_agent, 'model', None)
        if model_obj is None:
            # Fallback to configuration when the agent wrapper doesn't expose .model
            try:
                from bpmn_agent.config import MODEL as CFG_MODEL
                model_obj = CFG_MODEL
            except Exception:
                model_obj = None
        if isinstance(model_obj, str):
            self.model_name = model_obj
        elif hasattr(model_obj, 'model'):
            # For LiteLlm and similar objects with a 'model' attribute
            self.model_name = model_obj.model
        else:
            # Fallback to string representation
            self.model_name = str(model_obj)
        
        self.tools_used = [tool.__name__ if hasattr(tool, '__name__') else str(tool) 
                          for tool in root_agent.tools] if hasattr(root_agent, 'tools') else []
        
        # Update run_id to include model name if not custom
        if self.run_id.startswith("run_"):
            # Clean model name for filename
            clean_model_name = self.model_name.replace("/", "_").replace(":", "_").replace("-", "_")
            self.run_id = f"{clean_model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if self.verbose:
            print("✓ Test runner initialized")
            print(f"  Model: {self.model_name}")
            print(f"  Tools: {', '.join(self.tools_used)}")
            print(f"  Run ID: {self.run_id}")
    
    async def run_scenario(
        self,
        scenario: Dict[str, Any],
        include_scenario_instructions: bool = True,
        custom_prompt: Optional[str] = None,
        max_iterations: int = 25,
        scenario_number: Optional[int] = None,
        total_scenarios: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run a single scenario test
        
        Args:
            scenario: Scenario dictionary with 'scenario_name', 'prompt', 'instructions', etc.
            include_scenario_instructions: Whether to append scenario instructions to the prompt
            custom_prompt: Optional custom prompt to override the scenario's default prompt
            max_iterations: Maximum number of agent iterations before stopping (default: 25)
            scenario_number: Optional scenario number for logging (e.g., 1, 2, 3...)
            total_scenarios: Optional total number of scenarios for logging (e.g., 10)
        
        Returns:
            Dictionary with test results and metrics
        """
        scenario_name = scenario.get("scenario_name", "unknown")
        start_time = time.time()
        
        if self.verbose:
            # Enhanced header with scenario number and model info
            scenario_info = f"Scenario {scenario_number}/{total_scenarios}" if scenario_number and total_scenarios else "Scenario"
            model_info = f"Model: {self.model_name}" if self.model_name else "Model: Unknown"
            
            print(f"\n{'='*80}")
            print(f"{scenario_info}: {scenario_name}")
            print(f"{model_info}")
            print(f"{'='*80}")
            print(f"Description: {scenario.get('description', 'N/A')}")
            print(f"Expected Valid: {scenario.get('expected_valid', 'N/A')}")
            print(f"Rules Tested: {', '.join(scenario.get('rules_tested', []))}")
            print(f"{'='*80}\n")
        
        # Construct the query
        base_prompt = custom_prompt or scenario.get("prompt", "")
        
        if include_scenario_instructions:
            instructions_text = scenario.get("instructions", "")
            full_query = f"{instructions_text}\n\n{base_prompt}"
        else:
            full_query = base_prompt
        
        if self.verbose:
            print(f"Sending prompt to agent...")
            print(f"\n--- Full Prompt ---")
            print(full_query)
            print(f"--- End Prompt ---\n")
        
        # Track conversation
        conversation = []
        final_response = ""
        token_count_estimate = 0
        iteration_count = 0
        validation_retry_count = 0
        
        try:
            # Send the query to the agent
            async for event in self.runner.run_async(
                user_id="test_user",
                session_id="test_session",
                new_message=genai_types.Content(
                    role="user",
                    parts=[genai_types.Part.from_text(text=full_query)]
                ),
            ):
                # Capture all responses (including intermediate ones with function calls)
                if event.content and event.content.parts:
                    iteration_count += 1  # Count each event as an iteration
                    
                    # Check if we've hit the iteration limit
                    if iteration_count > max_iterations:
                        if self.verbose:
                            scenario_context = f"[{scenario_number}/{total_scenarios}]" if scenario_number and total_scenarios else ""
                            model_context = f"({self.model_name})" if self.model_name else ""
                            print(f"\n⚠️  ITERATION LIMIT REACHED ({max_iterations}) - Stopping {scenario_name} {scenario_context} {model_context}")
                        break
                    
                    if self.verbose:
                        # Enhanced iteration header with scenario and model context
                        scenario_context = f"[{scenario_number}/{total_scenarios}]" if scenario_number and total_scenarios else ""
                        model_context = f"({self.model_name})" if self.model_name else ""
                        print(f"\n--- {scenario_name} {scenario_context} {model_context} - Iteration {iteration_count}/{max_iterations} ---")
                        print(f"Is Final: {event.is_final_response()}")
                        print(f"Parts ({len(event.content.parts)}):")
                        
                    for idx, part in enumerate(event.content.parts, 1):
                        # Handle text parts
                        if hasattr(part, 'text') and part.text:
                            text = part.text
                            final_response += text + "\n"
                            if self.verbose:
                                print(f"\n  [{idx}] TEXT:")
                                print(f"  {text}")
                            token_count_estimate += len(text.split()) * 1.3
                        
                        # Handle function calls
                        elif hasattr(part, 'function_call') and part.function_call:
                            fc = part.function_call
                            
                            # Count validation retries
                            if fc.name == "validate_process":
                                validation_retry_count += 1
                            
                            if self.verbose:
                                print(f"\n  [{idx}] FUNCTION_CALL:")
                                print(f"  Name: {fc.name}", end="")
                                if fc.name == "validate_process":
                                    print(f" (Validation Attempt #{validation_retry_count})")
                                else:
                                    print()
                                print(f"  Args: {fc.args}")
                        
                        # Handle function responses
                        elif hasattr(part, 'function_response') and part.function_response:
                            fr = part.function_response
                            if self.verbose:
                                print(f"\n  [{idx}] FUNCTION_RESPONSE:")
                                print(f"  Name: {fr.name}")
                                print(f"  Response: {fr.response}")
                        
                        # Handle thoughts (extended thinking in some models)
                        elif hasattr(part, 'thought') and part.thought:
                            if self.verbose:
                                print(f"\n  [{idx}] THOUGHT:")
                                print(f"  {part.thought}")
                        
                        # Handle thought signatures (reasoning metadata from Gemini 2.5+)
                        elif hasattr(part, '__class__') and 'thought' in part.__class__.__name__.lower():
                            # This handles thought_signature and other thinking-related parts
                            if self.verbose:
                                print(f"\n  [{idx}] REASONING (internal, not included in final output)")
                        
                        # Handle any other part types
                        else:
                            if self.verbose:
                                part_type = part.__class__.__name__ if hasattr(part, '__class__') else type(part).__name__
                                print(f"\n  [{idx}] OTHER ({part_type})")
                    
                    if self.verbose:
                        print(f"--- End Event ---\n")
                    
                    # Store conversation entry
                    conversation.append({
                        "role": "agent",
                        "is_final": event.is_final_response(),
                        "parts": [self._serialize_part(part) for part in event.content.parts]
                    })
            
            execution_time = time.time() - start_time
            
            # Check if iteration limit was reached
            iteration_limit_reached = iteration_count > max_iterations
            
            # Extract validation results from the conversation
            # Track detailed validation metrics
            actual_valid = None  # None means not yet determined
            validation_errors = []
            generated_code = None
            first_validation_response = None
            first_validation_result = None  # True/False/None
            all_validation_results = []  # Track all validation attempts
            validation_history = []  # Track complete history with iteration info
            
            for conv_idx, conv in enumerate(conversation):
                for part in conv.get("parts", []):
                    # Extract generated code from validate_process function calls (FIRST one)
                    if part.get("type") == "function_call" and part.get("name") == "validate_process":
                        code = part.get("args", {}).get("code", "")
                        if code and not generated_code:  # Get the first code attempt
                            generated_code = code
                    
                    # Check function responses for validation results
                    if part.get("type") == "function_response" and part.get("name") == "validate_process":
                        response = part.get("response", "")
                        if isinstance(response, str):
                            # Parse validation result
                            is_valid = None
                            if "'valid': True" in response or '"valid": true' in response.lower():
                                is_valid = True
                            elif "'valid': False" in response or '"valid": false' in response.lower():
                                is_valid = False
                            
                            # Track all validation results
                            if is_valid is not None:
                                all_validation_results.append(is_valid)
                                validation_history.append({
                                    "iteration": conv_idx + 1,
                                    "valid": is_valid,
                                    "response": response[:200] + "..." if len(response) > 200 else response
                                })
                            
                            # Capture FIRST validation result
                            if actual_valid is None and is_valid is not None:
                                actual_valid = is_valid
                                first_validation_result = is_valid
                                first_validation_response = response
                            
                            # Collect validation errors from first validation
                            if first_validation_response == response and ("error" in response.lower() or "failed" in response.lower()):
                                validation_errors.append(response)
            
            # Fallback: check text responses for validation indicators (only if not determined yet)
            if actual_valid is None:
                final_response_lower = final_response.lower()
                actual_valid = any([
                    "validation successful" in final_response_lower,
                    "process is valid" in final_response_lower,
                    "valid process" in final_response_lower,
                    "✅ process is valid" in final_response_lower,
                ])
            
            # Final fallback: if still None, assume False
            if actual_valid is None:
                actual_valid = False
            
            # Extract additional validation errors from text
            text_errors = self._extract_validation_errors(final_response)
            validation_errors.extend(text_errors)
            
            expected_valid = scenario.get("expected_valid", True)
            category = scenario.get("category", "unknown")
            
            # Calculate validation behavior metrics
            failed_first = first_validation_result == False if first_validation_result is not None else None
            iterations_to_pass = None
            if True in all_validation_results:
                # Find iteration where it first passed
                for i, val in enumerate(all_validation_results):
                    if val == True:
                        iterations_to_pass = i + 1
                        break
            
            # Check if agent self-corrected
            self_corrected = len(all_validation_results) > 1 and all_validation_results[0] == False and True in all_validation_results
            
            # Determine final validation state (last validation result)
            final_valid = all_validation_results[-1] if all_validation_results else actual_valid
            
            # Enhanced negative test metrics
            test_type = scenario.get("test_type", "positive")
            negative_initial_validation = first_validation_result if test_type == "negative" else None
            negative_detection_occurred = False
            negative_correction_attempted = False
            negative_correction_successful = False
            negative_iterations_to_detect = None
            negative_iterations_to_fix = None
            
            if test_type == "negative":
                # Check if model detected the error (generated text discussing invalidity)
                if len(all_validation_results) > 1:
                    negative_detection_occurred = True
                    negative_correction_attempted = True
                    # Find iteration where detection occurred (first re-validation)
                    negative_iterations_to_detect = 2 if len(all_validation_results) > 1 else None
                
                # Check if correction was successful
                if negative_correction_attempted and final_valid == True:
                    negative_correction_successful = True
                    negative_iterations_to_fix = iterations_to_pass
            
            # Calculate "passed" based on scenario type
            # For NEGATIVE scenarios: Success means generating invalid code as requested initially
            # For POSITIVE scenarios: Success means generating valid code
            # If iteration limit was reached, scenario cannot pass
            if iteration_limit_reached:
                passed = False
                correctly_generated_invalid = None if test_type != "negative" else (first_validation_result == False)
                eventually_fixed = False
                if test_type == "negative":
                    # For negative tests, we can still check if they generated invalid code first
                    correctly_generated_invalid = (first_validation_result == False)
            elif test_type == "negative":
                # Negative test passes if:
                # 1. Model generated invalid code on first attempt (as requested by the prompt)
                passed = (first_validation_result == False)
                
                # Additional metrics for negative tests
                correctly_generated_invalid = (first_validation_result == False)
                eventually_fixed = (final_valid == True) if final_valid is not None else False
            else:
                # Positive tests pass if final result is valid
                passed = (final_valid == True) if final_valid is not None else False
                correctly_generated_invalid = None
                eventually_fixed = None
            
            # Research-relevant metrics
            tokens_per_iteration = token_count_estimate / iteration_count if iteration_count > 0 else 0
            time_per_iteration = execution_time / iteration_count if iteration_count > 0 else 0
            tokens_per_validation = token_count_estimate / len(all_validation_results) if len(all_validation_results) > 0 else 0
            
            # Success on first try (important for measuring agent capability)
            success_first_try = first_validation_result == True if first_validation_result is not None else False
            
            # Extract error categories from first validation
            error_categories = []
            if first_validation_response and not first_validation_result:
                error_text = first_validation_response.lower()
                if "syntax" in error_text:
                    error_categories.append("syntax")
                if "semantic" in error_text:
                    error_categories.append("semantics")
                if "structural" in error_text:
                    error_categories.append("structural")
                if "topological" in error_text:
                    error_categories.append("topological")
                if "reachability" in error_text:
                    error_categories.append("reachability")
                if "event" in error_text:
                    error_categories.append("event")
            
            # Count specific rules violated
            rules_violated = []
            rules_tested = scenario.get("rules_tested", [])
            if first_validation_response and not first_validation_result:
                response_lower = first_validation_response.lower()
                for rule in rules_tested:
                    if any(keyword in response_lower for keyword in rule.lower().split("_")):
                        rules_violated.append(rule)
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "run_id": self.run_id,
                "scenario_name": scenario_name,
                "category": category,
                "validation_category": scenario.get("category", "unknown"),
                "difficulty_level": scenario.get("difficulty_level", 0),
                "test_type": test_type,
                "expected_valid": expected_valid,
                "actual_valid": actual_valid,
                "final_valid": final_valid,
                "passed": passed,
                "validation_errors": validation_errors,
                "execution_time": round(execution_time, 2),
                "token_count_estimate": int(token_count_estimate),
                "iteration_count": iteration_count,
                "max_iterations": max_iterations,
                "iteration_limit_reached": iteration_limit_reached,
                "validation_retry_count": validation_retry_count,
                # Validation behavior metrics
                "first_validation_result": first_validation_result,
                "failed_first": failed_first,
                "iterations_to_pass": iterations_to_pass,
                "self_corrected": self_corrected,
                "success_first_try": success_first_try,
                "validation_history": validation_history,
                "all_validation_results": all_validation_results,
                # Negative test specific metrics
                "correctly_generated_invalid": correctly_generated_invalid,
                "eventually_fixed": eventually_fixed,
                # Enhanced negative test detection/correction metrics
                "negative_initial_validation": negative_initial_validation,
                "negative_detection_occurred": negative_detection_occurred,
                "negative_correction_attempted": negative_correction_attempted,
                "negative_correction_successful": negative_correction_successful,
                "negative_iterations_to_detect": negative_iterations_to_detect,
                "negative_iterations_to_fix": negative_iterations_to_fix,
                # Research efficiency metrics
                "tokens_per_iteration": round(tokens_per_iteration, 2),
                "time_per_iteration": round(time_per_iteration, 2),
                "tokens_per_validation": round(tokens_per_validation, 2),
                # Error analysis
                "error_categories": error_categories,
                "rules_violated": rules_violated,
                "rules_tested": rules_tested,
                # Model and configuration
                "model_name": self.model_name,
                "tools_used": self.tools_used,
                "instruction_set": "scenario_specific" if include_scenario_instructions else "agent_default",
                # Code and responses
                "generated_code": generated_code,
                "full_query": full_query,
                "final_response": final_response,
                "conversation": conversation,
            }
            
            if self.verbose:
                # Enhanced result header with scenario and model context
                scenario_context = f"[{scenario_number}/{total_scenarios}]" if scenario_number and total_scenarios else ""
                model_context = f"({self.model_name})" if self.model_name else ""
                
                print(f"\n{'='*80}")
                print(f"RESULT: {scenario_name} {scenario_context} {model_context}")
                if iteration_limit_reached:
                    print(f"Test Result: ✗ FAILED (Iteration Limit Reached: {iteration_count}/{max_iterations})")
                else:
                    print(f"Test Result: {'✓ PASSED' if passed else '✗ FAILED'}")
                
                # Show different interpretation for negative vs positive tests
                if category == "negative":
                    print(f"Category: NEGATIVE TEST")
                    print(f"Goal: Generate invalid code as requested, then optionally detect & fix")
                    print(f"First Validation: {'✗ Invalid (as expected ✓)' if first_validation_result == False else '✓ Valid (unexpected ✗)'}")
                    print(f"Final Validation: {'✓ Valid (fixed)' if final_valid == True else '✗ Invalid (not fixed)'}")
                    
                    if correctly_generated_invalid:
                        print(f"  ✓ Successfully generated invalid code as requested")
                        if eventually_fixed:
                            print(f"  ✓ BONUS: Agent detected the error and fixed it!")
                            print(f"    Iterations to fix: {iterations_to_pass}")
                        else:
                            print(f"  ⚠ Agent did not attempt to fix the invalid code")
                    else:
                        print(f"  ✗ Failed to generate invalid code (generated valid code instead)")
                else:
                    print(f"Category: {category.upper()} TEST")
                    print(f"Expected Valid: {expected_valid}, Final Valid: {final_valid}")
                    
                    # Show validation behavior
                    print(f"\nValidation Behavior:")
                    if first_validation_result is not None:
                        print(f"  First Validation: {'✓ Passed' if first_validation_result else '✗ Failed'}")
                    else:
                        print(f"  First Validation: ⚠ Unknown (no validation call detected)")
                    
                    if failed_first:
                        print(f"  ⚠ Generated invalid code first (unexpected for positive test)")
                    
                    if self_corrected:
                        print(f"  Agent Self-Corrected: Yes")
                        if iterations_to_pass:
                            print(f"  Iterations to Pass: {iterations_to_pass}")
                    elif iterations_to_pass == 1:
                        print(f"  Agent Self-Corrected: No (passed on first try)")
                
                if len(validation_history) > 1:
                    print(f"\n  Validation History ({len(validation_history)} attempts):")
                    for vh in validation_history:
                        status = "✓ Pass" if vh["valid"] else "✗ Fail"
                        print(f"    Attempt {validation_history.index(vh) + 1} (Iteration {vh['iteration']}): {status}")
                
                print(f"\nPerformance Metrics:")
                print(f"  Execution Time: {execution_time:.2f}s")
                print(f"  Estimated Tokens: {int(token_count_estimate)}")
                print(f"  Iterations: {iteration_count}")
                print(f"  Validation Attempts: {len(all_validation_results)}")
                
                if generated_code:
                    print(f"\nGenerated Code (First Attempt):")
                    print("```python")
                    print(generated_code.strip())
                    print("```")
                if validation_errors:
                    print(f"\nValidation Errors (First Attempt): {len(validation_errors)}")
                    for error in validation_errors[:3]:  # Show first 3 errors
                        print(f"  - {error[:100]}...")
                print(f"{'='*80}\n")
            
            self.results.append(result)
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "run_id": self.run_id,
                "scenario_name": scenario_name,
                "category": scenario.get("category", "unknown"),
                "expected_valid": scenario.get("expected_valid", True),
                "actual_valid": False,
                "passed": False,
                "validation_errors": [str(e)],
                "execution_time": round(execution_time, 2),
                "token_count_estimate": int(token_count_estimate),
                "iteration_count": iteration_count,
                "validation_retry_count": validation_retry_count,
                "model_name": self.model_name,
                "tools_used": self.tools_used,
                "instruction_set": "scenario_specific" if include_scenario_instructions else "agent_default",
                "error": str(e),
            }
            
            if self.verbose:
                print(f"\n✗ ERROR: {e}\n")
            
            self.results.append(error_result)
            return error_result
    
    def _serialize_part(self, part) -> Dict[str, Any]:
        """Serialize a part object to a dictionary, handling all response part types"""
        # Check part types in order of priority
        if hasattr(part, 'text') and part.text:
            return {"type": "text", "text": part.text}
        
        elif hasattr(part, 'function_call') and part.function_call:
            fc = part.function_call
            return {
                "type": "function_call",
                "name": fc.name,
                "args": dict(fc.args) if fc.args else {}
            }
        
        elif hasattr(part, 'function_response') and part.function_response:
            fr = part.function_response
            return {
                "type": "function_response",
                "name": fr.name,
                "response": str(fr.response)
            }
        
        elif hasattr(part, 'thought') and part.thought:
            return {"type": "thought", "thought": part.thought}
        
        # Handle thought_signature and other reasoning-related parts
        elif hasattr(part, '__class__') and 'thought' in part.__class__.__name__.lower():
            return {
                "type": "reasoning", 
                "class": part.__class__.__name__,
                "note": "Internal reasoning, not included in output"
            }
        
        # Fallback for unknown part types
        else:
            part_type = part.__class__.__name__ if hasattr(part, '__class__') else type(part).__name__
            return {
                "type": "unknown",
                "class": part_type,
                "attributes": [attr for attr in dir(part) if not attr.startswith('_')]
            }
    
    def _extract_validation_errors(self, response: str) -> List[str]:
        """Extract validation errors from agent response"""
        errors = []
        
        # Look for common error patterns
        error_indicators = [
            "error:",
            "validation error:",
            "invalid:",
            "violation:",
            "failed:",
        ]
        
        lines = response.lower().split('\n')
        for line in lines:
            for indicator in error_indicators:
                if indicator in line:
                    errors.append(line.strip())
        
        return errors if errors else []
    
    async def run_multiple_scenarios(
        self,
        scenarios: List[Dict[str, Any]],
        include_scenario_instructions: bool = True,
        max_iterations: int = 25
    ) -> List[Dict[str, Any]]:
        """Run multiple scenarios in sequence"""
        results = []
        
        total = len(scenarios)
        if self.verbose:
            print(f"\n🚀 Starting test run of {total} scenarios...")
            print(f"   Max iterations per scenario: {max_iterations}\n")
        
        for idx, scenario in enumerate(scenarios, 1):
            if self.verbose:
                print(f"\n[{idx}/{total}] Running scenario: {scenario.get('scenario_name')}...")
            
            result = await self.run_scenario(
                scenario=scenario,
                include_scenario_instructions=include_scenario_instructions,
                max_iterations=max_iterations,
                scenario_number=idx,
                total_scenarios=total
            )
            results.append(result)
            
            # Progress update: cumulative passed/failed scenarios so far
            if self.verbose and self.results:
                passed_so_far = sum(1 for r in self.results if r.get("passed"))
                failed_so_far = sum(1 for r in self.results if r.get("passed") is False)
                print(f"[Progress] Scenarios passed: {passed_so_far}, failed: {failed_so_far} (completed: {len(self.results)}/{total})")
            
            # Brief pause between scenarios
            await asyncio.sleep(1)
        
        return results
    
    def save_results(self, output_file: Optional[str] = None):
        """Save test results to a JSON file organized by model/run"""
        if not self.results:
            print("No results to save")
            return
        
        # Create directory structure: benchmark_results/model_name/run_id/
        clean_model_name = self.model_name.replace("/", "_").replace(":", "_").replace("-", "_")
        model_dir = Path("benchmark_results") / clean_model_name
        run_dir = model_dir / self.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename if not provided
        if output_file is None:
            output_file = f"results.json"
        
        output_path = run_dir / output_file
        
        # Save results with metadata
        output_data = {
            "metadata": {
                "run_id": self.run_id,
                "model_name": self.model_name,
                "tools_used": self.tools_used,
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results if r.get("passed")),
                "failed": sum(1 for r in self.results if not r.get("passed")),
            },
            "results": self.results
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Also save to a JSONL file for easy appending and analysis
        jsonl_path = model_dir / "all_runs.jsonl"
        with open(jsonl_path, 'a') as f:
            f.write(json.dumps(output_data["metadata"]) + "\n")
        
        print(f"\n✓ Results saved to: {output_path}")
        print(f"✓ Run metadata appended to: {jsonl_path}")
    
    def print_summary(self):
        """Print a summary of test results"""
        if not self.results:
            print("No results to summarize")
            return
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("passed"))
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        # Performance metrics
        avg_time = sum(r.get("execution_time", 0) for r in self.results) / total if total > 0 else 0
        total_tokens = sum(r.get("token_count_estimate", 0) for r in self.results)
        avg_iterations = sum(r.get("iteration_count", 0) for r in self.results) / total if total > 0 else 0
        total_iterations = sum(r.get("iteration_count", 0) for r in self.results)
        
        # New validation behavior metrics
        tests_failed_first = sum(1 for r in self.results if r.get("failed_first") == True)
        tests_self_corrected = sum(1 for r in self.results if r.get("self_corrected") == True)
        avg_validation_attempts = sum(len(r.get("all_validation_results", [])) for r in self.results) / total if total > 0 else 0
        
        # Iteration limit metrics
        tests_hit_iteration_limit = sum(1 for r in self.results if r.get("iteration_limit_reached") == True)
        max_iterations_used = max((r.get("iteration_count", 0) for r in self.results), default=0)
        
        # Category breakdown
        negative_tests = [r for r in self.results if r.get("category") == "negative"]
        negative_passed = sum(1 for r in negative_tests if r.get("passed"))
        negative_correctly_invalid = sum(1 for r in negative_tests if r.get("correctly_generated_invalid") == True)
        negative_eventually_fixed = sum(1 for r in negative_tests if r.get("eventually_fixed") == True)
        
        positive_tests = [r for r in self.results if r.get("category") == "positive"]
        positive_passed = sum(1 for r in positive_tests if r.get("passed"))
        
        print(f"\n{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({pass_rate:.1f}%)")
        print(f"Failed: {failed} ({100-pass_rate:.1f}%)")
        
        if negative_tests or positive_tests:
            print(f"\nBy Category:")
            if positive_tests:
                pos_rate = (positive_passed / len(positive_tests) * 100) if len(positive_tests) > 0 else 0
                print(f"  Positive Tests: {positive_passed}/{len(positive_tests)} passed ({pos_rate:.1f}%)")
            if negative_tests:
                neg_rate = (negative_passed / len(negative_tests) * 100) if len(negative_tests) > 0 else 0
                invalid_rate = (negative_correctly_invalid / len(negative_tests) * 100) if len(negative_tests) > 0 else 0
                fixed_rate = (negative_eventually_fixed / len(negative_tests) * 100) if len(negative_tests) > 0 else 0
                print(f"  Negative Tests: {negative_passed}/{len(negative_tests)} passed ({neg_rate:.1f}%)")
                print(f"    - Correctly generated invalid code: {negative_correctly_invalid}/{len(negative_tests)} ({invalid_rate:.1f}%)")
                print(f"    - Eventually detected & fixed: {negative_eventually_fixed}/{len(negative_tests)} ({fixed_rate:.1f}%)")
        
        print(f"\nValidation Behavior:")
        print(f"  Tests Failed First Validation: {tests_failed_first}/{total}")
        print(f"  Tests Self-Corrected: {tests_self_corrected}/{total}")
        print(f"  Average Validation Attempts: {avg_validation_attempts:.1f}")
        
        print(f"\nPerformance Metrics:")
        print(f"  Average Execution Time: {avg_time:.2f}s")
        print(f"  Total Estimated Tokens: {total_tokens:,}")
        print(f"  Average Iterations: {avg_iterations:.1f} (Total: {total_iterations})")
        print(f"  Max Iterations Used: {max_iterations_used}")
        if tests_hit_iteration_limit > 0:
            print(f"  ⚠️  Tests Hit Iteration Limit: {tests_hit_iteration_limit}/{total}")
        print(f"{'='*80}\n")
        
        # Failed tests detail
        if failed > 0:
            print("Failed Tests Detail:")
            for result in self.results:
                if not result.get("passed"):
                    category = result.get('category')
                    print(f"  ✗ {result.get('scenario_name')} - {category}")
                    
                    if result.get("iteration_limit_reached"):
                        print(f"    ⚠️  Iteration Limit Reached: {result.get('iteration_count')}/{result.get('max_iterations')}")
                    
                    if category == "negative":
                        print(f"    Generated Invalid Code: {'Yes' if result.get('correctly_generated_invalid') else 'No (FAIL)'}")
                        print(f"    Eventually Fixed: {'Yes' if result.get('eventually_fixed') else 'No'}")
                    else:
                        print(f"    Expected: {'Valid' if result.get('expected_valid') else 'Invalid'}, Final: {'Valid' if result.get('final_valid') else 'Invalid'}")
                        if result.get("failed_first") is not None:
                            print(f"    First Validation: {'Failed' if result.get('failed_first') else 'Passed'}")
                        if result.get("self_corrected"):
                            print(f"    Self-Corrected: Yes (in {result.get('iterations_to_pass', '?')} attempts)")
            print()


def list_scenarios():
    """List all available scenarios"""
    print("\n" + "="*80)
    print("AVAILABLE SCENARIOS")
    print("="*80 + "\n")
    
    all_scenarios = get_all_scenarios()
    
    for category_name, scenarios in all_scenarios.items():
        print(f"\n{category_name.upper()} ({len(scenarios)} scenarios):")
        for scenario in scenarios:
            print(f"  - {scenario.get('scenario_name')}")
            print(f"    {scenario.get('description', 'No description')}")
    
    # Count total scenarios
    total_scenarios = sum(len(s) for s in all_scenarios.values())
    print(f"\nTotal scenarios: {total_scenarios}")
    print("="*80 + "\n")


def find_scenario_by_name(scenario_name: str) -> Optional[Dict[str, Any]]:
    """Find a scenario by name"""
    all_scenarios_dict = get_all_scenarios()
    for category, scenarios in all_scenarios_dict.items():
        for scenario in scenarios:
            if scenario.get("scenario_name") == scenario_name:
                return scenario
    return None


async def main():
    """Main entry point for the test script"""
    parser = argparse.ArgumentParser(
        description="Automated BPMN Agent Scenario Testing"
    )
    
    parser.add_argument(
        "--scenario",
        type=str,
        help="Run a specific scenario by name"
    )
    
    parser.add_argument(
        "--category",
        type=str,
        choices=["level_1_basic_syntax", "level_2_static_semantics", "level_3_event_rules", 
                 "level_4_structural_rules", "level_5_topological_reachability", "level_6_integration_complex"],
        help="Run all scenarios in a level category"
    )
    
    parser.add_argument(
        "--validation-category",
        type=str,
        choices=["syntax", "semantics", "event_rules", "structural", "topological", "integration"],
        help="Run all scenarios in a validation category"
    )
    
    parser.add_argument(
        "--difficulty",
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        help="Run scenarios at a specific difficulty level (1=easiest, 6=hardest)"
    )
    
    parser.add_argument(
        "--test-type",
        type=str,
        choices=["positive", "negative"],
        help="Run only positive or negative test scenarios"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all available scenarios"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available scenarios"
    )
    
    parser.add_argument(
        "--no-instructions",
        action="store_true",
        help="Don't append scenario instructions to the prompt"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output file name for results (default: auto-generated)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output (only summary)"
    )
    
    parser.add_argument(
        "--run-id",
        type=str,
        help="Custom run ID for organizing results (default: auto-generated)"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=25,
        help="Maximum number of iterations per scenario before stopping (default: 25)"
    )
    
    args = parser.parse_args()
    
    # List scenarios and exit
    if args.list:
        list_scenarios()
        return
    
    # Determine which scenarios to run
    scenarios_to_run = []
    
    if args.scenario:
        scenario = find_scenario_by_name(args.scenario)
        if scenario is None:
            print(f"Error: Scenario '{args.scenario}' not found")
            print("Use --list to see available scenarios")
            return
        scenarios_to_run = [scenario]
    
    elif args.category:
        scenarios_to_run = get_scenarios_by_category(args.category)
        if not scenarios_to_run:
            print(f"Error: No scenarios found for category '{args.category}'")
            return
    
    elif args.validation_category:
        scenarios_to_run = get_scenarios_by_validation_category(args.validation_category)
        if not scenarios_to_run:
            print(f"Error: No scenarios found for validation category '{args.validation_category}'")
            return
    
    elif args.difficulty:
        scenarios_to_run = get_scenarios_by_difficulty_level(args.difficulty)
        if not scenarios_to_run:
            print(f"Error: No scenarios found for difficulty level '{args.difficulty}'")
            return
    
    elif args.test_type:
        scenarios_to_run = get_scenarios_by_test_type(args.test_type)
        if not scenarios_to_run:
            print(f"Error: No scenarios found for test type '{args.test_type}'")
            return
    
    elif args.all:
        # Get all scenarios from all categories
        all_scenarios_dict = get_all_scenarios()
        scenarios_to_run = []
        for scenarios in all_scenarios_dict.values():
            scenarios_to_run.extend(scenarios)
    
    else:
        print("Error: Must specify --scenario, --category, --all, or --list")
        parser.print_help()
        return
    
    # Run the tests
    runner = ScenarioTestRunner(verbose=not args.quiet, run_id=args.run_id)
    await runner.initialize()
    
    await runner.run_multiple_scenarios(
        scenarios=scenarios_to_run,
        include_scenario_instructions=not args.no_instructions,
        max_iterations=args.max_iterations
    )
    
    # Print summary and save results
    runner.print_summary()
    runner.save_results(output_file=args.output)
    
    print("\n✓ Test run complete!")


if __name__ == "__main__":
    asyncio.run(main())
