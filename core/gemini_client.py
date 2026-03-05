from __future__ import annotations

from collections.abc import Generator

import google.generativeai as genai


class GeminiClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        genai.configure(api_key=api_key)

    def validate_key(self) -> bool:
        models = list(genai.list_models())
        return len(models) > 0

    def stream_response(
        self,
        model_name: str,
        messages: list[dict[str, str]],
        system_prompt: str,
        temperature: float,
        max_tokens: int,
        top_p: float,
        top_k: int,
    ) -> Generator[str, None, None]:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt if system_prompt else None,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=top_p,
                top_k=top_k,
            ),
        )

        history = [
            {"role": m["role"], "parts": [m["content"]]}
            for m in messages[:-1]
            if m["role"] in {"user", "model"}
        ]
        chat = model.start_chat(history=history)
        response = chat.send_message(messages[-1]["content"], stream=True)
        for chunk in response:
            if getattr(chunk, "text", ""):
                yield chunk.text
