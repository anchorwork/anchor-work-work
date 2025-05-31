"""
utils/llm_client.py

Unified client for interacting with OpenAI (and future LLM providers).
Supports sync, async, and streaming calls, robust error handling, logging, and easy extensibility.
Integrates with model_service.py for agent/task-based model selection.
"""

import os
import openai
import logging
import asyncio
import random
import time
from typing import Optional, Dict, Any, List, Union, Callable, Generator

from utils.model_service import (
    model_service,  # Global instance
    get_default_model,
    choose_model,
)

logger = logging.getLogger(__name__)

# --- Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
DEFAULT_MODEL = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-2024-11-20")
MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
RETRY_BACKOFF = float(os.getenv("OPENAI_RETRY_BACKOFF", "2.0"))
DEFAULT_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "30"))

openai.api_key = OPENAI_API_KEY
openai.api_base = OPENAI_API_BASE

# --- Exceptions ---
class LLMClientError(Exception):
    """Custom exception for LLM client errors."""

# --- Core Client ---
class LLMClient:
    """
    Unified client for LLM (OpenAI) chat/completion.
    Integrates with model_service for model selection.
    Usage:
        client = LLMClient()
        model = get_default_model(agent_id="coder")
        response = client.chat(messages=[{"role": "user", "content": "Hello!"}], model=model)
    """

    def __init__(self, default_model: Optional[str] = None):
        self.default_model = default_model or DEFAULT_MODEL

    def _select_model(self, agent_id: Optional[str] = None, prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        """
        Select the model using model_service logic.
        """
        if model:
            return model
        if prompt:
            return choose_model(prompt)
        if agent_id:
            return get_default_model(agent_id)
        return self.default_model

    def chat(
        self,
        messages: List[Dict[str, str]],
        agent_id: Optional[str] = None,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT,
        stream: bool = False,
        on_token: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], Generator[str, None, None]]:
        """
        Synchronous chat completion (with optional streaming).
        If stream=True, returns a generator yielding tokens.
        """
        selected_model = self._select_model(agent_id, prompt, model)
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.debug(f"OpenAI chat call (attempt {attempt}): model={selected_model}, messages={messages}")
                if stream:
                    # Streaming mode: yield tokens as they arrive
                    response = openai.ChatCompletion.create(
                        model=selected_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        timeout=timeout,
                        stream=True,
                        **kwargs
                    )
                    def token_generator():
                        for chunk in response:
                            delta = chunk["choices"][0]["delta"]
                            token = delta.get("content", "")
                            if token:
                                if on_token:
                                    on_token(token)
                                yield token
                    return token_generator()
                else:
                    response = openai.ChatCompletion.create(
                        model=selected_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        timeout=timeout,
                        **kwargs
                    )
                    return response
            except openai.error.RateLimitError as e:
                logger.warning(f"OpenAI rate limit error (attempt {attempt}): {e}")
                if attempt == MAX_RETRIES:
                    logger.error("Max retries reached for OpenAI chat (rate limit).")
                    raise LLMClientError(f"OpenAI chat failed due to rate limit: {e}")
                sleep_time = RETRY_BACKOFF * attempt + random.uniform(0, 1)
                time.sleep(sleep_time)
            except openai.error.Timeout as e:
                logger.error(f"OpenAI timeout error: {e}")
                raise LLMClientError(f"OpenAI chat timed out: {e}")
            except Exception as e:
                logger.warning(f"OpenAI chat error (attempt {attempt}): {e}")
                if attempt == MAX_RETRIES:
                    logger.error("Max retries reached for OpenAI chat.")
                    raise LLMClientError(f"OpenAI chat failed: {e}")
                time.sleep(RETRY_BACKOFF * attempt + random.uniform(0, 1))

    async def chat_async(
        self,
        messages: List[Dict[str, str]],
        agent_id: Optional[str] = None,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: int = DEFAULT_TIMEOUT,
        stream: bool = False,
        on_token: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], Callable[[], AsyncGenerator[str, None]]]:
        """
        Asynchronous chat completion (with optional streaming).
        If stream=True, returns an async generator yielding tokens.
        """
        selected_model = self._select_model(agent_id, prompt, model)
        loop = asyncio.get_running_loop()
        if stream:
            # Streaming mode: async generator
            def sync_token_gen():
                response = openai.ChatCompletion.create(
                    model=selected_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout,
                    stream=True,
                    **kwargs
                )
                for chunk in response:
                    delta = chunk["choices"][0]["delta"]
                    token = delta.get("content", "")
                    if token:
                        if on_token:
                            on_token(token)
                        yield token

            async def async_token_gen():
                for token in await loop.run_in_executor(None, lambda: list(sync_token_gen())):
                    yield token
            return async_token_gen()
        else:
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    logger.debug(f"OpenAI async chat call (attempt {attempt}): model={selected_model}, messages={messages}")
                    response = await loop.run_in_executor(
                        None,
                        lambda: openai.ChatCompletion.create(
                            model=selected_model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            timeout=timeout,
                            **kwargs
                        )
                    )
                    return response
                except openai.error.RateLimitError as e:
                    logger.warning(f"OpenAI async rate limit error (attempt {attempt}): {e}")
                    if attempt == MAX_RETRIES:
                        logger.error("Max retries reached for OpenAI async chat (rate limit).")
                        raise LLMClientError(f"OpenAI async chat failed due to rate limit: {e}")
                    sleep_time = RETRY_BACKOFF * attempt + random.uniform(0, 1)
                    await asyncio.sleep(sleep_time)
                except openai.error.Timeout as e:
                    logger.error(f"OpenAI async timeout error: {e}")
                    raise LLMClientError(f"OpenAI async chat timed out: {e}")
                except Exception as e:
                    logger.warning(f"OpenAI async chat error (attempt {attempt}): {e}")
                    if attempt == MAX_RETRIES:
                        logger.error("Max retries reached for OpenAI async chat.")
                        raise LLMClientError(f"OpenAI async chat failed: {e}")
                    await asyncio.sleep(RETRY_BACKOFF * attempt + random.uniform(0, 1))

    def simple_completion(
        self,
        prompt: str,
        agent_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
        timeout: int = DEFAULT_TIMEOUT,
        **kwargs
    ) -> str:
        """
        Synchronous text completion (legacy models).
        """
        selected_model = self._select_model(agent_id, prompt, model)
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.debug(f"OpenAI completion call (attempt {attempt}): {prompt}")
                response = openai.Completion.create(
                    model=selected_model,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout,
                    **kwargs
                )
                return response.choices[0].text.strip()
            except openai.error.RateLimitError as e:
                logger.warning(f"OpenAI completion rate limit error (attempt {attempt}): {e}")
                if attempt == MAX_RETRIES:
                    logger.error("Max retries reached for OpenAI completion (rate limit).")
                    raise LLMClientError(f"OpenAI completion failed due to rate limit: {e}")
                sleep_time = RETRY_BACKOFF * attempt + random.uniform(0, 1)
                time.sleep(sleep_time)
            except openai.error.Timeout as e:
                logger.error(f"OpenAI completion timeout error: {e}")
                raise LLMClientError(f"OpenAI completion timed out: {e}")
            except Exception as e:
                logger.warning(f"OpenAI completion error (attempt {attempt}): {e}")
                if attempt == MAX_RETRIES:
                    logger.error("Max retries reached for OpenAI completion.")
                    raise LLMClientError(f"OpenAI completion failed: {e}")
                time.sleep(RETRY_BACKOFF * attempt + random.uniform(0, 1))

    async def simple_completion_async(
        self,
        prompt: str,
        agent_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
        timeout: int = DEFAULT_TIMEOUT,
        **kwargs
    ) -> str:
        """
        Asynchronous text completion (legacy models).
        """
        selected_model = self._select_model(agent_id, prompt, model)
        loop = asyncio.get_running_loop()
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.debug(f"OpenAI async completion call (attempt {attempt}): {prompt}")
                response = await loop.run_in_executor(
                    None,
                    lambda: openai.Completion.create(
                        model=selected_model,
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        timeout=timeout,
                        **kwargs
                    )
                )
                return response.choices[0].text.strip()
            except openai.error.RateLimitError as e:
                logger.warning(f"OpenAI async completion rate limit error (attempt {attempt}): {e}")
                if attempt == MAX_RETRIES:
                    logger.error("Max retries reached for OpenAI async completion (rate limit).")
                    raise LLMClientError(f"OpenAI async completion failed due to rate limit: {e}")
                sleep_time = RETRY_BACKOFF * attempt + random.uniform(0, 1)
                await asyncio.sleep(sleep_time)
            except openai.error.Timeout as e:
                logger.error(f"OpenAI async completion timeout error: {e}")
                raise LLMClientError(f"OpenAI async completion timed out: {e}")
            except Exception as e:
                logger.warning(f"OpenAI async completion error (attempt {attempt}): {e}")
                if attempt == MAX_RETRIES:
                    logger.error("Max retries reached for OpenAI async completion.")
                    raise LLMClientError(f"OpenAI async completion failed: {e}")
                await asyncio.sleep(RETRY_BACKOFF * attempt + random.uniform(0, 1))

# --- Usage Example ---
# client = LLMClient()
# model = get_default_model(agent_id="coder")
# response = client.chat([{"role": "user", "content": "Hello!"}], model=model)
# print(response["choices"][0]["message"]["content"])
#
# # Streaming example:
# for token in client.chat([{"role": "user", "content": "Stream this!"}], stream=True):
#     print(token, end="", flush=True)

# --- For backwards compatibility ---
default_llm_client = LLMClient()

def chat_sync(*args, **kwargs):
    return default_llm_client.chat(*args, **kwargs)

async def chat_async(*args, **kwargs):
    return await default_llm_client.chat_async(*args, **kwargs)