
import os
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from rag.embeddings import EmbeddingModel


class VectorStore:
    def __init__(self):
        self.embedding = EmbeddingModel().get_embedding_model()

    def create_vectorstore(self, project_id, chunks):
        documents = []
        for chunk in chunks:
            documents.append(
                Document(
                    page_content=chunk["text"],
                    metadata={
                        "page": chunk.get("page", 1),
                        "source": chunk.get("source", ""),
                        "file_path": chunk.get("file_path", ""),
                        "chunk_id": chunk.get("chunk_id", 0),
                    },
                )
            )

        if not documents:
            return False

        save_path = os.path.join("vector_db", str(project_id))
        os.makedirs(save_path, exist_ok=True)

        vector_db = FAISS.from_documents(documents, self.embedding)
        vector_db.save_local(save_path)
        return True

    def load_vectorstore(self, project_id):
        save_path = os.path.join("vector_db", str(project_id))
        index_file = os.path.join(save_path, "index.faiss")

        if not os.path.exists(index_file):
            return None

        return FAISS.load_local(
            save_path,
            self.embedding,
            allow_dangerous_deserialization=True,
        )

    def similarity_search(self, project_id, query, k=5):
        db = self.load_vectorstore(project_id)
        if db is None:
            return []
        return db.similarity_search(query, k=k)
