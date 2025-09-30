"""
LLM Adapter: centralize calls to LLM providers (OpenAI GPT-4 or Google PaLM).

Responsibilities:
- Prompt assembly (system prompt + truncated context)
- Locale handling (respond in Hindi/Tamil/etc)
- Token budgeting and request timeouts
- Fallback strategy for rate limits or provider errors
- Return structured data: (reply_text, metadata)
"""

import os
import logging
from typing import List, Tuple

# Example using OpenAI client (but we must keep an adapter interface)
import openai
from config import Config

openai.api_key = Config.OPENAI_API_KEY

SYSTEM_PROMPT = "You are a helpful customer support assistant. Be concise and friendly."

def call_llm(context_messages: List[dict], user_message: str, locale: str = "en_IN") -> Tuple[str, dict]:
    """
    Query the LLM and return a tuple (reply_text, metadata).

    Inputs:
      - context_messages: list of {"role": "user"/"assistant", "content": "..."}
      - user_message: current user text
      - locale: user preferred locale (e.g., "hi_IN" — used in system prompt)

    Outputs:
      - reply_text: assistant reply string
      - metadata: dict: {model, usage, tokens, latency_ms, fallback}
    """
    # 1) Build messages with system prompt + context (truncate to last N)
    messages = [{"role": "system", "content": SYSTEM_PROMPT + f" Respond in {locale} if possible."}]
    messages.extend(context_messages[-Config.MAX_CONTEXT_MESSAGES:])
    messages.append({"role": "user", "content": user_message})

    try:
        # Keep a firm timeout to meet SLA
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=300,
            temperature=0.25,
            timeout=Config.LLM_REQUEST_TIMEOUT_SEC
        )
        reply = resp["choices"][0]["message"]["content"].strip()
        meta = {"model": "gpt-4", "usage": resp.get("usage"), "finish_reason": resp["choices"][0].get("finish_reason")}
        return reply, meta
    except Exception as exc:
        logging.exception("LLM call failed; attempting fallback.")
        # Fallback logic: attempt to use a faster model or return graceful message
        try:
            fallback_resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.25,
                timeout=Config.LLM_REQUEST_TIMEOUT_SEC
            )
            reply = fallback_resp["choices"][0]["message"]["content"].strip()
            return reply, {"model": "gpt-3.5-turbo", "fallback": True}
        except Exception as e2:
            logging.exception("Fallback also failed.")
            return ("We're unable to process this request right now. We'll escalate to a human agent." , {"error": str(e2)})
