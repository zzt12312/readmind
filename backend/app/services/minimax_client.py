from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Iterator
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LLMClientError(RuntimeError):
    pass


@dataclass
class LLMClient:
    api_key: str
    base_url: str
    model: str

    def chat(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        max_completion_tokens: int = 800,
    ) -> str:
        data = self._request_chat(
            system_prompt=system_prompt,
            messages=messages,
            max_completion_tokens=max_completion_tokens,
            stream=False,
        )

        try:
            content = data["choices"][0]["message"]["content"]
        except Exception as error:
            raise LLMClientError(f"Unexpected DeepSeek response: {data}") from error

        return strip_thinking(content).strip()

    def stream_chat(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        max_completion_tokens: int = 800,
    ) -> Iterator[str]:
        response = self._request_chat(
            system_prompt=system_prompt,
            messages=messages,
            max_completion_tokens=max_completion_tokens,
            stream=True,
        )

        try:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="ignore").strip()
                if not line or not line.startswith("data:"):
                    continue
                payload = line.removeprefix("data:").strip()
                if payload == "[DONE]":
                    break
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                delta = extract_stream_delta(data)
                if delta:
                    yield delta
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="ignore")
            raise LLMClientError(f"DeepSeek HTTP error {error.code}: {detail}") from error
        except URLError as error:
            raise LLMClientError(f"DeepSeek network error: {error}") from error
        except Exception as error:
            raise LLMClientError(f"DeepSeek client error: {error}") from error
        finally:
            response.close()

    def _request_chat(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        max_completion_tokens: int,
        stream: bool,
    ) -> Any:
        if not self.api_key:
            raise LLMClientError("Missing DEEPSEEK_API_KEY")

        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}, *messages],
            "temperature": 0.3,
            "top_p": 0.9,
            "max_tokens": max_completion_tokens,
            "stream": stream,
        }

        request = Request(
            url=f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            response = urlopen(request, timeout=60)
            if stream:
                return response
            with response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="ignore")
            raise LLMClientError(f"DeepSeek HTTP error {error.code}: {detail}") from error
        except URLError as error:
            raise LLMClientError(f"DeepSeek network error: {error}") from error
        except Exception as error:
            raise LLMClientError(f"DeepSeek client error: {error}") from error


def strip_thinking(content: str) -> str:
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
    return content.strip()


def extract_stream_delta(data: dict[str, Any]) -> str:
    try:
        delta = data["choices"][0]["delta"].get("content", "")
    except Exception:
        return ""

    if isinstance(delta, str):
        return delta

    if isinstance(delta, list):
        parts: list[str] = []
        for item in delta:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or ""
                if text:
                    parts.append(str(text))
        return "".join(parts)

    return ""


def create_llm_client(app_config: Any) -> LLMClient:
    return LLMClient(
        api_key=app_config.get("DEEPSEEK_API_KEY", ""),
        base_url=app_config.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        model=app_config.get("DEEPSEEK_MODEL", "deepseek-chat"),
    )
