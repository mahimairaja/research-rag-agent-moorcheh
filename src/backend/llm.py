import os
from typing import Dict, List

import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()


class LLMClient:
    def __init__(self):
        self.token = os.getenv("HF_TOKEN", "")
        self.model_name = os.getenv(
            "HF_LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.2"
        )
        self.client = None
        try:
            if self.token:
                self.client = InferenceClient(
                    model=self.model_name, token=self.token, timeout=60
                )
        except Exception:
            self.client = None

    def has_token(self) -> bool:
        return bool(self.token)

    def generate_answer(
        self, question: str, context_chunks: List[Dict], max_length: int = 512
    ) -> str:
        if not context_chunks:
            return "No relevant context found. Please index some documents first."

        # Format context from chunks
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk.get("source", "Unknown")
            text = chunk.get("text", "")
            context_parts.append(f"[Source {i}: {source}]\n{text}")

        context = "\n\n".join(context_parts)

        # Format prompt
        prompt = f"""You are a research assistant. Use ONLY the provided context to answer the question. If the context doesn't contain enough information, say so clearly.

Question: {question}

Context:
{context}

Answer:"""
        if self.token:
            try:
                if self.client is not None:
                    try:
                        messages = [
                            {
                                "role": "system",
                                "content": "You are a research assistant. Use ONLY the provided context to answer questions. If the context doesn't contain enough information, say so clearly.",
                            },
                            {
                                "role": "user",
                                "content": f"Question: {question}\n\nContext:\n{context}\n\nAnswer:",
                            },
                        ]
                        completion = self.client.chat.completions.create(
                            model=self.model_name,
                            messages=messages,
                            max_tokens=max_length,
                            temperature=0.7,
                            top_p=0.9,
                        )
                        generated_text = None
                        if hasattr(completion, "choices") and completion.choices:
                            choice = completion.choices[0]
                            if isinstance(getattr(choice, "message", None), dict):
                                generated_text = choice.message.get("content", "")
                            else:
                                msg = getattr(choice, "message", None)
                                if msg is not None:
                                    generated_text = getattr(msg, "content", "")
                        if generated_text:
                            return generated_text.strip()
                    except Exception:
                        pass

                    try:
                        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
                        tg = self.client.text_generation(
                            formatted_prompt,
                            max_new_tokens=max_length,
                            temperature=0.7,
                            top_p=0.9,
                            do_sample=True,
                            return_full_text=False,
                        )
                        if isinstance(tg, str):
                            return tg.strip()
                        if isinstance(tg, dict) and tg.get("generated_text"):
                            return tg["generated_text"].strip()
                    except Exception:
                        pass

                return "API error: Unable to generate via router (chat and text fallbacks failed). Please verify HF_TOKEN and model availability."

            except requests.exceptions.Timeout:
                return (
                    "Request timed out. The model may be processing. Please try again."
                )
            except Exception as e:
                return f"Error generating answer: {str(e)}"
        else:
            return self._extractive_fallback(question, context_chunks)

    def _extractive_fallback(self, question: str, context_chunks: List[Dict]) -> str:
        if not context_chunks:
            return "No context available. Please set HF_TOKEN environment variable for LLM generation."

        top_chunk = context_chunks[0]
        source = top_chunk.get("source", "Unknown")
        text = top_chunk.get("text", "")

        answer = f"Based on {source}:\n\n{text[:500]}"
        if len(text) > 500:
            answer += "..."

        return answer
