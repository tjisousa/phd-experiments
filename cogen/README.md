# A Semantically-Grounded Agentic Framework for Assisting BPMN Model Instance Execution

## Setup & Requirements

### Prerequisites
- Python 3.9+
- Familiarity with Python environments and dependency management

### Environment Setup
Create a `.env` file in both the project root and the `bpmn_agent/` folder with the following API keys:
```
GOOGLE_GENAI_USE_VERTEXAI=
GOOGLE_API_KEY=
OPENAI_API_KEY=
```

**Note**: OpenRouter API key is also needed for running some models (Qwen, Grok, GLM) and is configured in `bpmn_agent/config.py`.

### Key Dependencies
- Google ADK (Agentic Development Kit)
- LiteLLM for multi-model support
- Standard libraries: asyncio, json, pathlib, statistics

### Model Configuration
Models are configured in `bpmn_agent/config.py`. The system supports multiple LLM providers:
- Google Gemini (2.5 Flash, Pro)
- OpenAI GPT-5 variants
- OpenRouter models (Qwen, Grok, GLM)

## Running Experiments

### Command-Line Interface

```bash
# List all available test scenarios
python scripts/run_scenario_tests.py --list

# Run a single scenario
python scripts/run_scenario_tests.py --scenario l1_simple_linear_process

# Run scenarios by difficulty level (1-6)
python scripts/run_scenario_tests.py --difficulty 1

# Run scenarios by validation category
python scripts/run_scenario_tests.py --validation-category syntax

# Run all scenarios (full benchmark)
python scripts/run_scenario_tests.py --all --max-iterations 25

# Analyze results for all models
python scripts/analyze_results.py --research-mode --aggregate

# Analyze specific model results
python scripts/analyze_results.py --model gemini_2.5_flash --research-mode

# Generate RQ-specific analysis
python scripts/analyze_results.py --research-mode --rq 1 --aggregate
```

### Key Options
- `--max-iterations N`: Limit agent iterations per scenario (default: 25)
- `--research-mode`: Generate RQ-specific CSV analysis
- `--aggregate`: Combine results across all models
- `--monolithic-dir PATH`: Compare against monolithic baseline

## Data & Results

### Pre-computed Experimental Results Structure

```
analysis/
├── benchmark_ours/              # Agentic approach results
│   ├── gemini_2.5_flash/
│   ├── gemini_2.5_pro/
│   ├── openai_gpt_5_2025_08_07/
│   └── [other models]/
│       ├── all_runs.jsonl       # Metadata from all runs
│       └── [run_timestamp]/
│           └── results.json     # Detailed test results
│
├── benchmark_mono/              # Monolithic baseline results
│   └── [same structure]
│
└── results_final_analysis/
    └── aggregate_all_models/
        ├── rq1_agentic_impact.csv
        ├── rq2_validation_efficiency.csv
        └── rq3_cot_feedback.csv
```

### Result Files Contain
- **Test metadata**: model, timestamp, pass/fail rates
- **Validation metrics**: iteration counts, repair attempts, convergence rates
- **Error analysis**: violation categories, rules violated, error detection levels
- **Generated code**: BPMN process code and validation responses

### Analysis Outputs
CSV analysis files provide research-ready summaries for each research question:
- **RQ1**: Agentic impact on semantic conformance
- **RQ2**: Validation efficiency metrics
- **RQ3**: Chain-of-thought feedback effectiveness
