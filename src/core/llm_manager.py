"""
LLM Manager: switch between Gemini (Google GenAI) and local Ollama (qwen2.5:7b).

Logic:
- Primary: Gemini (if GOOGLE_API_KEY is available and USE_GEMINI_PRIMARY=True).
- Fallback: Ollama (HTTP API at OLLAMA_BASE_URL, default http://localhost:11434).

This module exposes a simple `generate_answer` function that other parts
of the system (e.g., RAG engine, web app) can call.
"""

from __future__ import annotations

import os
from typing import Optional

import requests
from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMManager:
    def __init__(self):
        self.use_gemini_primary = settings.USE_GEMINI_PRIMARY
        self.google_api_key = settings.GOOGLE_API_KEY
        self.gemini_model_name = settings.LLM_MODEL_NAME

        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.ollama_model_name = settings.OLLAMA_MODEL_NAME

        self._gemini_client: Optional[ChatGoogleGenerativeAI] = None

    def _get_gemini_client(self) -> ChatGoogleGenerativeAI:
        if self._gemini_client is None:
            if not self.google_api_key:
                raise RuntimeError("GOOGLE_API_KEY is not set.")
            logger.info(f"Initializing Gemini client: {self.gemini_model_name}")
            self._gemini_client = ChatGoogleGenerativeAI(
                model=self.gemini_model_name,
                temperature=0.7,
                max_output_tokens=512,
                google_api_key=self.google_api_key,
                convert_system_message_to_human=True,
            )
        return self._gemini_client

    def _call_gemini(self, prompt: str) -> str:
        client = self._get_gemini_client()
        logger.info("Calling Gemini LLM...")
        resp = client.invoke(prompt)
        # LangChain ChatGoogleGenerativeAI usually returns a Message-like object
        try:
            return resp.content
        except Exception:
            return str(resp)

    def _call_ollama(self, prompt: str) -> str:
        """
        Call local Ollama HTTP API.
        Assumes Ollama is running, e.g. `ollama serve` on D:/Ollama but reachable at localhost:11434.
        """
        url = f"{self.ollama_base_url}/v1/chat/completions"
        logger.info(f"Calling Ollama model: {self.ollama_model_name} at {url}")
        payload = {
            "model": self.ollama_model_name,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        try:
            res = requests.post(url, json=payload, timeout=120)
            res.raise_for_status()
            data = res.json()
            # OpenAI-style response
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama call failed: {e}", exc_info=True)
            raise

    def generate_answer(self, prompt: str) -> str:
        """
        Generate answer using primary model with fallback.
        """
        if self.use_gemini_primary and self.google_api_key:
            try:
                return self._call_gemini(prompt)
            except Exception as e:
                logger.error(f"Gemini failed, falling back to Ollama: {e}", exc_info=True)

        # Fallback or primary if Gemini disabled
        return self._call_ollama(prompt)


llm_manager = LLMManager()


