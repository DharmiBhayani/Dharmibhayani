import os
import sqlite3

import streamlit as st

from config.config import DATABASE_PATH
from database.database import get_projects
from rag.loader import DocumentLoader
from rag.splitter import DocumentSplitter
from rag.vectorstore import VectorStore


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Rebuild PDF Index",
    page_icon="🔄",
    layout="wide",
)


# =========================================================
# TITLE
# =========================================================

st.title(
    "🔄 Rebuild Project PDF Index"
)


# =========================================================
# SESSION STATE
# =========================================================

if "all_chunks" not in st.session_state:
    st.session_state.all_chunks = []


if "chunks_project_id" not in st.session_state:
    st.session_state.chunks_project_id = None


# =========================================================
# LOAD PROJECTS
# =========================================================

projects = get_projects()


if not projects:

    st.warning(
        "No projects found."
    )

    st.stop()


project_map = {
    project[1]: project[0]
    for project in projects
}


selected_project = st.selectbox(
    "📁 Select Project",
    list(project_map.keys()),
    key="selected_project",
)


project_id = project_map[
    selected_project
]


# =========================================================
# CLEAR OLD CHUNKS WHEN PROJECT CHANGES
# =========================================================

if (
    st.session_state.chunks_project_id
    != project_id
):

    st.session_state.all_chunks = []

    st.session_state.chunks_project_id = (
        project_id
    )


# =========================================================
# LOAD PROJECT DOCUMENTS
# =========================================================

conn = sqlite3.connect(
    DATABASE_PATH
)

try:

    files = conn.execute(
        """
        SELECT file_name, file_path
        FROM project_documents
        WHERE project_id = ?
        ORDER BY id
        """,
        (project_id,),
    ).fetchall()

except sqlite3.OperationalError:

    files = []

finally:

    conn.close()


# =========================================================
# CHECK DOCUMENTS
# =========================================================

if not files:

    st.info(
        "No uploaded documents are registered "
        "for this project."
    )

    st.stop()


# =========================================================
# SHOW DOCUMENTS
# =========================================================

st.subheader(
    "📄 Project Documents"
)


for file_name, file_path in files:

    st.write(
        f"📄 **{file_name}** — `{file_path}`"
    )


# =========================================================
# BUTTON STYLE
# =========================================================

st.markdown(
    """
    <style>

    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #218838 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTION
# =========================================================

def set_chunk_metadata(
    chunk,
    chunk_id,
    file_name,
    file_path,
):
    """
    Force one chunk to have one consistent chunk ID.

    The same ID is stored in:
        - chunk["chunk_id"]
        - chunk["metadata"]["chunk_id"]

    or for LangChain Documents:
        - chunk.metadata["chunk_id"]
    """

    # =====================================================
    # DICTIONARY CHUNK
    # =====================================================

    if isinstance(
        chunk,
        dict
    ):

        metadata = chunk.get(
            "metadata",
            {}
        )

        if not isinstance(
            metadata,
            dict
        ):

            metadata = {}


        chunk["metadata"] = metadata


        # -------------------------------------------------
        # CHUNK ID
        # -------------------------------------------------

        chunk["chunk_id"] = int(
            chunk_id
        )

        metadata["chunk_id"] = int(
            chunk_id
        )


        # -------------------------------------------------
        # SOURCE
        # -------------------------------------------------

        source = chunk.get(
            "source"
        )

        if not source:

            source = metadata.get(
                "source",
                file_name
            )


        chunk["source"] = source

        metadata["source"] = source


        # -------------------------------------------------
        # FILE PATH
        # -------------------------------------------------

        chunk["file_path"] = file_path

        metadata["file_path"] = file_path


        # -------------------------------------------------
        # PAGE
        # -------------------------------------------------

        page = chunk.get(
            "page"
        )


        if page is None:

            page = metadata.get(
                "page"
            )


        if page is None:

            page = metadata.get(
                "page_number"
            )


        if page is not None:

            chunk["page"] = page

            metadata["page"] = page


        return chunk


    # =====================================================
    # LANGCHAIN DOCUMENT
    # =====================================================

    if not hasattr(
        chunk,
        "metadata"
    ):

        chunk.metadata = {}


    if not isinstance(
        chunk.metadata,
        dict
    ):

        chunk.metadata = {}


    metadata = chunk.metadata


    # -----------------------------------------------------
    # CHUNK ID
    # -----------------------------------------------------

    metadata["chunk_id"] = int(
        chunk_id
    )


    # -----------------------------------------------------
    # SOURCE
    # -----------------------------------------------------

    source = metadata.get(
        "source",
        file_name
    )


    metadata["source"] = source


    # -----------------------------------------------------
    # FILE PATH
    # -----------------------------------------------------

    metadata["file_path"] = file_path


    # -----------------------------------------------------
    # PAGE
    # -----------------------------------------------------

    page = metadata.get(
        "page"
    )


    if page is None:

        page = metadata.get(
            "page_number"
        )


    if page is not None:

        metadata["page"] = page


    return chunk


# =========================================================
# REBUILD INDEX
# =========================================================

if st.button(
    "🔄 Rebuild Vector Index",
    type="primary",
    key="rebuild_vector_index",
):

    loader = DocumentLoader()

    splitter = DocumentSplitter()

    all_chunks = []


    st.write(
        "### 🔄 Processing documents..."
    )


    # =====================================================
    # PROCESS EACH DOCUMENT
    # =====================================================

    for file_name, file_path in files:

        # -------------------------------------------------
        # CHECK FILE
        # -------------------------------------------------

        if not os.path.exists(
            file_path
        ):

            st.warning(
                f"⚠️ Missing file: {file_path}"
            )

            continue


        try:

            # =============================================
            # LOAD PDF
            # =============================================

            documents = (
                loader.load_document(
                    file_path
                )
            )


            # =============================================
            # SPLIT PDF
            # =============================================

            chunks = (
                splitter.split_documents(
                    documents
                )
            )


            # =============================================
            # ADD DOCUMENT CHUNKS
            # =============================================

            all_chunks.extend(
                chunks
            )


            st.write(
                f"✅ **{file_name}** → "
                f"**{len(chunks)} chunks**"
            )


        except Exception as e:

            st.error(
                f"❌ Error processing "
                f"{file_name}: {e}"
            )


    # =====================================================
    # CHECK CHUNKS
    # =====================================================

    if not all_chunks:

        st.error(
            "❌ No text could be extracted "
            "from the project documents."
        )

        st.stop()


    # =====================================================
    # IMPORTANT:
    # ASSIGN FINAL SEQUENTIAL CHUNK IDS
    #
    # This happens AFTER ALL documents are processed.
    #
    # Result:
    #
    # Chunk 1 -> ID 1
    # Chunk 2 -> ID 2
    # Chunk 3 -> ID 3
    # Chunk 4 -> ID 4
    # Chunk 5 -> ID 5
    # ...
    # =====================================================

    for index, chunk in enumerate(
        all_chunks,
        start=1
    ):

        # Find file information from existing metadata

        if isinstance(
            chunk,
            dict
        ):

            metadata = chunk.get(
                "metadata",
                {}
            )

            if not isinstance(
                metadata,
                dict
            ):

                metadata = {}

            file_name = metadata.get(
                "source",
                chunk.get(
                    "source",
                    "Project PDF"
                )
            )

            file_path = metadata.get(
                "file_path",
                chunk.get(
                    "file_path",
                    ""
                )
            )

        else:

            metadata = getattr(
                chunk,
                "metadata",
                {}
            )

            if not isinstance(
                metadata,
                dict
            ):

                metadata = {}

            file_name = metadata.get(
                "source",
                "Project PDF"
            )

            file_path = metadata.get(
                "file_path",
                ""
            )


        # -------------------------------------------------
        # FORCE FINAL ID
        # -------------------------------------------------

        all_chunks[index - 1] = (
            set_chunk_metadata(
                chunk=chunk,
                chunk_id=index,
                file_name=file_name,
                file_path=file_path,
            )
        )


    # =====================================================
    # VERIFY CHUNK IDS
    # =====================================================

    expected_ids = list(
        range(
            1,
            len(all_chunks) + 1
        )
    )


    actual_ids = []


    for chunk in all_chunks:

        if isinstance(
            chunk,
            dict
        ):

            metadata = chunk.get(
                "metadata",
                {}
            )

            chunk_id = chunk.get(
                "chunk_id",
                metadata.get(
                    "chunk_id"
                )
            )

        else:

            metadata = getattr(
                chunk,
                "metadata",
                {}
            )

            chunk_id = metadata.get(
                "chunk_id"
            )


        actual_ids.append(
            int(chunk_id)
        )


    if actual_ids != expected_ids:

        st.error(
            "❌ Chunk ID generation failed. "
            "The IDs are not sequential."
        )

        st.write(
            "Expected:",
            expected_ids
        )

        st.write(
            "Actual:",
            actual_ids
        )

        st.stop()


    # =====================================================
    # CREATE VECTOR STORE
    # =====================================================

    try:

        VectorStore().create_vectorstore(
            project_id,
            all_chunks
        )

    except Exception as e:

        st.error(
            f"❌ Failed to create vector index: {e}"
        )

        st.stop()


    # =====================================================
    # SAVE CHUNKS
    # =====================================================

    st.session_state.all_chunks = (
        all_chunks
    )

    st.session_state.chunks_project_id = (
        project_id
    )


    # =====================================================
    # SUCCESS
    # =====================================================

    st.success(
        f"✅ Index rebuilt successfully with "
        f"**{len(all_chunks)} chunks**."
    )


    # =====================================================
    # SHOW ID VERIFICATION
    # =====================================================

    st.success(
        "✅ Chunk IDs successfully reset to "
        f"**1 → {len(all_chunks)}**."
    )


# =========================================================
# GET SAVED CHUNKS
# =========================================================

all_chunks = (
    st.session_state.all_chunks
)


# =========================================================
# SHOW CHUNKS
# =========================================================

if all_chunks:

    st.subheader(
        "📦 Generated Chunks"
    )


    st.write(
        f"Total chunks created: "
        f"**{len(all_chunks)}**"
    )


    # =====================================================
    # CREATE RANGE OPTIONS
    # =====================================================

    chunk_ranges = []


    for start in range(
        1,
        len(all_chunks) + 1,
        10
    ):

        end = min(
            start + 9,
            len(all_chunks)
        )


        chunk_ranges.append(
            f"{start} - {end}"
        )


    # =====================================================
    # RANGE DROPDOWN
    # =====================================================

    selected_range = st.selectbox(
        "📦 Select Chunk Range",
        chunk_ranges,
        key="chunk_range",
    )


    # =====================================================
    # GET SELECTED RANGE
    # =====================================================

    start_chunk, end_chunk = map(
        int,
        selected_range.split(
            " - "
        )
    )


    st.info(
        f"Showing chunks **{start_chunk} "
        f"to {end_chunk}** out of "
        f"**{len(all_chunks)}**."
    )


    # =====================================================
    # SELECT CHUNKS
    # =====================================================

    selected_chunks = all_chunks[
        start_chunk - 1:end_chunk
    ]


    # =====================================================
    # DISPLAY CHUNKS
    # =====================================================

    for display_index, chunk in enumerate(
        selected_chunks,
        start=start_chunk
    ):

        # =================================================
        # IMPORTANT:
        # DISPLAY NUMBER AND CHUNK ID ARE THE SAME
        # =================================================

        chunk_id = display_index


        # =================================================
        # GET METADATA
        # =================================================

        if isinstance(
            chunk,
            dict
        ):

            metadata = chunk.get(
                "metadata",
                {}
            )

            if not isinstance(
                metadata,
                dict
            ):

                metadata = {}


            source = chunk.get(
                "source",
                metadata.get(
                    "source",
                    "Unknown"
                )
            )


            page = chunk.get(
                "page",
                metadata.get(
                    "page",
                    metadata.get(
                        "page_number",
                        "Unknown"
                    )
                )
            )


            file_path = chunk.get(
                "file_path",
                metadata.get(
                    "file_path",
                    ""
                )
            )


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


        else:

            metadata = getattr(
                chunk,
                "metadata",
                {}
            )


            if not isinstance(
                metadata,
                dict
            ):

                metadata = {}


            source = metadata.get(
                "source",
                "Unknown"
            )


            page = metadata.get(
                "page",
                metadata.get(
                    "page_number",
                    "Unknown"
                )
            )


            file_path = metadata.get(
                "file_path",
                ""
            )


            content = getattr(
                chunk,
                "page_content",
                ""
            )


        # =================================================
        # EXPANDER
        # =================================================

        with st.expander(
            f"📦 Chunk {chunk_id}"
        ):

            # ---------------------------------------------
            # SOURCE
            # ---------------------------------------------

            st.write(
                f"📄 **Source:** {source}"
            )


            # ---------------------------------------------
            # PDF PAGE
            # ---------------------------------------------

            st.write(
                f"📑 **PDF Page:** {page}"
            )


            # ---------------------------------------------
            # CHUNK ID
            # ---------------------------------------------

            st.write(
                f"🔢 **Chunk ID:** {chunk_id}"
            )


            # ---------------------------------------------
            # FILE
            # ---------------------------------------------

            st.write(
                f"📁 **File:** {file_path}"
            )


            # ---------------------------------------------
            # CONTENT
            # ---------------------------------------------

            st.text_area(
                "Chunk Content",
                str(content),
                height=200,
                key=(
                    f"chunk_content_"
                    f"{project_id}_"
                    f"{chunk_id}"
                ),
            )