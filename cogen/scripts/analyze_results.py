"""
BPMN Agent Benchmark Results Analysis (CSV outputs only)

This script analyzes benchmark results and generates CSV summaries for research.

Usage:
    python analyze_results.py
    python analyze_results.py --results-dir benchmark_results
    python analyze_results.py --output-dir results
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
from datetime import datetime
import statistics


class BenchmarkAnalyzer:
    """Analyzes BPMN agent benchmark results and exports CSVs"""
    
    def __init__(self, results_dir: str = "benchmark_results", output_dir: str = "results", 
                 model_name: Optional[str] = None, run_id: Optional[str] = None):
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
        self.model_name = model_name
        self.run_id = run_id
        self.results = []
        self.aggregated_data = {}
        self.run_metadata = {}
        self.model_info = {}  # Deprecated; kept for backward compatibility
        
    def load_results(self):
        """Load JSON result files from the benchmark directory"""
        print(f"Loading results from {self.results_dir}...")
        
        # Determine which files to load based on model_name and run_id
        if self.model_name and self.run_id:
            # Load specific run
            result_file = self.results_dir / self.model_name / self.run_id / "results.json"
            if result_file.exists():
                self._load_result_file(result_file)
            else:
                print(f"⚠ No results found for model '{self.model_name}', run '{self.run_id}'")
                return False
        elif self.model_name:
            # Load all runs for a specific model
            model_dir = self.results_dir / self.model_name
            if model_dir.exists():
                for run_dir in model_dir.iterdir():
                    if run_dir.is_dir():
                        result_file = run_dir / "results.json"
                        if result_file.exists():
                            self._load_result_file(result_file)
            else:
                print(f"⚠ No results found for model '{self.model_name}'")
                return False
        else:
            # Load all results from all models and runs
            for model_dir in self.results_dir.iterdir():
                if model_dir.is_dir():
                    for run_dir in model_dir.iterdir():
                        if run_dir.is_dir():
                            result_file = run_dir / "results.json"
                            if result_file.exists():
                                self._load_result_file(result_file)
            
            # Also try to load old format for backward compatibility
            for file_path in self.results_dir.glob("*.json"):
                if file_path.name != "all_results.jsonl":
                    try:
                        with open(file_path, 'r') as f:
                            result = json.load(f)
                            if isinstance(result, list):
                                self.results.extend(result)
                            elif isinstance(result, dict) and "results" not in result:
                                self.results.append(result)
                    except Exception as e:
                        print(f"Warning: Could not load {file_path}: {e}")
        
        print(f"✓ Loaded {len(self.results)} test results from {len(self.run_metadata)} run(s)")
        
        if not self.results:
            print("⚠ No results found. Run tests first with run_scenario_tests.py")
            return False
        
        return True
    
    def _load_result_file(self, file_path: Path):
        """Load a single result file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and "metadata" in data and "results" in data:
                    # New format with metadata
                    run_id = data["metadata"].get("run_id", file_path.parent.name)
                    self.run_metadata[run_id] = data["metadata"]
                    self.results.extend(data["results"])
                elif isinstance(data, list):
                    # Old format: array of results
                    self.results.extend(data)
                elif isinstance(data, dict):
                    # Old format: single result
                    self.results.append(data)
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
    
    def aggregate_data(self):
        """Aggregate results by various dimensions"""
        print("Aggregating data...")
        
        # By category
        self.aggregated_data['by_category'] = defaultdict(list)
        self.aggregated_data['by_model'] = defaultdict(list)
        self.aggregated_data['by_scenario'] = defaultdict(list)
        self.aggregated_data['by_rules'] = defaultdict(list)
        self.aggregated_data['by_error_category'] = defaultdict(list)
        
        # New aggregation dimensions
        self.aggregated_data['by_validation_category'] = defaultdict(list)
        self.aggregated_data['by_difficulty_level'] = defaultdict(list)
        self.aggregated_data['by_test_type'] = defaultdict(list)
        
        for result in self.results:
            category = result.get('category', 'unknown')
            model = result.get('model_name', 'unknown')
            scenario = result.get('scenario_name', 'unknown')
            validation_category = result.get('validation_category', 'unknown')
            difficulty_level = result.get('difficulty_level', 0)
            test_type = result.get('test_type', 'positive')
            
            self.aggregated_data['by_category'][category].append(result)
            self.aggregated_data['by_model'][model].append(result)
            self.aggregated_data['by_scenario'][scenario].append(result)
            self.aggregated_data['by_validation_category'][validation_category].append(result)
            self.aggregated_data['by_difficulty_level'][difficulty_level].append(result)
            self.aggregated_data['by_test_type'][test_type].append(result)
            
            # Aggregate by rules tested
            for rule in result.get('rules_tested', []):
                self.aggregated_data['by_rules'][rule].append(result)
            
            # Aggregate by error categories
            for error_cat in result.get('error_categories', []):
                self.aggregated_data['by_error_category'][error_cat].append(result)
        
        print("✓ Data aggregated")
    
    def get_models(self):
        """Get list of all models"""
        return list(self.aggregated_data['by_model'].keys())
    
    def calculate_repair_attempts(self, result):
        """Calculate repair attempts from validation history"""
        validation_history = result.get('validation_history', [])
        if len(validation_history) <= 1:
            return 0
        
        repair_attempts = 0
        for i in range(1, len(validation_history)):
            prev_iter = validation_history[i-1]['iteration']
            curr_iter = validation_history[i]['iteration']
            # Iterations between validations = repair attempts
            repair_attempts += (curr_iter - prev_iter - 1)
        
        return repair_attempts
    
    def calculate_repair_iterations_detailed(self, result):
        """Calculate repair iterations between validations as a list"""
        validation_history = result.get('validation_history', [])
        if len(validation_history) <= 1:
            return []
        
        repair_cycles = []
        for i in range(1, len(validation_history)):
            prev_iter = validation_history[i-1]['iteration']
            curr_iter = validation_history[i]['iteration']
            repair_cycles.append(curr_iter - prev_iter - 1)
        
        return repair_cycles
    
    def calculate_convergence_within_n(self, results, n_iterations):
        """Calculate proportion of tests that converged within N iterations"""
        converged = 0
        for result in results:
            if result.get('passed') and result.get('iterations_to_pass'):
                if result.get('iterations_to_pass') <= n_iterations:
                    converged += 1
        
        total = len([r for r in results if r.get('passed')])
        return (converged / total * 100) if total > 0 else 0
    
    def infer_agent_contribution(self, rules_violated):
        """Map rules violated to element types (agents)"""
        element_types = set()
        
        # Rule to element type mapping
        start_event_rules = ['ONE_START_EVENT', 'START_NO_INCOMING']
        end_event_rules = ['AT_LEAST_ONE_END_EVENT', 'END_NO_OUTGOING']
        task_rules = ['VALID_TASK_TYPES', 'NO_CONSECUTIVE_SERVICE_TASKS', 'MAX_TASKS_IN_A_ROW', 
                     'MANDATORY_ERROR_HANDLING_FOR_SCRIPTS', 'NO_EVENT_BETWEEN_SAME_TASKS']
        gateway_rules = ['VALID_GATEWAY_TYPES', 'GATEWAY_BRANCHING_RULE', 'GATEWAY_CANNOT_BE_BOTH',
                        'EXCLUSIVE_GATEWAY_BEHAVIOR', 'PARALLEL_GATEWAY_BEHAVIOR', 'PATH_SYMMETRY_RULE']
        intermediate_event_rules = ['INTERMEDIATE_MUST_CONNECT']
        
        for rule in rules_violated:
            if rule in start_event_rules:
                element_types.add('StartEvent')
            elif rule in end_event_rules:
                element_types.add('EndEvent')
            elif rule in task_rules:
                element_types.add('Task')
            elif rule in gateway_rules:
                element_types.add('Gateway')
            elif rule in intermediate_event_rules:
                element_types.add('IntermediateEvent')
        
        return list(element_types)
    
    def calculate_first_repair_success_rate(self, results):
        """Check if first validation after initial failure succeeds"""
        first_repair_successes = 0
        total_repair_attempts = 0
        
        for result in results:
            val_history = result.get('validation_history', [])
            # Need at least 2 validations: initial failure + first repair
            if len(val_history) >= 2:
                # Check if first validation failed
                if not val_history[0].get('valid'):
                    total_repair_attempts += 1
                    # Check if second validation succeeded
                    if val_history[1].get('valid'):
                        first_repair_successes += 1
        
        return (first_repair_successes / total_repair_attempts * 100) if total_repair_attempts > 0 else 0
    
    def calculate_error_detection_by_level(self):
        """Parse validation errors to extract which level caught the error"""
        level_detection = defaultdict(int)
        
        for result in self.results:
            validation_errors = result.get('validation_errors', [])
            if validation_errors:
                # Parse first validation error to see which level failed
                first_error = str(validation_errors[0])
                if 'Syntax validation failed' in first_error or 'Syntax Error' in first_error:
                    level_detection['Syntax'] += 1
                elif 'Static semantics' in first_error or 'Static Semantic' in first_error:
                    level_detection['Static Semantics'] += 1
                elif 'Event rules' in first_error or 'Event Rule' in first_error:
                    level_detection['Event Rules'] += 1
                elif 'Structural rules' in first_error or 'Structural Rule' in first_error:
                    level_detection['Structural Rules'] += 1
                elif 'Advanced structural' in first_error:
                    level_detection['Advanced Structural Rules'] += 1
                elif 'Topological rules' in first_error or 'Topological Rule' in first_error:
                    level_detection['Topological Rules'] += 1
                elif 'Reachability' in first_error:
                    level_detection['Reachability'] += 1
        
        return level_detection
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate summary statistics"""
        stats = {
            'total_tests': len(self.results),
            'passed': sum(1 for r in self.results if r.get('passed')),
            'failed': sum(1 for r in self.results if not r.get('passed')),
            'pass_rate': 0.0,
            'avg_execution_time': 0.0,
            'avg_tokens': 0.0,
            'avg_iterations': 0.0,
            'avg_validation_attempts': 0.0,
            'avg_repair_attempts': 0.0,
            'avg_validation_retries': 0.0,
            'repair_success_rate': 0.0,
            'success_first_try_rate': 0.0,
            'self_correction_rate': 0.0,
            # Negative test specific metrics
            'negative_tests_count': sum(1 for r in self.results if r.get('category') == 'negative'),
            'negative_correctly_invalid_rate': 0.0,
            'negative_eventually_fixed_rate': 0.0,
        }
        
        if self.results:
            stats['pass_rate'] = stats['passed'] / stats['total_tests'] * 100
            
            # Filter out None values for numeric fields
            exec_times = [r.get('execution_time', 0) for r in self.results if r.get('execution_time') is not None]
            stats['avg_execution_time'] = statistics.mean(exec_times) if exec_times else 0
            
            tokens = [r.get('token_count_estimate', 0) for r in self.results if r.get('token_count_estimate') is not None]
            stats['avg_tokens'] = statistics.mean(tokens) if tokens else 0
            
            iterations = [r.get('iteration_count', 0) for r in self.results if r.get('iteration_count') is not None]
            stats['avg_iterations'] = statistics.mean(iterations) if iterations else 0
            
            validation_attempts = [len(r.get('all_validation_results', [])) for r in self.results]
            stats['avg_validation_attempts'] = statistics.mean(validation_attempts) if validation_attempts else 0
            
            # Calculate repair metrics
            repair_attempts = [self.calculate_repair_attempts(r) for r in self.results]
            stats['avg_repair_attempts'] = statistics.mean(repair_attempts) if repair_attempts else 0
            
            validation_retries = [r.get('validation_retry_count', 0) for r in self.results if r.get('validation_retry_count') is not None]
            stats['avg_validation_retries'] = statistics.mean(validation_retries) if validation_retries else 0
            
            # Calculate repair success rate (tests where repairs led to passing)
            repair_success_count = sum(1 for r in self.results 
                                     if r.get('self_corrected') and r.get('passed'))
            total_with_repairs = sum(1 for r in self.results 
                                   if self.calculate_repair_attempts(r) > 0)
            stats['repair_success_rate'] = (repair_success_count / total_with_repairs * 100) if total_with_repairs > 0 else 0
            
            stats['success_first_try_rate'] = sum(
                1 for r in self.results if r.get('success_first_try')
            ) / stats['total_tests'] * 100
            stats['self_correction_rate'] = sum(
                1 for r in self.results if r.get('self_corrected')
            ) / stats['total_tests'] * 100
            
            # Calculate negative test metrics
            negative_tests = [r for r in self.results if r.get('category') == 'negative']
            if negative_tests:
                stats['negative_correctly_invalid_rate'] = sum(
                    1 for r in negative_tests if r.get('correctly_generated_invalid')
                ) / len(negative_tests) * 100
                stats['negative_eventually_fixed_rate'] = sum(
                    1 for r in negative_tests if r.get('eventually_fixed')
                ) / len(negative_tests) * 100
        
        # Statistics by category
        stats['by_category'] = {}
        for category, results in self.aggregated_data['by_category'].items():
            passed = sum(1 for r in results if r.get('passed'))
            total = len(results)
            
            # Filter out None values for category statistics
            exec_times = [r.get('execution_time', 0) for r in results if r.get('execution_time') is not None]
            tokens = [r.get('token_count_estimate', 0) for r in results if r.get('token_count_estimate') is not None]
            repair_attempts = [self.calculate_repair_attempts(r) for r in results]
            validation_retries = [r.get('validation_retry_count', 0) for r in results if r.get('validation_retry_count') is not None]
            
            stats['by_category'][category] = {
                'total': total,
                'passed': passed,
                'pass_rate': (passed / total * 100) if total > 0 else 0,
                'avg_execution_time': statistics.mean(exec_times) if exec_times else 0,
                'avg_tokens': statistics.mean(tokens) if tokens else 0,
                'avg_repair_attempts': statistics.mean(repair_attempts) if repair_attempts else 0,
                'avg_validation_retries': statistics.mean(validation_retries) if validation_retries else 0,
            }
        
        return stats
    
    def print_summary(self):
        """Print a text summary of results"""
        stats = self.calculate_statistics()
        
        print("\n" + "="*80)
        print("BENCHMARK ANALYSIS SUMMARY")
        print("="*80)
        print(f"\nOverall Results:")
        print(f"  Total Tests: {stats['total_tests']}")
        print(f"  Passed: {stats['passed']} ({stats['pass_rate']:.1f}%)")
        print(f"  Failed: {stats['failed']} ({100-stats['pass_rate']:.1f}%)")
        
        print(f"\nPerformance Metrics:")
        print(f"  Average Execution Time: {stats['avg_execution_time']:.2f}s")
        print(f"  Average Tokens: {stats['avg_tokens']:.0f}")
        print(f"  Average Iterations: {stats['avg_iterations']:.1f}")
        print(f"  Average Validation Attempts: {stats['avg_validation_attempts']:.1f}")
        
        print(f"\nAgent Behavior:")
        print(f"  Success on First Try: {stats['success_first_try_rate']:.1f}%")
        print(f"  Self-Correction Rate: {stats['self_correction_rate']:.1f}%")
        
        if stats['negative_tests_count'] > 0:
            print(f"\nNegative Test Performance:")
            print(f"  Total Negative Tests: {stats['negative_tests_count']}")
            print(f"  Correctly Generated Invalid Code: {stats['negative_correctly_invalid_rate']:.1f}%")
            print(f"  Eventually Detected & Fixed: {stats['negative_eventually_fixed_rate']:.1f}%")
        
        print(f"\nBy Category:")
        for category, cat_stats in stats['by_category'].items():
            print(f"  {category.capitalize()}:")
            print(f"    Tests: {cat_stats['total']}")
            print(f"    Pass Rate: {cat_stats['pass_rate']:.1f}%")
            print(f"    Avg Time: {cat_stats['avg_execution_time']:.2f}s")
            print(f"    Avg Tokens: {cat_stats['avg_tokens']:.0f}")
        
        print("="*80 + "\n")
    
    def export_research_summary_table(self):
        """Export comprehensive research summary table"""
        import csv
        
        output_path = self.output_dir / 'research_summary_table.csv'
        models = self.get_models()
        val_cats = ['syntax', 'semantics', 'event_rules', 'structural', 'topological', 'integration']
        difficulty_levels = sorted([k for k in self.aggregated_data['by_difficulty_level'].keys() if k > 0])
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Research Summary Table'])
            writer.writerow([])
            
            # Overall metrics by model (sorted by performance - pass rate descending)
            writer.writerow(['Model', 'Total Tests', 'Pass Rate (%)', 'Avg Time (s)', 'Avg Tokens', 'Avg Iterations', 'Avg Repair Attempts', 'Avg Validation Retries'])
            
            # Calculate performance metrics for each model and sort by pass rate
            model_performance = []
            for model in models:
                results = self.aggregated_data['by_model'][model]
                passed = sum(1 for r in results if r.get('passed'))
                pass_rate = passed / len(results) * 100 if results else 0
                
                exec_times = [r.get('execution_time', 0) for r in results if r.get('execution_time')]
                tokens = [r.get('token_count_estimate', 0) for r in results if r.get('token_count_estimate')]
                iterations = [r.get('iteration_count', 0) for r in results if r.get('iteration_count')]
                repair_attempts = [self.calculate_repair_attempts(r) for r in results]
                validation_retries = [r.get('validation_retry_count', 0) for r in results if r.get('validation_retry_count') is not None]
                
                model_performance.append({
                    'model': model,
                    'total': len(results),
                    'pass_rate': pass_rate,
                    'avg_time': statistics.mean(exec_times) if exec_times else 0,
                    'avg_tokens': statistics.mean(tokens) if tokens else 0,
                    'avg_iterations': statistics.mean(iterations) if iterations else 0,
                    'avg_repair_attempts': statistics.mean(repair_attempts) if repair_attempts else 0,
                    'avg_validation_retries': statistics.mean(validation_retries) if validation_retries else 0
                })
            
            # Sort by pass rate (best to lowest)
            model_performance.sort(key=lambda x: x['pass_rate'], reverse=True)
            
            for model_data in model_performance:
                writer.writerow([
                    model_data['model'],
                    model_data['total'],
                    f"{model_data['pass_rate']:.1f}",
                    f"{model_data['avg_time']:.2f}" if model_data['avg_time'] > 0 else "0",
                    f"{model_data['avg_tokens']:.0f}" if model_data['avg_tokens'] > 0 else "0",
                    f"{model_data['avg_iterations']:.1f}" if model_data['avg_iterations'] > 0 else "0",
                    f"{model_data['avg_repair_attempts']:.1f}" if model_data['avg_repair_attempts'] > 0 else "0",
                    f"{model_data['avg_validation_retries']:.1f}" if model_data['avg_validation_retries'] > 0 else "0"
                ])
            
            writer.writerow([])
            writer.writerow(['Pass Rate by Validation Category (%)'])
            writer.writerow(['Model'] + [c.replace('_', ' ').title() for c in val_cats])
            
            # Calculate average performance across validation categories for sorting
            model_val_performance = []
            for model in models:
                rates = []
                for val_cat in val_cats:
                    results = [r for r in self.aggregated_data['by_validation_category'][val_cat]
                              if r.get('model_name') == model]
                    rate = sum(1 for r in results if r.get('passed')) / len(results) * 100 if results else 0
                    rates.append(rate)
                
                # Calculate average performance across all validation categories
                avg_performance = statistics.mean(rates) if rates else 0
                model_val_performance.append({
                    'model': model,
                    'rates': rates,
                    'avg_performance': avg_performance
                })
            
            # Sort by average performance (best to lowest)
            model_val_performance.sort(key=lambda x: x['avg_performance'], reverse=True)
            
            for model_data in model_val_performance:
                formatted_rates = [f"{rate:.1f}" for rate in model_data['rates']]
                writer.writerow([model_data['model']] + formatted_rates)
            
            writer.writerow([])
            writer.writerow(['Pass Rate by Difficulty Level (%)'])
            writer.writerow(['Model'] + [f'Level {l}' for l in difficulty_levels])
            
            # Calculate average performance across difficulty levels for sorting
            model_diff_performance = []
            for model in models:
                rates = []
                for level in difficulty_levels:
                    results = [r for r in self.aggregated_data['by_difficulty_level'][level]
                              if r.get('model_name') == model]
                    rate = sum(1 for r in results if r.get('passed')) / len(results) * 100 if results else 0
                    rates.append(rate)
                
                # Calculate average performance across all difficulty levels
                avg_performance = statistics.mean(rates) if rates else 0
                model_diff_performance.append({
                    'model': model,
                    'rates': rates,
                    'avg_performance': avg_performance
                })
            
            # Sort by average performance (best to lowest)
            model_diff_performance.sort(key=lambda x: x['avg_performance'], reverse=True)
            
            for model_data in model_diff_performance:
                formatted_rates = [f"{rate:.1f}" for rate in model_data['rates']]
                writer.writerow([model_data['model']] + formatted_rates)
            
            writer.writerow([])
            writer.writerow(['Negative Test Performance'])
            writer.writerow(['Model', 'Total Negative', 'Generated Invalid (%)', 'Detected (%)', 'Corrected (%)', 'Avg Iters to Fix'])
            
            # Calculate negative test performance for each model and sort by overall performance
            model_neg_performance = []
            for model in models:
                neg_results = [r for r in self.aggregated_data['by_test_type']['negative']
                              if r.get('model_name') == model]
                
                if neg_results:
                    gen_invalid = sum(1 for r in neg_results if r.get('correctly_generated_invalid'))
                    detected = sum(1 for r in neg_results if r.get('negative_detection_occurred'))
                    corrected = sum(1 for r in neg_results if r.get('negative_correction_successful'))
                    
                    fix_iters = [r.get('negative_iterations_to_fix') for r in neg_results 
                                if r.get('negative_iterations_to_fix')]
                    
                    # Calculate average performance across negative test metrics
                    gen_invalid_rate = gen_invalid / len(neg_results) * 100
                    detected_rate = detected / len(neg_results) * 100
                    corrected_rate = corrected / len(neg_results) * 100
                    avg_fix_iters = statistics.mean(fix_iters) if fix_iters else 0
                    
                    # Overall performance score (higher is better): average of detection and correction rates
                    overall_performance = (detected_rate + corrected_rate) / 2
                    
                    model_neg_performance.append({
                        'model': model,
                        'total': len(neg_results),
                        'gen_invalid_rate': gen_invalid_rate,
                        'detected_rate': detected_rate,
                        'corrected_rate': corrected_rate,
                        'avg_fix_iters': avg_fix_iters,
                        'overall_performance': overall_performance
                    })
            
            # Sort by overall performance (best to lowest)
            model_neg_performance.sort(key=lambda x: x['overall_performance'], reverse=True)
            
            for model_data in model_neg_performance:
                writer.writerow([
                    model_data['model'],
                    model_data['total'],
                    f"{model_data['gen_invalid_rate']:.1f}",
                    f"{model_data['detected_rate']:.1f}",
                    f"{model_data['corrected_rate']:.1f}",
                    f"{model_data['avg_fix_iters']:.1f}" if model_data['avg_fix_iters'] > 0 else "N/A"
                ])
        
        print(f"✓ Saved: {output_path}")
    
    def export_summary_table(self):
        """Export summary statistics to a CSV file"""
        import csv
        
        output_path = self.output_dir / 'summary_statistics.csv'
        
        stats = self.calculate_statistics()
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Overall statistics
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Tests', stats['total_tests']])
            writer.writerow(['Passed', stats['passed']])
            writer.writerow(['Failed', stats['failed']])
            writer.writerow(['Pass Rate (%)', f"{stats['pass_rate']:.2f}"])
            writer.writerow(['Average Execution Time (s)', f"{stats['avg_execution_time']:.2f}"])
            writer.writerow(['Average Tokens', f"{stats['avg_tokens']:.0f}"])
            writer.writerow(['Average Iterations', f"{stats['avg_iterations']:.2f}"])
            writer.writerow(['Average Validation Attempts', f"{stats['avg_validation_attempts']:.2f}"])
            writer.writerow(['Average Repair Attempts', f"{stats['avg_repair_attempts']:.2f}"])
            writer.writerow(['Average Validation Retries', f"{stats['avg_validation_retries']:.2f}"])
            writer.writerow(['Repair Success Rate (%)', f"{stats['repair_success_rate']:.2f}"])
            writer.writerow(['Success First Try Rate (%)', f"{stats['success_first_try_rate']:.2f}"])
            writer.writerow(['Self-Correction Rate (%)', f"{stats['self_correction_rate']:.2f}"])
            
            writer.writerow([])
            writer.writerow(['Category', 'Total', 'Passed', 'Pass Rate (%)', 'Avg Time (s)', 'Avg Tokens', 'Avg Repair Attempts', 'Avg Validation Retries'])
            
            # Sort categories by pass rate (best to lowest)
            sorted_categories = sorted(stats['by_category'].items(), 
                                     key=lambda x: x[1]['pass_rate'], reverse=True)
            
            for category, cat_stats in sorted_categories:
                writer.writerow([
                    category,
                    cat_stats['total'],
                    cat_stats['passed'],
                    f"{cat_stats['pass_rate']:.2f}",
                    f"{cat_stats['avg_execution_time']:.2f}",
                    f"{cat_stats['avg_tokens']:.0f}",
                    f"{cat_stats['avg_repair_attempts']:.2f}",
                    f"{cat_stats['avg_validation_retries']:.2f}"
                ])
        
        print(f"✓ Saved: {output_path}")
    
    def export_model_comparison_table(self):
        """Export detailed model comparison to CSV"""
        import csv
        
        models = list(self.aggregated_data['by_model'].keys())
        
        if len(models) < 2:
            return
        
        output_path = self.output_dir / 'model_comparison_table.csv'
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Model', 'Total Tests', 'Passed', 'Failed', 'Pass Rate (%)', 
                           'Avg Time (s)', 'Avg Tokens', 'Avg Iterations', 
                           'Avg Repair Attempts', 'Avg Validation Retries',
                           'First Try Success (%)', 'Self-Correction (%)'])
            
            # Calculate performance metrics for each model and sort by pass rate
            model_performance = []
            for model in models:
                results = self.aggregated_data['by_model'][model]
                passed = sum(1 for r in results if r.get('passed'))
                total = len(results)
                failed = total - passed
                pass_rate = (passed / total * 100) if total > 0 else 0
                
                exec_times = [r.get('execution_time', 0) for r in results if r.get('execution_time') is not None]
                tokens = [r.get('token_count_estimate', 0) for r in results if r.get('token_count_estimate') is not None]
                iterations = [r.get('iteration_count', 0) for r in results if r.get('iteration_count') is not None]
                repair_attempts = [self.calculate_repair_attempts(r) for r in results]
                validation_retries = [r.get('validation_retry_count', 0) for r in results if r.get('validation_retry_count') is not None]
                
                avg_time = statistics.mean(exec_times) if exec_times else 0
                avg_tokens = statistics.mean(tokens) if tokens else 0
                avg_iterations = statistics.mean(iterations) if iterations else 0
                avg_repair_attempts = statistics.mean(repair_attempts) if repair_attempts else 0
                avg_validation_retries = statistics.mean(validation_retries) if validation_retries else 0
                
                first_try = sum(1 for r in results if r.get('success_first_try')) / total * 100 if total > 0 else 0
                self_corrected = sum(1 for r in results if r.get('self_corrected')) / total * 100 if total > 0 else 0
                
                model_performance.append({
                    'model': model,
                    'total': total,
                    'passed': passed,
                    'failed': failed,
                    'pass_rate': pass_rate,
                    'avg_time': avg_time,
                    'avg_tokens': avg_tokens,
                    'avg_iterations': avg_iterations,
                    'avg_repair_attempts': avg_repair_attempts,
                    'avg_validation_retries': avg_validation_retries,
                    'first_try': first_try,
                    'self_corrected': self_corrected
                })
            
            # Sort by pass rate (best to lowest)
            model_performance.sort(key=lambda x: x['pass_rate'], reverse=True)
            
            # Write sorted model data
            for model_data in model_performance:
                writer.writerow([
                    model_data['model'], 
                    model_data['total'], 
                    model_data['passed'], 
                    model_data['failed'], 
                    f"{model_data['pass_rate']:.2f}",
                    f"{model_data['avg_time']:.2f}", 
                    f"{model_data['avg_tokens']:.0f}", 
                    f"{model_data['avg_iterations']:.2f}",
                    f"{model_data['avg_repair_attempts']:.2f}",
                    f"{model_data['avg_validation_retries']:.2f}",
                    f"{model_data['first_try']:.2f}", 
                    f"{model_data['self_corrected']:.2f}"
                ])
            
            # Add category breakdown
            writer.writerow([])
            writer.writerow(['Model Performance by Category'])
            writer.writerow(['Model', 'Category', 'Tests', 'Pass Rate (%)'])
            
            # Sort models by their overall performance (using the same order as main table)
            sorted_models = [model_data['model'] for model_data in model_performance]
            
            for model in sorted_models:
                # Sort categories by pass rate for this model
                model_categories = []
                for category in self.aggregated_data['by_category'].keys():
                    results = [r for r in self.aggregated_data['by_model'][model] 
                             if r.get('category') == category]
                    if results:
                        passed = sum(1 for r in results if r.get('passed'))
                        pass_rate = (passed / len(results) * 100)
                        model_categories.append({
                            'category': category,
                            'tests': len(results),
                            'pass_rate': pass_rate
                        })
                
                # Sort categories by pass rate (best to lowest)
                model_categories.sort(key=lambda x: x['pass_rate'], reverse=True)
                
                for cat_data in model_categories:
                    writer.writerow([
                        model, 
                        cat_data['category'], 
                        cat_data['tests'], 
                        f"{cat_data['pass_rate']:.2f}"
                    ])
        
        print(f"✓ Saved: {output_path}")
    
    def export_rq1_agentic_impact_csv(self, monolithic_analyzer=None):
        """Export RQ1: Agentic Impact on Semantic Conformance"""
        import csv
        
        output_path = self.output_dir / 'rq1_agentic_impact.csv'
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['RQ1: Agentic Impact on Semantic Conformance'])
            writer.writerow([])
            
            # Overall comparison
            writer.writerow(['Section', 'Metric', 'Agentic', 'Monolithic', 'Delta'])
            
            agentic_stats = self.calculate_statistics()
            agentic_pass_rate = agentic_stats['pass_rate']
            agentic_first_try = agentic_stats['success_first_try_rate']
            
            if monolithic_analyzer:
                mono_stats = monolithic_analyzer.calculate_statistics()
                mono_pass_rate = mono_stats['pass_rate']
                mono_first_try = mono_stats['success_first_try_rate']
            else:
                mono_pass_rate = 0
                mono_first_try = 0
            
            delta_pass = agentic_pass_rate - mono_pass_rate
            delta_first = agentic_first_try - mono_first_try
            
            writer.writerow(['Overall', 'Pass Rate (%)', 
                           f'{agentic_pass_rate:.1f}', 
                           f'{mono_pass_rate:.1f}', 
                           f'{delta_pass:+.1f}'])
            writer.writerow(['Overall', 'First-Attempt Success (%)', 
                           f'{agentic_first_try:.1f}', 
                           f'{mono_first_try:.1f}', 
                           f'{delta_first:+.1f}'])
            
            writer.writerow([])
            writer.writerow(['Violation Distribution by Validation Category'])
            writer.writerow(['Category', 'Agentic Count', 'Monolithic Count', 'Agentic Pass Rate (%)', 'Monolithic Pass Rate (%)'])
            
            val_cats = ['syntax', 'semantics', 'event_rules', 'structural', 'topological', 'integration']
            for val_cat in val_cats:
                agentic_results = self.aggregated_data.get('by_validation_category', {}).get(val_cat, [])
                agentic_count = len(agentic_results)
                agentic_passed = sum(1 for r in agentic_results if r.get('passed'))
                agentic_rate = (agentic_passed / agentic_count * 100) if agentic_count > 0 else 0
                
                if monolithic_analyzer:
                    mono_results = monolithic_analyzer.aggregated_data.get('by_validation_category', {}).get(val_cat, [])
                    mono_count = len(mono_results)
                    mono_passed = sum(1 for r in mono_results if r.get('passed'))
                    mono_rate = (mono_passed / mono_count * 100) if mono_count > 0 else 0
                else:
                    mono_count = 0
                    mono_rate = 0
                
                writer.writerow([val_cat.replace('_', ' ').title(), 
                               agentic_count, 
                               mono_count, 
                               f'{agentic_rate:.1f}',
                               f'{mono_rate:.1f}'])
            
            writer.writerow([])
            writer.writerow(['Element Type Contribution (Inferred from Rules Violated)'])
            writer.writerow(['Element Type', 'Violations Count', 'Test Count', 'Violation Rate (%)'])
            
            element_violations = defaultdict(int)
            element_tests = defaultdict(int)
            
            for result in self.results:
                rules_violated = result.get('rules_violated', [])
                if rules_violated:
                    element_types = self.infer_agent_contribution(rules_violated)
                    for elem_type in element_types:
                        element_violations[elem_type] += 1
                        element_tests[elem_type] += 1
                else:
                    # Count tests without violations for each potential element type
                    pass
            
            for elem_type in ['StartEvent', 'EndEvent', 'Task', 'Gateway', 'IntermediateEvent']:
                viol_count = element_violations.get(elem_type, 0)
                test_count = len(self.results)  # All tests could potentially involve this element
                viol_rate = (viol_count / test_count * 100) if test_count > 0 else 0
                writer.writerow([elem_type, viol_count, test_count, f'{viol_rate:.1f}'])
            
            writer.writerow([])
            writer.writerow(['NOTES'])
            writer.writerow(['Metric', 'Availability', 'Notes'])
            writer.writerow(['Pass Rate Comparison', 'Available', 'Direct comparison from test results'])
            writer.writerow(['First-Attempt Correctness', 'Available', 'From success_first_try field'])
            writer.writerow(['Violation Distribution', 'Available', 'From validation_category and error_categories'])
            writer.writerow(['Precise Agent Attribution', 'Partial', 'Inferred from rules_violated; no direct per-agent tracking'])
        
        print(f"✓ Saved: {output_path}")
    
    def export_rq2_validation_efficiency_csv(self, monolithic_analyzer=None):
        """Export RQ2: Validation Efficiency"""
        import csv
        
        output_path = self.output_dir / 'rq2_validation_efficiency.csv'
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['RQ2: Validation Efficiency'])
            writer.writerow([])
            
            # High-level comparison if monolithic data available
            if monolithic_analyzer:
                writer.writerow(['Overall Comparison: Agentic vs Monolithic'])
                writer.writerow(['Metric', 'Agentic', 'Monolithic', 'Delta'])
                
                # Calculate aggregate metrics for both
                agentic_avg_validations = statistics.mean([len(r.get('all_validation_results', [])) for r in self.results])
                mono_avg_validations = statistics.mean([len(r.get('all_validation_results', [])) for r in monolithic_analyzer.results])
                
                agentic_avg_time = statistics.mean([r.get('execution_time', 0) for r in self.results if r.get('execution_time')])
                mono_avg_time = statistics.mean([r.get('execution_time', 0) for r in monolithic_analyzer.results if r.get('execution_time')])
                
                agentic_avg_repairs = statistics.mean([self.calculate_repair_attempts(r) for r in self.results])
                mono_avg_repairs = statistics.mean([monolithic_analyzer.calculate_repair_attempts(r) for r in monolithic_analyzer.results])
                
                writer.writerow(['Avg Validation Attempts', f'{agentic_avg_validations:.2f}', 
                               f'{mono_avg_validations:.2f}', 
                               f'{agentic_avg_validations - mono_avg_validations:+.2f}'])
                writer.writerow(['Avg Execution Time (s)', f'{agentic_avg_time:.2f}', 
                               f'{mono_avg_time:.2f}', 
                               f'{agentic_avg_time - mono_avg_time:+.2f}'])
                writer.writerow(['Avg Repair Attempts', f'{agentic_avg_repairs:.2f}', 
                               f'{mono_avg_repairs:.2f}', 
                               f'{agentic_avg_repairs - mono_avg_repairs:+.2f}'])
                
                writer.writerow([])
            
            # Repair iteration statistics (Agentic approach)
            writer.writerow(['Repair Iteration Statistics (Agentic Approach)'])
            writer.writerow(['Metric', 'Value', 'Unit'])
            
            all_repair_attempts = []
            for result in self.results:
                repair_attempts = self.calculate_repair_attempts(result)
                all_repair_attempts.append(repair_attempts)
            
            if all_repair_attempts:
                mean_repairs = statistics.mean(all_repair_attempts)
                median_repairs = statistics.median(all_repair_attempts)
                min_repairs = min(all_repair_attempts)
                max_repairs = max(all_repair_attempts)
                
                # Calculate 95th percentile
                sorted_repairs = sorted(all_repair_attempts)
                percentile_95_idx = int(len(sorted_repairs) * 0.95)
                percentile_95 = sorted_repairs[percentile_95_idx] if percentile_95_idx < len(sorted_repairs) else max_repairs
            else:
                mean_repairs = median_repairs = min_repairs = max_repairs = percentile_95 = 0
            
            writer.writerow(['Mean Repair Iterations', f'{mean_repairs:.2f}', 'iterations'])
            writer.writerow(['Median Repair Iterations', f'{median_repairs:.1f}', 'iterations'])
            writer.writerow(['95th Percentile', f'{percentile_95}', 'iterations'])
            writer.writerow(['Min Repair Iterations', f'{min_repairs}', 'iterations'])
            writer.writerow(['Max Repair Iterations', f'{max_repairs}', 'iterations'])
            
            writer.writerow([])
            writer.writerow(['Convergence Rate (% Passing Within N Iterations)'])
            writer.writerow(['Iteration Threshold', 'Pass Rate (%)', 'Count'])
            
            for n in [1, 3, 5, 10]:
                convergence_rate = self.calculate_convergence_within_n(self.results, n)
                count = sum(1 for r in self.results 
                          if r.get('passed') and r.get('iterations_to_pass') and r.get('iterations_to_pass') <= n)
                writer.writerow([f'Within {n}', f'{convergence_rate:.1f}', count])
            
            writer.writerow([])
            writer.writerow(['Error Detection by Validation Level'])
            writer.writerow(['Validation Level', 'Errors Detected', 'Percentage (%)'])
            
            level_detection = self.calculate_error_detection_by_level()
            total_errors = sum(level_detection.values())
            
            for level in ['Syntax', 'Static Semantics', 'Event Rules', 'Structural Rules', 
                         'Advanced Structural Rules', 'Topological Rules', 'Reachability']:
                count = level_detection.get(level, 0)
                percentage = (count / total_errors * 100) if total_errors > 0 else 0
                writer.writerow([level, count, f'{percentage:.1f}'])
            
            writer.writerow([])
            writer.writerow(['Repair Difficulty by Error Type'])
            writer.writerow(['Error Category', 'Mean Iterations to Fix', 'Test Count'])
            
            error_iterations = defaultdict(list)
            for result in self.results:
                error_cats = result.get('error_categories', [])
                iterations_to_pass = result.get('iterations_to_pass', 0)
                if error_cats and iterations_to_pass:
                    for error_cat in error_cats:
                        error_iterations[error_cat].append(iterations_to_pass)
            
            for error_cat in ['syntax', 'semantics', 'event', 'structural', 'topological']:
                iters = error_iterations.get(error_cat, [])
                mean_iters = statistics.mean(iters) if iters else 0
                count = len(iters)
                writer.writerow([error_cat.title(), f'{mean_iters:.2f}', count])
            
            writer.writerow([])
            writer.writerow(['Validation Overhead'])
            writer.writerow(['Metric', 'Value', 'Unit'])
            
            exec_times = [r.get('execution_time', 0) for r in self.results if r.get('execution_time')]
            tokens = [r.get('token_count_estimate', 0) for r in self.results if r.get('token_count_estimate')]
            validation_counts = [len(r.get('all_validation_results', [])) for r in self.results]
            
            avg_time = statistics.mean(exec_times) if exec_times else 0
            avg_tokens = statistics.mean(tokens) if tokens else 0
            avg_validations = statistics.mean(validation_counts) if validation_counts else 0
            
            time_per_validation = (avg_time / avg_validations) if avg_validations > 0 else 0
            tokens_per_validation = (avg_tokens / avg_validations) if avg_validations > 0 else 0
            
            writer.writerow(['Avg Execution Time', f'{avg_time:.2f}', 'seconds'])
            writer.writerow(['Avg Tokens per Test', f'{avg_tokens:.0f}', 'tokens'])
            writer.writerow(['Avg Validations per Test', f'{avg_validations:.1f}', 'validations'])
            writer.writerow(['Avg Time per Validation', f'{time_per_validation:.2f}', 'seconds'])
            writer.writerow(['Avg Tokens per Validation', f'{tokens_per_validation:.0f}', 'tokens'])
        
        print(f"✓ Saved: {output_path}")
    
    def export_rq3_cot_feedback_csv(self, monolithic_analyzer=None):
        """Export RQ3: CoT Feedback Effectiveness"""
        import csv
        
        output_path = self.output_dir / 'rq3_cot_feedback.csv'
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['RQ3: CoT Feedback Effectiveness'])
            writer.writerow([])
            
            # High-level comparison if monolithic data available
            if monolithic_analyzer:
                writer.writerow(['Overall Comparison: Agentic vs Monolithic'])
                writer.writerow(['Metric', 'Agentic (%)', 'Monolithic (%)', 'Delta'])
                
                # Calculate aggregate metrics for both
                agentic_stats = self.calculate_statistics()
                mono_stats = monolithic_analyzer.calculate_statistics()
                
                agentic_self_correction = agentic_stats['self_correction_rate']
                mono_self_correction = mono_stats['self_correction_rate']
                
                agentic_first_repair = self.calculate_first_repair_success_rate(self.results)
                mono_first_repair = monolithic_analyzer.calculate_first_repair_success_rate(monolithic_analyzer.results)
                
                writer.writerow(['Self-Correction Rate', f'{agentic_self_correction:.1f}', 
                               f'{mono_self_correction:.1f}', 
                               f'{agentic_self_correction - mono_self_correction:+.1f}'])
                writer.writerow(['First-Repair Success', f'{agentic_first_repair:.1f}', 
                               f'{mono_first_repair:.1f}', 
                               f'{agentic_first_repair - mono_first_repair:+.1f}'])
                
                writer.writerow([])
            
            # Available metrics (Agentic approach)
            writer.writerow(['Available Metrics (Agentic Approach)'])
            writer.writerow(['Metric', 'Value (%)', 'Count', 'Notes'])
            
            stats = self.calculate_statistics()
            self_correction_rate = stats['self_correction_rate']
            self_correction_count = sum(1 for r in self.results if r.get('self_corrected'))
            
            first_repair_success = self.calculate_first_repair_success_rate(self.results)
            first_repair_count = sum(1 for r in self.results 
                                    if len(r.get('validation_history', [])) >= 2 
                                    and not r.get('validation_history', [])[0].get('valid')
                                    and r.get('validation_history', [])[1].get('valid'))
            
            writer.writerow(['Self-Correction Rate', 
                           f'{self_correction_rate:.1f}', 
                           self_correction_count,
                           'Scenarios that passed after repair'])
            writer.writerow(['First-Repair Success', 
                           f'{first_repair_success:.1f}', 
                           first_repair_count,
                           'Violations fixed on first repair attempt'])
            
            writer.writerow([])
            writer.writerow(['Self-Correction by Validation Category'])
            writer.writerow(['Category', 'Total Tests', 'Self-Corrected', 'Self-Correction Rate (%)'])
            
            for val_cat in ['syntax', 'semantics', 'event_rules', 'structural', 'topological', 'integration']:
                results = self.aggregated_data.get('by_validation_category', {}).get(val_cat, [])
                total = len(results)
                self_corrected = sum(1 for r in results if r.get('self_corrected'))
                rate = (self_corrected / total * 100) if total > 0 else 0
                writer.writerow([val_cat.replace('_', ' ').title(), total, self_corrected, f'{rate:.1f}'])
            
            writer.writerow([])
            writer.writerow(['Self-Correction by Difficulty Level'])
            writer.writerow(['Difficulty Level', 'Total Tests', 'Self-Corrected', 'Self-Correction Rate (%)'])
            
            difficulty_levels = sorted([k for k in self.aggregated_data.get('by_difficulty_level', {}).keys() if k > 0])
            for level in difficulty_levels:
                results = self.aggregated_data.get('by_difficulty_level', {}).get(level, [])
                total = len(results)
                self_corrected = sum(1 for r in results if r.get('self_corrected'))
                rate = (self_corrected / total * 100) if total > 0 else 0
                writer.writerow([f'Level {level}', total, self_corrected, f'{rate:.1f}'])
        
        print(f"✓ Saved: {output_path}")
    
    def export_analysis_feasibility_csv(self):
        """Export documentation of metric feasibility"""
        import csv
        
        output_path = self.output_dir / 'analysis_feasibility.csv'
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            writer.writerow(['BPMN Agent Research Metrics - Feasibility Analysis'])
            writer.writerow([])
            writer.writerow(['Research Question', 'Metric', 'Availability', 'Calculation Method', 'Notes'])
            
            # RQ1 Metrics
            writer.writerow(['RQ1: Agentic Impact', 'Pass Rate', 'Available', 
                           'Direct from test results', 'Compares agentic vs monolithic'])
            writer.writerow(['RQ1: Agentic Impact', 'First-Attempt Correctness', 'Available', 
                           'success_first_try field', 'Measures initial generation quality'])
            writer.writerow(['RQ1: Agentic Impact', 'Violation Distribution', 'Available', 
                           'validation_category + error_categories', 'Full breakdown by level'])
            writer.writerow(['RQ1: Agentic Impact', 'Agent-Specific Contribution', 'Partial', 
                           'Inferred from rules_violated', 'No direct per-agent tracking; requires re-instrumentation'])
            
            # RQ2 Metrics
            writer.writerow(['RQ2: Validation Efficiency', 'Repair Iteration Count', 'Available', 
                           'Calculated from validation_history', 'Mean, median, 95th percentile'])
            writer.writerow(['RQ2: Validation Efficiency', 'Convergence Rate', 'Available', 
                           'iterations_to_pass field', '% passing within N iterations'])
            writer.writerow(['RQ2: Validation Efficiency', 'Error Detection by Level', 'Available', 
                           'Parse validation_errors', 'Identifies which level caught errors'])
            writer.writerow(['RQ2: Validation Efficiency', 'Repair Difficulty', 'Available', 
                           'iterations_to_pass by error_category', 'Mean iterations per error type'])
            writer.writerow(['RQ2: Validation Efficiency', 'Validation Overhead', 'Available', 
                           'execution_time + token_count_estimate', 'Time and token cost per validation'])
            
            # RQ3 Metrics
            writer.writerow(['RQ3: CoT Feedback', 'Self-Correction Rate', 'Available', 
                           'self_corrected field', 'Scenarios passing after repair'])
            writer.writerow(['RQ3: CoT Feedback', 'First-Repair Success', 'Available', 
                           'Calculated from validation_history', '% fixed on first repair'])
            
        
        print(f"✓ Saved: {output_path}")
    
    
    def run_analysis(self, research_mode=False, monolithic_dir=None, rq_filter='all'):
        """Run complete analysis pipeline"""
        if not self.load_results():
            return
        
        self.aggregate_data()
        self.print_summary()
        
        # Organize output directory by model/run if available
        if self.model_name and self.run_id:
            self.output_dir = self.output_dir / self.model_name / self.run_id
        elif self.model_name:
            self.output_dir = self.output_dir / self.model_name / "aggregate"
        else:
            self.output_dir = self.output_dir / "all_models"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if research_mode:
            # Research mode: Generate RQ-specific CSVs
            print("\n📊 Research Mode: Generating RQ analysis CSVs...")
            
            # Load monolithic results if provided
            monolithic_analyzer = None
            if monolithic_dir:
                print(f"Loading monolithic baseline from {monolithic_dir}...")
                # Load monolithic results without run_id matching (different run timestamps)
                monolithic_analyzer = BenchmarkAnalyzer(
                    results_dir=monolithic_dir,
                    output_dir=self.output_dir,
                    model_name=self.model_name,
                    run_id=None  # Load any run for this model
                )
                if monolithic_analyzer.load_results():
                    monolithic_analyzer.aggregate_data()
                    print(f"✓ Monolithic baseline loaded ({len(monolithic_analyzer.results)} tests)")
                else:
                    print("⚠ Could not load monolithic baseline, proceeding without comparison")
                    monolithic_analyzer = None
            
            # Generate RQ CSVs based on filter
            if rq_filter in ['all', '1']:
                self.export_rq1_agentic_impact_csv(monolithic_analyzer)
            
            if rq_filter in ['all', '2']:
                self.export_rq2_validation_efficiency_csv(monolithic_analyzer)
            
            if rq_filter in ['all', '3']:
                self.export_rq3_cot_feedback_csv(monolithic_analyzer)
            
            if rq_filter == 'all':
                self.export_analysis_feasibility_csv()
            
            print(f"\n✓ Research analysis complete. Results saved in: {self.output_dir}/")
        else:
            # Standard mode: Only export existing CSVs
            self.export_research_summary_table()
            self.export_summary_table()
            
            # If multiple models exist, also export comparison table
            if len(self.get_models()) >= 2:
                self.export_model_comparison_table()
            
            print(f"\n✓ Analysis complete (CSVs only). Results saved in: {self.output_dir}/")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze BPMN agent benchmark results (CSV outputs only)"
    )
    
    parser.add_argument(
        "--results-dir",
        type=str,
        default="benchmark_results",
        help="Directory containing benchmark result files"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Directory to save CSV outputs"
    )
    
    # Removed: --format (no figures generated)
    
    parser.add_argument(
        "--model",
        type=str,
        help="Analyze results for a specific model only"
    )
    
    parser.add_argument(
        "--run-id",
        type=str,
        help="Analyze results for a specific run ID only (requires --model)"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List all available models in the results directory"
    )
    
    parser.add_argument(
        "--each-run",
        action="store_true",
        help="Generate individual analysis for each model run inside results-dir"
    )
    
    parser.add_argument(
        "--research-mode",
        action="store_true",
        help="Enable RQ-specific CSV generation for research questions"
    )
    
    parser.add_argument(
        "--monolithic-dir",
        type=str,
        help="Path to monolithic benchmark results for comparison (used with --research-mode)"
    )
    
    parser.add_argument(
        "--rq",
        type=str,
        default="all",
        choices=["all", "1", "2", "3"],
        help="Select specific research question to analyze (1, 2, 3, or 'all')"
    )
    
    parser.add_argument(
        "--aggregate",
        action="store_true",
        help="Generate aggregate analysis across all models (requires --research-mode)"
    )
    
    args = parser.parse_args()
    
    # List models and exit
    if args.list_models:
        list_available_models(args.results_dir)
        return
    
    # Validate run-id requires model
    if args.run_id and not args.model:
        print("Error: --run-id requires --model to be specified")
        return
    
    # Aggregate mode: analyze all models combined
    if args.aggregate:
        if not args.research_mode:
            print("Error: --aggregate requires --research-mode")
            return
        
        print("\n" + "="*80)
        print("AGGREGATE ANALYSIS: All Models Combined")
        print("="*80 + "\n")
        
        # Load all agentic results
        print("Loading agentic results from all models...")
        agentic_analyzer = BenchmarkAnalyzer(
            results_dir=args.results_dir,
            output_dir=args.output_dir,
            model_name=None,  # Load all models
            run_id=None
        )
        if not agentic_analyzer.load_results():
            print("⚠ Could not load agentic results")
            return
        
        agentic_analyzer.aggregate_data()
        print(f"✓ Loaded {len(agentic_analyzer.results)} agentic tests across {len(agentic_analyzer.get_models())} models")
        
        # Load all monolithic results
        monolithic_analyzer = None
        if args.monolithic_dir:
            print(f"\nLoading monolithic baseline from all models...")
            monolithic_analyzer = BenchmarkAnalyzer(
                results_dir=args.monolithic_dir,
                output_dir=args.output_dir,
                model_name=None,  # Load all models
                run_id=None
            )
            if monolithic_analyzer.load_results():
                monolithic_analyzer.aggregate_data()
                print(f"✓ Loaded {len(monolithic_analyzer.results)} monolithic tests across {len(monolithic_analyzer.get_models())} models")
            else:
                print("⚠ Could not load monolithic baseline")
                monolithic_analyzer = None
        
        # Print summary
        agentic_analyzer.print_summary()
        if monolithic_analyzer:
            print("\n" + "="*80)
            print("MONOLITHIC BASELINE SUMMARY")
            print("="*80)
            monolithic_analyzer.print_summary()
        
        # Generate aggregate research CSVs
        output_dir = Path(args.output_dir) / "aggregate_all_models"
        output_dir.mkdir(parents=True, exist_ok=True)
        agentic_analyzer.output_dir = output_dir
        
        print(f"\n📊 Generating aggregate research CSVs...")
        
        if args.rq in ['all', '1']:
            agentic_analyzer.export_rq1_agentic_impact_csv(monolithic_analyzer)
        
        if args.rq in ['all', '2']:
            agentic_analyzer.export_rq2_validation_efficiency_csv(monolithic_analyzer)
        
        if args.rq in ['all', '3']:
            agentic_analyzer.export_rq3_cot_feedback_csv(monolithic_analyzer)
        
        if args.rq == 'all':
            agentic_analyzer.export_analysis_feasibility_csv()
        
        print(f"\n✓ Aggregate analysis complete. Results saved in: {output_dir}/")
        return
    
    # Batch mode: analyze each model run individually
    if args.each_run:
        results_path = Path(args.results_dir)
        if not results_path.exists():
            print(f"⚠ Results directory not found: {args.results_dir}")
            return
        
        print("\nRunning per-run analysis for all models and runs found...")
        print("-" * 80)
        for model_dir in sorted(results_path.iterdir()):
            if model_dir.is_dir() and not model_dir.name.startswith('.'):
                model_name = model_dir.name
                for run_dir in sorted(model_dir.iterdir()):
                    if run_dir.is_dir() and not run_dir.name.startswith('.'):
                        result_file = run_dir / "results.json"
                        if result_file.exists():
                            run_id = run_dir.name
                            print(f"\n🧪 Analyzing model='{model_name}', run='{run_id}'")
                            analyzer = BenchmarkAnalyzer(
                                results_dir=args.results_dir,
                                output_dir=args.output_dir,
                                model_name=model_name,
                                run_id=run_id
                            )
                            analyzer.run_analysis(
                                research_mode=args.research_mode,
                                monolithic_dir=args.monolithic_dir,
                                rq_filter=args.rq
                            )
        print("\n✓ Per-run analysis complete.")
        return
    
    analyzer = BenchmarkAnalyzer(
        results_dir=args.results_dir,
        output_dir=args.output_dir,
        model_name=args.model,
        run_id=args.run_id
    )
    
    analyzer.run_analysis(
        research_mode=args.research_mode,
        monolithic_dir=args.monolithic_dir,
        rq_filter=args.rq
    )


def list_available_models(results_dir: str):
    """List all available models and their runs"""
    results_path = Path(results_dir)
    
    if not results_path.exists():
        print(f"⚠ Results directory not found: {results_dir}")
        return
    
    print(f"\n{'='*80}")
    print(f"AVAILABLE MODELS AND RUNS")
    print(f"{'='*80}\n")
    
    models_found = False
    for model_dir in sorted(results_path.iterdir()):
        if model_dir.is_dir() and not model_dir.name.startswith('.'):
            models_found = True
            print(f"📊 Model: {model_dir.name}")
            
            runs = []
            for run_dir in sorted(model_dir.iterdir()):
                if run_dir.is_dir() and not run_dir.name.startswith('.'):
                    result_file = run_dir / "results.json"
                    if result_file.exists():
                        try:
                            with open(result_file, 'r') as f:
                                data = json.load(f)
                                if "metadata" in data:
                                    metadata = data["metadata"]
                                    runs.append({
                                        "run_id": run_dir.name,
                                        "timestamp": metadata.get("timestamp", "N/A"),
                                        "total_tests": metadata.get("total_tests", 0),
                                        "passed": metadata.get("passed", 0),
                                        "failed": metadata.get("failed", 0)
                                    })
                        except:
                            runs.append({"run_id": run_dir.name, "timestamp": "N/A"})
            
            if runs:
                for run in runs:
                    timestamp = run.get("timestamp", "N/A")
                    if timestamp != "N/A" and "T" in timestamp:
                        timestamp = timestamp.split("T")[0]  # Show date only
                    
                    if "total_tests" in run:
                        pass_rate = (run["passed"] / run["total_tests"] * 100) if run["total_tests"] > 0 else 0
                        print(f"  └─ Run: {run['run_id']}")
                        print(f"     Date: {timestamp}, Tests: {run['total_tests']}, Pass Rate: {pass_rate:.1f}%")
                    else:
                        print(f"  └─ Run: {run['run_id']} (Date: {timestamp})")
            else:
                print(f"  └─ No runs found")
            print()
    
    if not models_found:
        print("⚠ No models found in results directory")
    
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
