from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml
from dotenv import load_dotenv
from openai import OpenAI


CONFIG_PATH = Path("config/app_config.yaml")


@dataclass
class AppConfig:
    app_title: str
    app_version: str
    model_identifier: str
    temperature: float
    max_tokens: int
    timeout: int
    message_window: int
    forbidden_topics: List[str]


def load_config(path: Path = CONFIG_PATH) -> AppConfig:
    """Load the YAML config and map it into a flat dataclass."""
    raw: Dict = yaml.safe_load(path.read_text(encoding="utf8"))

    app_cfg = raw.get("app", {})
    model_cfg = raw.get("model", {})
    memory_cfg = raw.get("memory", {})
    safety_cfg = raw.get("safety", {})

    return AppConfig(
        app_title=app_cfg.get("title", "GenAI Support Bot"),
        app_version=app_cfg.get("version", "1.0.0"),
        model_identifier=model_cfg.get("identifier", "gpt-4o-mini"),
        temperature=float(model_cfg.get("temperature", 0.7)),
        max_tokens=int(model_cfg.get("max_tokens", 500)),
        timeout=int(model_cfg.get("timeout", 10)),
        message_window=int(memory_cfg.get("message_window", 5)),
        forbidden_topics=list(safety_cfg.get("forbidden_topics", [])),
    )


def build_system_message(config: AppConfig) -> str:
    """Create a basic prompt contract using forbidden topics from config."""
    if config.forbidden_topics:
        forbidden = ", ".join(config.forbidden_topics)
        safety_clause = (
            f"You must refuse requests that involve {forbidden}. "
            "Give a short friendly refusal in those cases."
        )
    else:
        safety_clause = (
            "If the user asks for unsafe or harmful content, refuse politely."
        )

    return (
        "You are the GenAI Support Bot. "
        "You help users with software development data work and AI assisted workflows. "
        "Respond directly to the question with one or two short sentences. "
        "Do not start your replies with greetings like Hello Hi or Hey unless the user explicitly asks you to greet them. "
        "You may summarise or paraphrase what the user said earlier if that helps. "
        + safety_clause
    )


class Chatbot:
    """Tiny wrapper around the OpenAI client and config."""

    def __init__(self, config: AppConfig) -> None:
        load_dotenv()
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please configure it in your .env file."
            )

        self._client = OpenAI()
        self._config = config
        self._system_message = build_system_message(config)

    def _windowed_history(
        self, history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Take the last N messages based on config.message_window."""
        window = max(self._config.message_window, 0)
        if window == 0:
            return []
        return history[-window:]


    def answer(
        self,
        history: List[Dict[str, str]],
        user_message: str,
    ) -> str:
        """
        Build messages list with system prompt, history and new user message
        then call the model and return the assistant text.
        """

        # Local safety filter
        if self._is_forbidden(user_message):
            return (
                "I cannot help with that topic. "
                "Please ask about something safe such as development data or AI workflows."
            )

        # Suppress generic greetings for one word messages
        lowered = user_message.strip().lower()
        if lowered in {"hi", "hello", "hey"}:
            return "Hi. What would you like help with in your development or AI work"

        # Build message list for the model
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": self._system_message}
        ]
        messages.extend(self._windowed_history(history))
        messages.append({"role": "user", "content": user_message})

        # Model call
        response = self._client.chat.completions.create(
            model=self._config.model_identifier,
            messages=messages,
            temperature=self._config.temperature,
            max_tokens=self._config.max_tokens,
            timeout=self._config.timeout,
        )

        return response.choices[0].message.content.strip()


    def _is_forbidden(self, text: str) -> bool:
        """Return True when the message hits a forbidden topic."""
        lowered = text.lower()
        for topic in self._config.forbidden_topics:
            if topic.lower() in lowered:
                return True
        return False        

