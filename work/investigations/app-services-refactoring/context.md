## Objective
Investigate the `app-services` zone for refactoring opportunities, coupling issues, and
compliance with the strategy pattern for swappable LLM providers.

## Scope
Files in `app/llms/**`, `app/knowledge/**`, `app/embeddings/**`, `app/prompts/**` (18 files):
- LLM provider clients and wrappers (aws_chat, litellm_wrapper, chats, clients, chat_events, model_config, default_models, image_description_service)
- Knowledge management (pack, markdown, documents)
- Embeddings (client, documents, in_memory, model)
- Prompt management (prompts, prompts_factory, inspirations)

## Key Questions
- Is the strategy/abstract-base-class pattern used for LLM provider swappability?
- Are any files tightly coupled to a specific provider?
- Do functions stay under the 20-line limit?
- Is there mutable global state?
- Are there code smells (god objects, poor separation of concerns, duplication)?
- Is there an ongoing migration/refactoring in progress (e.g. LiteLLM migration)?

## Rules from CHARTER.yaml
- Allowed: constructor DI, type hints, abstract base classes, strategy pattern, functions <20 lines
- Forbidden: tight LLM provider coupling, eval/exec on user input, hardcoded secrets, mutable global state
- Max file lines: 300, target test coverage: 80%

## Expected Output
An assertion-backed markdown report (.a.md) with evidence for each assertion.
Use the assertion-backed-markdown skill to produce the report.
