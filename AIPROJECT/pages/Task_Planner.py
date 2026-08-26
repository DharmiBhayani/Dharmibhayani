import os

import fitz
import streamlit as st

from agents.task_agent import TaskPlanningAgent
from database.database import get_projects, save_ai_log
from models.model_manager import ModelManager


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Task Planner",
    page_icon="📝",
    layout="wide",
)


# =========================================================
# BUTTON STYLE
# =========================================================

st.markdown(
    """
    <style>

    button[kind="primary"] {
        background-color: #28a745 !important;
        border-color: #28a745 !important;
        color: white !important;
    }

    button[kind="primary"]:hover {
        background-color: #218838 !important;
        border-color: #218838 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# TITLE
# =========================================================

st.title(
    "📝 Task Planner — Ask Your Project PDF"
)


st.info(
    "Upload your project PDF from the Project page. "
    "Then ask your project question here. The answer is generated "
    "only from the selected project's uploaded document(s). "
    "The system also evaluates the answer for groundedness "
    "and possible hallucination."
)


# =========================================================
# PROJECTS
# =========================================================

projects = get_projects()


if not projects:

    st.warning(
        "No projects found. First create a project and upload "
        "its PDF from the Project page."
    )

    st.stop()


project_names = {
    p[1]: p[0]
    for p in projects
}


selected_project = st.selectbox(
    "📁 Select Project",
    list(project_names.keys()),
)


project_id = project_names[
    selected_project
]


# =========================================================
# MODEL
# =========================================================

model_manager = ModelManager()


model_names = (
    model_manager.available_models()
)


model_mode = st.radio(
    "Answer Mode",
    [
        "One Model",
        "Compare All 3 Models",
    ],
    horizontal=True,
)


if model_mode == "One Model":

    selected_model = st.selectbox(
        "Select Model",
        model_names,
    )

else:

    selected_model = None


# =========================================================
# QUESTION
# =========================================================

question = st.text_area(
    "Ask a question about this project's PDF",
    height=120,
)


# =========================================================
# TOP K
# =========================================================

top_k = st.slider(
    "Number of PDF chunks to retrieve",
    min_value=2,
    max_value=8,
    value=5,
)


# =========================================================
# HISTORY SAVE FUNCTION
# =========================================================

def save_history(
    project_id,
    question,
    result,
):

    if not result:

        return


    # -----------------------------------------------------
    # DON'T SAVE FAILED RESPONSES
    # -----------------------------------------------------

    if not result.get(
        "success",
        True
    ):

        return


    answer = result.get(
        "answer",
        ""
    )


    if not answer:

        return


    model = result.get(
        "model",
        "Unknown"
    )


    input_tokens = result.get(
        "input_tokens",
        0
    )


    output_tokens = result.get(
        "output_tokens",
        0
    )


    total_tokens = result.get(
        "total_tokens",
        input_tokens + output_tokens
    )


    latency = result.get(
        "latency",
        0.0
    )


    # -----------------------------------------------------
    # SAVE DATABASE HISTORY
    # -----------------------------------------------------

    try:

        save_ai_log(
            project_id=project_id,
            agent="Task Planner",
            model=model,
            input_text=question,
            output_text=answer,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            tokens=total_tokens,
            latency=latency,
            cost=0.0,
        )

    except Exception as e:

        st.warning(
            "Answer generated, but history could not "
            f"be saved: {e}"
        )


# =========================================================
# CHUNK ID HELPER
# =========================================================

def get_chunk_data(
    chunk,
    fallback_id,
):

    """
    Extract chunk information safely.

    The actual chunk_id from the rebuilt vector index
    is preferred.
    """

    # =====================================================
    # DICTIONARY
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


        chunk_id = chunk.get(
            "chunk_id"
        )


        if chunk_id is None:

            chunk_id = metadata.get(
                "chunk_id"
            )


        if chunk_id is None:

            chunk_id = fallback_id


        page = chunk.get(
            "page"
        )


        if page is None:

            page = metadata.get(
                "page"
            )


        if page is None:

            page = metadata.get(
                "page_number",
                "Unknown"
            )


        source = chunk.get(
            "source"
        )


        if not source:

            source = metadata.get(
                "source",
                "Project PDF"
            )


        file_path = chunk.get(
            "file_path"
        )


        if not file_path:

            file_path = metadata.get(
                "file_path",
                ""
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


        return {
            "chunk_id": int(chunk_id),
            "page": page,
            "source": source,
            "file_path": file_path,
            "content": content,
            "metadata": metadata,
        }


    # =====================================================
    # LANGCHAIN DOCUMENT
    # =====================================================

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


    chunk_id = metadata.get(
        "chunk_id",
        fallback_id
    )


    page = metadata.get(
        "page"
    )


    if page is None:

        page = metadata.get(
            "page_number",
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


    content = getattr(
        chunk,
        "page_content",
        ""
    )


    return {
        "chunk_id": int(chunk_id),
        "page": page,
        "source": source,
        "file_path": file_path,
        "content": content,
        "metadata": metadata,
    }


# =========================================================
# DISPLAY RESULT
# =========================================================

def display_result(
    result,
    result_key,
):

    # =====================================================
    # FAILED RESULT
    # =====================================================

    if not result.get(
        "success",
        True
    ):

        st.error(
            result.get(
                "answer",
                "Model failed."
            )
        )

        return


    # =====================================================
    # GET MODEL
    # =====================================================

    model = result.get(
        "model",
        "AI Model"
    )


    # =====================================================
    # AI ANSWER
    # =====================================================

    st.markdown(
        "### 🤖 AI Answer"
    )


    st.write(
        result.get(
            "answer",
            "No response generated."
        )
    )


    # =====================================================
    # RAG EVALUATION
    # =====================================================

    st.markdown(
        "### 🛡️ RAG Answer Evaluation"
    )


    groundedness = result.get(
        "groundedness_score",
        0
    )


    hallucination = result.get(
        "hallucination_score",
        100
    )


    evaluation_reason = result.get(
        "evaluation_reason",
        "No evaluation explanation available."
    )


    # =====================================================
    # SCORE CARDS
    # =====================================================

    score1, score2 = st.columns(2)


    score1.metric(
        "🟢 Groundedness Score",
        f"{groundedness}%"
    )


    score2.metric(
        "🔴 Hallucination Score",
        f"{hallucination}%"
    )


    # =====================================================
    # SCORE MESSAGE
    # =====================================================

    if hallucination <= 10:

        st.success(
            "✅ The answer is strongly supported by "
            "the retrieved PDF chunks."
        )

    elif hallucination <= 30:

        st.warning(
            "⚠️ The answer contains some information "
            "that may not be fully supported by the PDF."
        )

    else:

        st.error(
            "🚨 The answer contains a high amount of "
            "potentially unsupported information."
        )


    # =====================================================
    # EVALUATION EXPLANATION
    # =====================================================

    with st.expander(
        "🔍 Evaluation Explanation"
    ):

        st.write(
            evaluation_reason
        )


    # =====================================================
    # PERFORMANCE
    # =====================================================

    st.markdown(
        "### ⚡ Performance"
    )


    # =====================================================
    # IMPORTANT:
    # MODEL + LATENCY + INPUT + OUTPUT + TOTAL
    # ARE NOW IN ONE ROW
    # =====================================================

    m1, m2, m3, m4, m5 = st.columns(5)


    m1.metric(
        "🤖 Model",
        model
    )


    m2.metric(
        "⏱️ Latency",
        f"{result.get('latency', 0):.3f} sec"
    )


    m3.metric(
        "📥 Input Tokens",
        result.get(
            "input_tokens",
            0
        )
    )


    m4.metric(
        "📤 Output Tokens",
        result.get(
            "output_tokens",
            0
        )
    )


    m5.metric(
        "🔢 Total Tokens",
        result.get(
            "total_tokens",
            0
        )
    )


    # =====================================================
    # RETRIEVED CHUNK COUNT
    # =====================================================

    retrieved_chunks = result.get(
        "retrieved_chunks",
        []
    )


    retrieved_count = len(
        retrieved_chunks
    )


    st.caption(
        f"Retrieved chunks: **{retrieved_count}**"
    )


    # =====================================================
    # SUPPORTING CHUNK IDS
    # =====================================================

    supporting_chunk_ids = result.get(
        "supporting_chunk_ids",
        []
    )


    # Normalize IDs to integers/strings consistently

    normalized_supporting_ids = set()


    for chunk_id in supporting_chunk_ids:

        try:

            normalized_supporting_ids.add(
                int(chunk_id)
            )

        except (
            ValueError,
            TypeError
        ):

            normalized_supporting_ids.add(
                str(chunk_id)
            )


    # =====================================================
    # RETRIEVED PDF CHUNKS
    # =====================================================

    if not retrieved_chunks:

        st.warning(
            "No retrieved PDF chunks are available."
        )

        return


    st.markdown(
        "### 📚 Retrieved PDF Chunks"
    )


    st.caption(
        "⭐ = This chunk was identified by the "
        "evaluator as supporting the answer."
    )


    # =====================================================
    # DISPLAY RETRIEVED CHUNKS
    # =====================================================

    for index, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):

        # -------------------------------------------------
        # GET CHUNK DATA
        # -------------------------------------------------

        chunk_data = get_chunk_data(
            chunk=chunk,
            fallback_id=index,
        )


        chunk_id = chunk_data[
            "chunk_id"
        ]


        page = chunk_data[
            "page"
        ]


        source = chunk_data[
            "source"
        ]


        file_path = chunk_data[
            "file_path"
        ]


        content = chunk_data[
            "content"
        ]


        # -------------------------------------------------
        # SUPPORTING CHECK
        # -------------------------------------------------

        is_supporting = (
            chunk_id
            in normalized_supporting_ids
            or str(chunk_id)
            in {
                str(x)
                for x in normalized_supporting_ids
            }
        )


        # -------------------------------------------------
        # CHUNK TITLE
        # -------------------------------------------------

        if is_supporting:

            chunk_title = (
                f"⭐ Chunk {chunk_id} — SUPPORTING"
            )

        else:

            chunk_title = (
                f"📦 Chunk {chunk_id}"
            )


        # -------------------------------------------------
        # EXPANDER
        # -------------------------------------------------

        with st.expander(
            chunk_title
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
            # SUPPORTING STATUS
            # ---------------------------------------------

            if is_supporting:

                st.success(
                    "✅ This chunk was identified as "
                    "supporting the generated answer."
                )

            else:

                st.info(
                    "This chunk was retrieved as context, "
                    "but the evaluator did not identify it "
                    "as a supporting chunk."
                )


            # ---------------------------------------------
            # CONTENT
            # ---------------------------------------------

            st.text_area(
                "Chunk Content",
                str(content),
                height=220,
                key=(
                    f"answer_chunk_"
                    f"{result_key}_"
                    f"{index}_"
                    f"{chunk_id}"
                ),
            )


            # ---------------------------------------------
            # OPEN PDF PAGE
            # ---------------------------------------------

            if (
                file_path
                and os.path.exists(
                    file_path
                )
            ):

                if st.button(
                    f"📖 Open PDF Page {page}",
                    key=(
                        f"open_chunk_"
                        f"{result_key}_"
                        f"{index}_"
                        f"{chunk_id}"
                    ),
                ):

                    st.session_state[
                        "pdf_path"
                    ] = file_path


                    try:

                        st.session_state[
                            "pdf_page"
                        ] = int(page)

                    except (
                        ValueError,
                        TypeError
                    ):

                        st.session_state[
                            "pdf_page"
                        ] = 1


                    st.rerun()


# =========================================================
# PDF VIEWER
# =========================================================

pdf_path = st.session_state.get(
    "pdf_path"
)


pdf_page = int(
    st.session_state.get(
        "pdf_page",
        1
    ) or 1
)


if (
    pdf_path
    and os.path.exists(
        pdf_path
    )
):

    st.markdown("---")


    st.subheader(
        f"📖 Project PDF — Page {pdf_page}"
    )


    try:

        # -------------------------------------------------
        # OPEN PDF
        # -------------------------------------------------

        pdf_document = fitz.open(
            pdf_path
        )


        total_pages = len(
            pdf_document
        )


        # -------------------------------------------------
        # VALIDATE PAGE
        # -------------------------------------------------

        if pdf_page < 1:

            pdf_page = 1


        if pdf_page > total_pages:

            pdf_page = total_pages


        # -------------------------------------------------
        # ZERO INDEX
        # -------------------------------------------------

        pdf_page_index = (
            pdf_page - 1
        )


        page = pdf_document.load_page(
            pdf_page_index
        )


        # -------------------------------------------------
        # RENDER PAGE
        # -------------------------------------------------

        zoom = 1.5


        matrix = fitz.Matrix(
            zoom,
            zoom
        )


        pix = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )


        image_bytes = pix.tobytes(
            "png"
        )


        # -------------------------------------------------
        # DISPLAY
        # -------------------------------------------------

        st.image(
            image_bytes,
            width="stretch",
            caption=(
                f"Project PDF — Page "
                f"{pdf_page} of {total_pages}"
            ),
        )


        pdf_document.close()


    except Exception as e:

        st.error(
            f"Unable to display PDF page: {e}"
        )


# =========================================================
# ASK QUESTION BUTTON
# =========================================================

if st.button(
    "🔎 Ask Question",
    type="primary",
    use_container_width=True,
):

    # =====================================================
    # VALIDATE QUESTION
    # =====================================================

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

        st.stop()


    # =====================================================
    # CLEAR PREVIOUS PDF
    # =====================================================

    st.session_state.pop(
        "pdf_path",
        None
    )


    st.session_state.pop(
        "pdf_page",
        None
    )


    # =====================================================
    # CREATE AGENT
    # =====================================================

    agent = TaskPlanningAgent()


    # =====================================================
    # ONE MODEL
    # =====================================================

    if model_mode == "One Model":

        with st.spinner(
            f"Searching the project PDF and "
            f"asking {selected_model}..."
        ):

            result = agent.run(
                project_id=project_id,
                question=question.strip(),
                model_name=selected_model,
                top_k=top_k,
            )


        # -------------------------------------------------
        # SAVE HISTORY
        # -------------------------------------------------

        save_history(
            project_id=project_id,
            question=question,
            result=result,
        )


        # -------------------------------------------------
        # SAVE RESULT
        # -------------------------------------------------

        st.session_state[
            "task_planner_results"
        ] = [
            result
        ]


        st.session_state[
            "task_planner_question"
        ] = question


        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        if result.get(
            "success",
            True
        ):

            st.success(
                "✅ Question and answer saved "
                "to Task Planner History."
            )


    # =====================================================
    # COMPARE ALL MODELS
    # =====================================================

    else:

        results = []


        progress = st.progress(
            0
        )


        for index, model_name in enumerate(
            model_names
        ):

            with st.spinner(
                f"Running {model_name}..."
            ):

                result = agent.run(
                    project_id=project_id,
                    question=question.strip(),
                    model_name=model_name,
                    top_k=top_k,
                )


                results.append(
                    result
                )


            # -------------------------------------------------
            # SAVE MODEL RESULT
            # -------------------------------------------------

            save_history(
                project_id=project_id,
                question=question,
                result=result,
            )


            progress.progress(
                (index + 1)
                / len(model_names)
            )


        # -------------------------------------------------
        # SAVE ALL RESULTS
        # -------------------------------------------------

        st.session_state[
            "task_planner_results"
        ] = results


        st.session_state[
            "task_planner_question"
        ] = question


        st.success(
            "✅ Question and all model answers "
            "saved to Task Planner History."
        )


# =========================================================
# SHOW SAVED RESULTS
# =========================================================

results = st.session_state.get(
    "task_planner_results",
    []
)


if results:

    st.divider()


    # =====================================================
    # QUESTION
    # =====================================================

    saved_question = st.session_state.get(
        "task_planner_question",
        ""
    )


    st.markdown(
        "### ❓ Question"
    )


    st.info(
        saved_question
    )


    # =====================================================
    # DISPLAY RESULTS
    # =====================================================

    for index, result in enumerate(
        results
    ):

        display_result(
            result,
            f"result_{index}"
        )


        if index < len(results) - 1:

            st.divider()