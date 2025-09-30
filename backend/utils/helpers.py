"""
General helpers used across the app:
- prompt truncation
- context assembly
- small util functions
"""

def truncate_context(messages, max_messages=8):
    """Keep the last N messages for LLM context window."""
    return messages[-max_messages:]
