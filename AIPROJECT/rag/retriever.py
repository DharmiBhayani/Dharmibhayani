from rag.vectorstore import VectorStore


class Retriever:

    def __init__(self):
        self.vector_store = VectorStore()

    # =========================================================
    # Retrieve relevant chunks
    # =========================================================

    def retrieve(
        self,
        project_id,
        query,
        k=5
    ):

        results = self.vector_store.similarity_search(
            project_id,
            query,
            k
        )

        chunks = []

        for result in results:

            # -------------------------------------------------
            # LangChain Document
            # -------------------------------------------------

            if hasattr(result, "page_content"):

                metadata = result.metadata or {}

                chunks.append({
                    "text": result.page_content,

                    "page": metadata.get(
                        "page",
                        1
                    ),

                    "source": metadata.get(
                        "source",
                        "Project PDF"
                    ),

                    "file_path": metadata.get(
                        "file_path",
                        ""
                    ),

                    "chunk_id": metadata.get(
                        "chunk_id",
                        0
                    ),
                })

            # -------------------------------------------------
            # Dictionary result
            # -------------------------------------------------

            elif isinstance(result, dict):

                chunks.append({
                    "text": result.get(
                        "text",
                        result.get(
                            "page_content",
                            ""
                        )
                    ),

                    "page": result.get(
                        "page",
                        1
                    ),

                    "source": result.get(
                        "source",
                        "Project PDF"
                    ),

                    "file_path": result.get(
                        "file_path",
                        ""
                    ),

                    "chunk_id": result.get(
                        "chunk_id",
                        0
                    ),
                })

        return chunks

    # =========================================================
    # Build context
    # =========================================================

    def build_context(
        self,
        project_id,
        query,
        k=5
    ):

        chunks = self.retrieve(
            project_id,
            query,
            k
        )

        context = "\n\n".join(
            f"Source: {c['source']}\n"
            f"Page: {c['page']}\n"
            f"{c['text']}"
            for c in chunks
        )

        return context, chunks

    # =========================================================
    # Get ALL source pages from retrieved chunks
    # =========================================================

    def get_best_source_page(
        self,
        chunks
    ):

        if not chunks:
            return []

        # -----------------------------------------------------
        # Count retrieved chunks for every source + page
        # -----------------------------------------------------

        page_counts = {}

        for chunk in chunks:

            source = chunk.get(
                "source",
                "Project PDF"
            )

            page = chunk.get(
                "page",
                1
            )

            # Convert page to integer when possible
            try:
                page = int(page)
            except (ValueError, TypeError):
                page = 1

            key = (
                source,
                page
            )

            page_counts[key] = (
                page_counts.get(
                    key,
                    0
                ) + 1
            )

        sorted_pages = sorted(
            page_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )

        # -----------------------------------------------------
        # Create ONE source entry for EACH page
        # -----------------------------------------------------

        source_pages = []

        for (
            (source, page),
            chunk_count
        ) in sorted_pages:

            # Find the first chunk belonging to this page
            representative_chunk = None

            for chunk in chunks:

                chunk_source = chunk.get(
                    "source",
                    "Project PDF"
                )

                chunk_page = chunk.get(
                    "page",
                    1
                )

                try:
                    chunk_page = int(
                        chunk_page
                    )
                except (
                    ValueError,
                    TypeError
                ):
                    chunk_page = 1

                if (
                    chunk_source == source
                    and chunk_page == page
                ):

                    representative_chunk = chunk

                    break

            # -------------------------------------------------
            # Add one representative chunk for this page
            # -------------------------------------------------

            if representative_chunk:

                source_pages.append({
                    "text": representative_chunk.get(
                        "text",
                        ""
                    ),

                    "page": page,

                    "source": source,

                    "file_path": representative_chunk.get(
                        "file_path",
                        ""
                    ),

                    "chunk_id": representative_chunk.get(
                        "chunk_id",
                        0
                    ),

                    # Extra information:
                    # how many retrieved chunks came
                    # from this page
                    "chunk_count": chunk_count,
                })

        return source_pages