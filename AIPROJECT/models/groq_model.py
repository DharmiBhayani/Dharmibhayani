import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


RAG_SYSTEM_PROMPT = """
You are an AI Project Management Assistant answering questions
about an uploaded project document.

Rules:

1. Use ONLY the supplied document context.
2. Do not invent facts.
3. If the answer is not supported by the context, say exactly:
   "I couldn't find this information in the uploaded project documents."
4. Give a direct, clear answer.
5. When useful, mention the source page number already present in the context.
"""


class GroqModel:

    display_name = "openai/gpt-oss-20b"

    def __init__(self):

        # Read the API key from .env
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is missing. "
                "Add it to your .env file."
            )

        print("DEBUG GROQ MODEL =", os.getenv("GROQ_MODEL"))

        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=os.getenv(
                "GROQ_MODEL",
                "openai/gpt-oss-20b"
            ),
            temperature=0,
        )

    def generate(self, context, question):

        prompt = f"""
{RAG_SYSTEM_PROMPT}

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

        try:

            response = self.llm.invoke(prompt)

            usage = getattr(
                response,
                "usage_metadata",
                {}
            ) or {}

            input_tokens = int(
                usage.get("input_tokens", 0) or 0
            )

            output_tokens = int(
                usage.get("output_tokens", 0) or 0
            )

            if (
                not input_tokens
                and hasattr(response, "response_metadata")
            ):

                token_usage = (
                    response.response_metadata.get(
                        "token_usage",
                        {}
                    ) or {}
                )

                input_tokens = int(
                    token_usage.get(
                        "prompt_tokens",
                        0
                    )
                    or token_usage.get(
                        "input_tokens",
                        0
                    )
                    or 0
                )

                output_tokens = int(
                    token_usage.get(
                        "completion_tokens",
                        0
                    )
                    or token_usage.get(
                        "output_tokens",
                        0
                    )
                    or 0
                )

            return {
                "success": True,
                "model": self.display_name,
                "answer": str(
                    response.content
                ).strip(),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": (
                    input_tokens + output_tokens
                ),
            }

        except Exception as e:

            return {
                "success": False,
                "model": self.display_name,
                "answer": str(e),
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            }