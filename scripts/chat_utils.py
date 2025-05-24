# Helper utilities for VerityOS chat mode
from llm_router import query_model
from scripts.memory_core_module import get_combined_context

def summarize_history(entries: list[str]) -> str:
    """
    Summarize a list of conversation entries into 3 concise bullet points.
    """
    prompt = "Summarize the following conversation history into 3 bullet points:\n" + "\n".join(entries)
    return query_model(prompt).strip()

def trim_context(entries: list[tuple[str, str]], max_tokens: int = 4096) -> list[tuple[str, str]]:
    """
    Trim the conversation history entries to fit within a token limit.
    This is a placeholder; implement token counting/trimming logic as needed.
    """
    # TODO: Implement token-based trimming
    return entries

def inject_long_term_memory(agent: str, user_input: str) -> str:
    """
    Fetch and return relevant long-term memory context when the user refers to past conversation.
    """
    memory_context = get_combined_context(agent)
    return memory_context
