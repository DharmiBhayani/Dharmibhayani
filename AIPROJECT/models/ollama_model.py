import ollama


RAG_SYSTEM_PROMPT = """You are an AI Project Management Assistant answering questions about an uploaded project document.

Rules:
1. Use ONLY the supplied document context.
2. Do not use outside knowledge to fill missing facts.
3. If the answer is not supported by the context, say exactly:
"I couldn't find this information in the uploaded project documents."
4. Give a direct, clear answer.
5. When useful, mention the source page number already present in the context.
"""


class OllamaModel:
    """Ollama provider. The same class can run Llama, Qwen, or other Ollama models."""

    def __init__(self, model_name="llama3.1:8b", temperature=0.0):
        self.model_name = model_name
        self.temperature = temperature

    def _build_prompt(self, context, question):
        return f"""{RAG_SYSTEM_PROMPT}

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    def generate(self, context, question):
        prompt = self._build_prompt(context, question)

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": self.temperature},
            )

            input_tokens = int(response.get("prompt_eval_count", 0) or 0)
            output_tokens = int(response.get("eval_count", 0) or 0)
            answer = response.get("message", {}).get("content", "").strip()

            return {
                "success": True,
                "model": f"Ollama - {self.model_name}",
                "answer": answer,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            }

        except Exception as e:
            return {
                "success": False,
                "model": f"Ollama - {self.model_name}",
                "answer": str(e),
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            }

    # Backward-compatible helpers for your existing project-management agents.
    def generate_raw(self, model, prompt):
        return ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": self.temperature},
        )

    def generate_model(self, model, prompt):
        try:
            response = self.generate_raw(model, prompt)
            return {
                "success": True,
                "model": model,
                "response": response["message"]["content"],
            }
        except Exception as e:
            return {"success": False, "model": model, "response": str(e)}

    def small_model(self, prompt):
        return self.generate_model("llama3.1:8b", prompt)

    def medium_model(self, prompt):
        return self.generate_model("qwen2.5:7b-instruct", prompt)

    def large_model(self, prompt):
        return self.generate_model("llama3.1:8b", prompt)
