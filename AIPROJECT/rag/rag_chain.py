import json
import re
import time

from logger.logger import log_request
from logger.token_tracker import count_tokens
from models.model_manager import ModelManager
from rag.retriever import Retriever


class RAGChain:

    def __init__(self):

        self.retriever = Retriever()
        self.models = ModelManager()

    # =========================================================
    # GET CHUNK CONTENT
    # =========================================================

    def _get_chunk_content(self, chunk):

        # ---------------------------------------------
        # Dictionary chunk
        # ---------------------------------------------

        if isinstance(chunk, dict):

            content = chunk.get(
                "text",
                ""
            )

            if not content:

                content = chunk.get(
                    "page_content",
                    ""
                )

            if not content:

                content = chunk.get(
                    "content",
                    ""
                )

            return str(content)

        # ---------------------------------------------
        # LangChain Document
        # ---------------------------------------------

        return str(
            getattr(
                chunk,
                "page_content",
                ""
            )
        )

    # =========================================================
    # GET CHUNK INFORMATION
    # =========================================================

    def _get_chunk_info(
        self,
        chunk,
        index
    ):

        # ---------------------------------------------
        # Dictionary
        # ---------------------------------------------

        if isinstance(chunk, dict):

            metadata = chunk.get(
                "metadata",
                {}
            )

            if not isinstance(
                metadata,
                dict
            ):
                metadata = {}

            chunk_id = chunk.get(
                "chunk_id",
                metadata.get(
                    "chunk_id",
                    index
                )
            )

            page = chunk.get(
                "page",
                metadata.get(
                    "page",
                    "Unknown"
                )
            )

            source = chunk.get(
                "source",
                metadata.get(
                    "source",
                    "Project PDF"
                )
            )

            file_path = chunk.get(
                "file_path",
                metadata.get(
                    "file_path",
                    ""
                )
            )

        # ---------------------------------------------
        # LangChain Document
        # ---------------------------------------------

        else:

            metadata = getattr(
                chunk,
                "metadata",
                {}
            )

            chunk_id = metadata.get(
                "chunk_id",
                index
            )

            page = metadata.get(
                "page",
                "Unknown"
            )

            source = metadata.get(
                "source",
                "Project PDF"
            )

            file_path = metadata.get(
                "file_path",
                ""
            )

        return {
            "chunk_id": chunk_id,
            "page": page,
            "source": source,
            "file_path": file_path,
            "content": self._get_chunk_content(
                chunk
            ),
        }

    # =========================================================
    # AUTOMATIC GROUNDEDNESS EVALUATION
    # =========================================================

    def evaluate_groundedness(
        self,
        model_name,
        question,
        answer,
        chunks
    ):

        if not answer or not chunks:

            return {
                "groundedness_score": 0,
                "hallucination_score": 100,
                "supporting_chunk_ids": [],
                "evaluation_reason": (
                    "No answer or PDF context available."
                ),
            }

        # ---------------------------------------------
        # Prepare chunks
        # ---------------------------------------------

        formatted_chunks = []

        for index, chunk in enumerate(chunks):

            info = self._get_chunk_info(
                chunk,
                index
            )

            formatted_chunks.append(
                f"""
CHUNK ID: {info["chunk_id"]}
PDF PAGE: {info["page"]}
SOURCE: {info["source"]}

CHUNK CONTENT:
{info["content"]}
"""
            )

        pdf_context = "\n".join(
            formatted_chunks
        )

        # ---------------------------------------------
        # Evaluation prompt
        # ---------------------------------------------

        evaluation_prompt = f"""
You are a RAG answer evaluator.

Your task is to check whether the generated answer
is supported by the supplied PDF chunks.

QUESTION:
{question}

GENERATED ANSWER:
{answer}

RETRIEVED PDF CHUNKS:
{pdf_context}

IMPORTANT RULES:

1. Use ONLY the supplied PDF chunks.
2. Do NOT use outside knowledge.
3. Check every important claim in the answer.
4. Identify which chunk IDs support the answer.
5. If a claim is not supported by the chunks,
   consider it hallucinated.
6. Give a groundedness score from 0 to 100.
7. 100 = completely supported by PDF.
8. 0 = completely unsupported by PDF.
9. Hallucination score = 100 - groundedness score.
10. Return ONLY valid JSON.

Return exactly:

{{
    "groundedness_score": 0,
    "hallucination_score": 100,
    "supporting_chunk_ids": [],
    "reason": "Short explanation"
}}
"""

        try:

            evaluation_result = self.models.generate(
                model_name,
                pdf_context,
                evaluation_prompt
            )

            evaluation_answer = (
                evaluation_result.get(
                    "answer",
                    ""
                )
            )

            # -----------------------------------------
            # Extract JSON
            # -----------------------------------------

            match = re.search(
                r"\{.*\}",
                evaluation_answer,
                re.DOTALL
            )

            if not match:

                return {
                    "groundedness_score": 0,
                    "hallucination_score": 100,
                    "supporting_chunk_ids": [],
                    "evaluation_reason": (
                        "Evaluator did not return valid JSON."
                    ),
                }

            data = json.loads(
                match.group(0)
            )

            groundedness = int(
                data.get(
                    "groundedness_score",
                    0
                )
            )

            groundedness = max(
                0,
                min(
                    100,
                    groundedness
                )
            )

            hallucination = (
                100 - groundedness
            )

            supporting_chunks = data.get(
                "supporting_chunk_ids",
                []
            )

            if not isinstance(
                supporting_chunks,
                list
            ):
                supporting_chunks = []

            return {
                "groundedness_score": groundedness,
                "hallucination_score": hallucination,
                "supporting_chunk_ids": (
                    supporting_chunks
                ),
                "evaluation_reason": data.get(
                    "reason",
                    ""
                ),
            }

        except Exception as e:

            return {
                "groundedness_score": 0,
                "hallucination_score": 100,
                "supporting_chunk_ids": [],
                "evaluation_reason": (
                    f"Evaluation failed: {str(e)}"
                ),
            }

    # =========================================================
    # ASK QUESTION
    # =========================================================

    def ask(
        self,
        project_id,
        question,
        model_name,
        top_k=5
    ):

        start = time.perf_counter()

        # =====================================================
        # RETRIEVE CHUNKS
        # =====================================================

        context, chunks = (
            self.retriever.build_context(
                project_id,
                question,
                top_k
            )
        )

        # =====================================================
        # NO CONTEXT
        # =====================================================

        if not context.strip():

            return {
                "success": False,

                "answer": (
                    "No information found in the "
                    "uploaded project documents."
                ),

                "chunks": [],

                "retrieved_chunks": [],

                "chunk_count": 0,

                "retrieved_chunk_count": 0,

                "groundedness_score": 0,

                "hallucination_score": 100,

                "supporting_chunk_ids": [],

                "evaluation_reason": (
                    "No PDF context found."
                ),

                "latency": round(
                    time.perf_counter() - start,
                    3
                ),

                "model": model_name,

                "input_tokens": 0,

                "output_tokens": 0,

                "total_tokens": 0,
            }

        # =====================================================
        # GENERATE NORMAL AI ANSWER
        # =====================================================

        result = self.models.generate(
            model_name,
            context,
            question
        )

        # =====================================================
        # TOKEN CALCULATION
        # =====================================================

        if not result.get(
            "input_tokens"
        ):

            result["input_tokens"] = (
                count_tokens(
                    question + context
                )
            )

        if not result.get(
            "output_tokens"
        ):

            result["output_tokens"] = (
                count_tokens(
                    result.get(
                        "answer",
                        ""
                    )
                )
            )

        result["total_tokens"] = (
            result["input_tokens"]
            + result["output_tokens"]
        )

        # =====================================================
        # AUTOMATIC GROUNDEDNESS EVALUATION
        # =====================================================

        evaluation = (
            self.evaluate_groundedness(
                model_name=model_name,
                question=question,
                answer=result.get(
                    "answer",
                    ""
                ),
                chunks=chunks
            )
        )

        result["groundedness_score"] = (
            evaluation[
                "groundedness_score"
            ]
        )

        result["hallucination_score"] = (
            evaluation[
                "hallucination_score"
            ]
        )

        result["supporting_chunk_ids"] = (
            evaluation[
                "supporting_chunk_ids"
            ]
        )

        result["evaluation_reason"] = (
            evaluation[
                "evaluation_reason"
            ]
        )

        # =====================================================
        # BEST SOURCE PAGE
        # =====================================================

        best_source_chunks = (
            self.retriever.get_best_source_page(
                chunks
            )
        )

        # =====================================================
        # RESULT INFORMATION
        # =====================================================

        result["chunks"] = (
            best_source_chunks
        )

        # ALL RETRIEVED CHUNKS
        result["retrieved_chunks"] = (
            chunks
        )

        result["chunk_count"] = len(
            best_source_chunks
        )

        result["retrieved_chunk_count"] = len(
            chunks
        )

        result["model"] = model_name

        # Total time including evaluation
        result["latency"] = round(
            time.perf_counter() - start,
            3
        )

        # =====================================================
        # LOG REQUEST
        # =====================================================

        log_request(
            project_id=project_id,
            agent="PDF RAG Q&A",
            model=model_name,
            input_text=question,
            output_text=result.get(
                "answer",
                ""
            ),
            latency=result.get(
                "latency",
                0
            ),
            input_tokens=result.get(
                "input_tokens",
                0
            ),
            output_tokens=result.get(
                "output_tokens",
                0
            ),
            total_tokens=result.get(
                "total_tokens",
                0
            ),

            source_pages=[
                {
                    "source": info.get(
                        "source"
                    ),
                    "page": info.get(
                        "page"
                    ),
                    "chunk_id": info.get(
                        "chunk_id"
                    ),
                }
                for index, chunk
                in enumerate(chunks)
                for info in [
                    self._get_chunk_info(
                        chunk,
                        index
                    )
                ]
            ],
        )

        return result