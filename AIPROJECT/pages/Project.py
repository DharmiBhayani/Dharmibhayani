import os
import sqlite3
import streamlit as st
import pandas as pd

from config.config import DATABASE_PATH
from rag.loader import DocumentLoader
from rag.splitter import DocumentSplitter
from rag.vectorstore import VectorStore


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Projects",
    page_icon="📁",
    layout="wide",
)

st.title("📁 Project Management")


# =========================================================
# SUPPORTED FILE TYPES
# =========================================================

SUPPORTED_TYPES = [
    "pdf",
    "docx",
    "txt",
    "pptx",
    "xlsx",
    "csv",
    "png",
    "jpg",
    "jpeg",
    "webp",
]


# =========================================================
# IMAGE OCR
# =========================================================

def load_image_with_ocr(file_path):
    """
    Extract text from an image using OCR.

    Requires:
        pip install pillow pytesseract

    Also requires Tesseract OCR to be installed
        on Windows separately.
    """

    try:
        from PIL import Image
        import pytesseract

        image = Image.open(file_path)

        text = pytesseract.image_to_string(image)

        if not text.strip():
            st.warning(
                f"⚠️ No readable text found in image: "
                f"{os.path.basename(file_path)}"
            )
            return []

        return [
            {
                "page_content": text,
                "metadata": {
                    "source": file_path,
                    "file_path": file_path,
                },
            }
        ]

    except ImportError:
        st.error(
            "❌ OCR packages are missing.\n\n"
            "Install them using:\n"
            "`pip install pillow pytesseract`"
        )
        return []

    except Exception as e:
        st.error(
            f"❌ Could not read image "
            f"{os.path.basename(file_path)}: {e}"
        )
        return []


# =========================================================
# LOAD DOCUMENT
# =========================================================

def load_project_file(file_path):
    """
    Load different project file formats.

    Text-based files are sent to DocumentLoader.
    Images are processed using OCR.
    """

    extension = os.path.splitext(file_path)[1].lower()

    # -----------------------------------------------------
    # IMAGE FILES
    # -----------------------------------------------------

    image_extensions = [
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    ]

    if extension in image_extensions:
        return load_image_with_ocr(file_path)

    # -----------------------------------------------------
    # NORMAL DOCUMENT FILES
    # -----------------------------------------------------

    try:
        loader = DocumentLoader()

        documents = loader.load_document(file_path)

        return documents

    except Exception as e:
        st.error(
            f"❌ Could not process "
            f"{os.path.basename(file_path)}: {e}"
        )

        return []


# =========================================================
# ADD NEW PROJECT
# =========================================================

st.subheader("➕ Add New Project")


project_name = st.text_input(
    "Project Name"
)


description = st.text_area(
    "Project Description"
)

# =========================================================
# FILE UPLOADER
# =========================================================

uploaded_files = st.file_uploader(
    "📄 Upload Project Documents",

    type=SUPPORTED_TYPES,

    accept_multiple_files=True,

    help=(
        "You can upload multiple files at once. "
        "Supported formats: PDF, Word, TXT, "
        "PowerPoint, Excel, CSV and images."
    ),
)


# =========================================================
# SHOW SELECTED FILES
# =========================================================

if uploaded_files:

    st.markdown("### 📎 Selected Files")

    for uploaded_file in uploaded_files:

        file_size_mb = (
            uploaded_file.size / (1024 * 1024)
        )

        st.write(
            f"📄 **{uploaded_file.name}** "
            f"— {file_size_mb:.2f} MB"
        )


# =========================================================
# SAVE PROJECT
# =========================================================

if st.button(
    "Save Project",
    type="primary",
):

    # -----------------------------------------------------
    # VALIDATE PROJECT NAME
    # -----------------------------------------------------

    if not project_name.strip():

        st.warning(
            "⚠️ Project name is required."
        )

        st.stop()


    # -----------------------------------------------------
    # DATABASE CONNECTION
    # -----------------------------------------------------

    conn = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = conn.cursor()


    # -----------------------------------------------------
    # INSERT PROJECT
    # -----------------------------------------------------

    cursor.execute(
        """
        INSERT INTO projects
        (
            project_name,
            name,
            description,
            deadline,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            project_name.strip(),
            project_name.strip(),
            description,
            str(deadline),
            status,
        ),
    )


    project_id = cursor.lastrowid


    # -----------------------------------------------------
    # PROJECT DOCUMENT TABLE
    # -----------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS project_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            file_name TEXT,
            file_path TEXT,
            uploaded_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


    # -----------------------------------------------------
    # CREATE UPLOAD FOLDER
    # -----------------------------------------------------

    upload_folder = os.path.join(
        "uploads",
        str(project_id),
    )

    os.makedirs(
        upload_folder,
        exist_ok=True,
    )


    # -----------------------------------------------------
    # RAG CHUNKS
    # -----------------------------------------------------

    all_chunks = []

    splitter = DocumentSplitter()


    # =====================================================
    # PROCESS ALL UPLOADED FILES
    # =====================================================

    if uploaded_files:

        progress_bar = st.progress(
            0
        )

        total_files = len(
            uploaded_files
        )


        for index, uploaded_file in enumerate(
            uploaded_files
        ):

            # -------------------------------------------------
            # SAFE FILE NAME
            # -------------------------------------------------

            file_name = os.path.basename(
                uploaded_file.name
            )

            file_path = os.path.join(
                upload_folder,
                file_name,
            )


            # -------------------------------------------------
            # SAVE FILE
            # -------------------------------------------------

            with open(
                file_path,
                "wb",
            ) as f:

                f.write(
                    uploaded_file.getbuffer()
                )


            # -------------------------------------------------
            # SAVE FILE INFORMATION IN DATABASE
            # -------------------------------------------------

            cursor.execute(
                """
                INSERT INTO project_documents
                (
                    project_id,
                    file_name,
                    file_path
                )
                VALUES (?, ?, ?)
                """,
                (
                    project_id,
                    file_name,
                    file_path,
                ),
            )


            # -------------------------------------------------
            # LOAD DOCUMENT
            # -------------------------------------------------

            extension = os.path.splitext(
                file_name
            )[1].lower()


            try:

                documents = load_project_file(
                    file_path
                )


                if not documents:
                    continue


                # -------------------------------------------------
                # SPLIT INTO CHUNKS
                # -------------------------------------------------

                chunks = splitter.split_documents(
                    documents
                )


                # -------------------------------------------------
                # ADD FILE INFORMATION TO CHUNKS
                # -------------------------------------------------

                for chunk in chunks:

                    # Existing code expects dictionary chunks
                    if isinstance(
                        chunk,
                        dict,
                    ):

                        chunk["file_path"] = (
                            file_path
                        )

                        chunk["file_name"] = (
                            file_name
                        )

                        chunk["project_id"] = (
                            project_id
                        )

                    all_chunks.append(
                        chunk
                    )


            except Exception as e:

                st.error(
                    f"❌ Error processing "
                    f"{file_name}: {e}"
                )


            # -------------------------------------------------
            # UPDATE PROGRESS
            # -------------------------------------------------

            progress_bar.progress(
                (index + 1) / total_files
            )


        progress_bar.empty()


    # =====================================================
    # COMMIT DATABASE
    # =====================================================

    conn.commit()
    conn.close()


    # =====================================================
    # CREATE VECTOR STORE
    # =====================================================

    if all_chunks:

        try:

            VectorStore().create_vectorstore(
                project_id,
                all_chunks,
            )

            st.success(
                f"✅ Project saved successfully!"
            )

            st.info(
                f"📄 {len(uploaded_files)} "
                f"file(s) uploaded"
            )

            st.info(
                f"🧩 {len(all_chunks)} "
                f"document chunks indexed"
            )


        except Exception as e:

            st.error(
                f"❌ Vector store creation failed: {e}"
            )

    else:

        st.success(
            "✅ Project saved."
        )

        if uploaded_files:

            st.warning(
                "⚠️ Files were uploaded, "
                "but no readable text could be extracted."
            )

        else:

            st.info(
                "ℹ️ No document was uploaded."
            )


# =========================================================
# ALL PROJECTS
# =========================================================

st.divider()

st.subheader(
    "📋 All Projects"
)


conn = sqlite3.connect(
    DATABASE_PATH
)


df = pd.read_sql(
    """
    SELECT *
    FROM projects
    ORDER BY id DESC
    """,
    conn,
)


conn.close()


if df.empty:

    st.info(
        "No projects available."
    )

else:

    st.dataframe(
        df,
        use_container_width=True,
    )