from rag.rag_chain import RAGChain


class TaskPlanningAgent:
    """
    Task Planner acts as the project's PDF question-answering page.

    The user asks a question for the selected project.

    RAG:
        1. Retrieves relevant PDF chunks.
        2. Generates the answer.
        3. Evaluates the answer against the retrieved chunks.
        4. Returns groundedness / hallucination scores.
        5. Returns supporting chunk IDs and PDF pages.
    """

    def __init__(self):

        self.rag = RAGChain()

    # =========================================================
    # RUN TASK PLANNER
    # =========================================================

    def run(
        self,
        project_id,
        question,
        model_name,
        top_k=5
    ):

        # -----------------------------------------------------
        # Validate question
        # -----------------------------------------------------

        if not question or not question.strip():

            return {
                "success": False,

                "answer": (
                    "Please enter a question."
                ),

                "chunks": [],

                "retrieved_chunks": [],

                "chunk_count": 0,

                "retrieved_chunk_count": 0,

                "groundedness_score": 0,

                "hallucination_score": 100,

                "supporting_chunk_ids": [],

                "evaluation_reason": (
                    "No question was provided."
                ),

                "model": model_name,

                "input_tokens": 0,

                "output_tokens": 0,

                "total_tokens": 0,

                "latency": 0,
            }

        # -----------------------------------------------------
        # Ask RAG
        # -----------------------------------------------------

        return self.rag.ask(
            project_id=project_id,
            question=question.strip(),
            model_name=model_name,
            top_k=top_k,
        )

    