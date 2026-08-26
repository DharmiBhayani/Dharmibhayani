from models.groq_model import GroqModel
from models.ollama_model import OllamaModel


class ModelManager:
    """Central registry for the three PDF-RAG answer models."""

    MODEL_REGISTRY = {
        "Groq - GPT OSS 20B": lambda: GroqModel(),
        "Ollama - Llama 3.1 8B": lambda: OllamaModel("llama3.1:8b"),
        "Ollama - Qwen 2.5 7B Instruct": lambda: OllamaModel("qwen2.5:7b-instruct"),
    }

    def __init__(self):
        self._instances = {}

    def available_models(self):
        return list(self.MODEL_REGISTRY.keys())

    def _get(self, model_name):
        if model_name not in self.MODEL_REGISTRY:
            raise ValueError(f"Model '{model_name}' is not configured.")

        if model_name not in self._instances:
            self._instances[model_name] = self.MODEL_REGISTRY[model_name]()

        return self._instances[model_name]

    def generate(self, model_name, context, question):
        try:
            return self._get(model_name).generate(context, question)
        except Exception as e:
            return {
                "success": False,
                "model": model_name,
                "answer": str(e),
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            }
