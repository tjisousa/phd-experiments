"""
BPMN Agent Configuration
Simple configuration constants for model selection across all agents.
Usage:
    from bpmn_agent.config import MODEL
    
    agent = Agent(
        name="my_agent",
        model=MODEL,
        ...
    )
"""
from google.adk.models.lite_llm import LiteLlm

# Set OpenRouter API key and base URL
OR_KEY = "OPENROUTER_API_KEY"
OR_API="https://openrouter.ai/api/v1"

# Primary model used across all agents and sub-agents
# MODEL = "gemini-2.5-flash-lite"
# MODEL = "gemini-2.5-flash"
# MODEL = "gemini-2.5-pro"
# MODEL = LiteLlm(model="openai/gpt-5-2025-08-07", reasoning_effort="low")
# MODEL = LiteLlm(model="openai/gpt-5-nano-2025-08-07")
# MODEL = LiteLlm(model="openai/gpt-5-mini-2025-08-07")
# MODEL = LiteLlm(model="openrouter/qwen/qwen3-coder-30b-a3b-instruct", api_key=OR_KEY, api_base=OR_API)
# MODEL = LiteLlm(model="openrouter/x-ai/grok-4-fast", api_key=OR_KEY, api_base=OR_API)
MODEL = LiteLlm(model="openrouter/z-ai/glm-4.6", api_key=OR_KEY, api_base=OR_API)

MODELS = []


if hasattr(MODEL, 'model'):
    model_name = MODEL.model
else:
    model_name = str(MODEL)
BENCHMARK_NAME = model_name + "-no-repair"

__all__ = ["MODEL", "MODELS", "BENCHMARK_NAME"]
