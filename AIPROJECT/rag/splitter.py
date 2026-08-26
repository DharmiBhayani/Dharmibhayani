from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentSplitter:
    def __init__(self, chunk_size=1000, chunk_overlap=150):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def split_documents(self, documents):
        chunks = []
        for doc in documents:
            parts = self.splitter.split_text(doc["text"])
            for i, text in enumerate(parts):
                chunks.append({
                    "text": text,
                    "page": doc.get("page", 1),
                    "source": doc.get("source", ""),
                    "file_path": doc.get("file_path", ""),
                    "chunk_id": i + 1,
                })
        return chunks
