from rag.vectorstore import VectorStore


# project id from database
project_id = 6


# Example PDF chunks
chunks = [
    {
        "text": "This project is an AI Project Management System.",
        "page": 1,
        "source": "DHARMI BHAYANI AI PROJECT.pdf",
        "chunk_id": 0
    },
    {
        "text": "The system contains Task Planner, Deadline Prediction and RAG.",
        "page": 2,
        "source": "DHARMI BHAYANI AI PROJECT.pdf",
        "chunk_id": 1
    }
]


vector = VectorStore()


result = vector.create_vectorstore(
    project_id,
    chunks
)


print("Vector created:", result)