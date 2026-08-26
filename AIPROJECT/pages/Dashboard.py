import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

from config.config import DATABASE_PATH


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI Model Performance Dashboard")

st.caption(
    "Compare answer quality manually, plus latency and token usage "
    "for every RAG request."
)


# ============================================================
# LOAD AI LOGS
# ============================================================

conn = sqlite3.connect(DATABASE_PATH)

df = pd.read_sql(
    """
    SELECT
        ai_logs.*,
        projects.name AS project_name
    FROM ai_logs
    LEFT JOIN projects
        ON projects.id = ai_logs.project_id
    ORDER BY ai_logs.id DESC
    """,
    conn,
)

conn.close()


# ============================================================
# NO DATA
# ============================================================

if df.empty:
    st.info(
        "No AI requests have been recorded yet. "
        "Ask a question from PDF RAG Q&A."
    )
    st.stop()


# ============================================================
# FILTERS
# ============================================================

projects = ["All"] + sorted(
    df["project_name"]
    .fillna("Unknown")
    .unique()
    .tolist()
)

models = ["All"] + sorted(
    df["model"]
    .dropna()
    .unique()
    .tolist()
)

col1, col2 = st.columns(2)

project_filter = col1.selectbox(
    "Project",
    projects,
)

model_filter = col2.selectbox(
    "Model",
    models,
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df.copy()

if project_filter != "All":
    filtered = filtered[
        filtered["project_name"]
        .fillna("Unknown")
        == project_filter
    ]

if model_filter != "All":
    filtered = filtered[
        filtered["model"] == model_filter
    ]


# ============================================================
# NO MATCHING DATA
# ============================================================

if filtered.empty:
    st.warning(
        "No records match the selected filters."
    )
    st.stop()


# ============================================================
# SUMMARY
# ============================================================

st.subheader("Summary")

c1, c2, c3, c4 = st.columns(4)


# Total requests

c1.metric(
    "Total Requests",
    len(filtered),
)


# Total input tokens

c2.metric(
    "Total Input Tokens",
    f'{int(filtered["input_tokens"].fillna(0).sum()):,}',
)


# Total output tokens

c3.metric(
    "Total Output Tokens",
    f'{int(filtered["output_tokens"].fillna(0).sum()):,}',
)


# Total tokens

c4.metric(
    "Total Tokens",
    f'{int(filtered["tokens"].fillna(0).sum()):,}',
)


st.divider()


# ============================================================
# MODEL / REQUEST COMPARISON
# ============================================================

st.subheader("Model Comparison — Every Request")

comparison_columns = [
    "id",
    "model",
    "latency",
    "input_tokens",
    "output_tokens",
    "tokens",
]


# Only use columns that actually exist

comparison_columns = [
    column
    for column in comparison_columns
    if column in filtered.columns
]


comparison = filtered[
    comparison_columns
].copy()


# ============================================================
# RENAME COLUMNS
# ============================================================

comparison = comparison.rename(
    columns={
        "id": "Request",
        "model": "Model",
        "latency": "Latency (sec)",
        "input_tokens": "Input Tokens",
        "output_tokens": "Output Tokens",
        "tokens": "Total Tokens",
    }
)


# ============================================================
# FORMAT LATENCY
# ============================================================

if "Latency (sec)" in comparison.columns:
    comparison["Latency (sec)"] = (
        pd.to_numeric(
            comparison["Latency (sec)"],
            errors="coerce",
        )
        .round(3)
    )


# ============================================================
# DISPLAY EVERY REQUEST
# ============================================================

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# LATENCY CHART
# ============================================================

if (
    "Request" in comparison.columns
    and "Latency (sec)" in comparison.columns
):

    chart1 = px.bar(
        comparison,
        x="Request",
        y="Latency (sec)",
        title="Latency for Each Request",
        text_auto=".3f",
    )

    chart1.update_layout(
        xaxis_title="Request",
        yaxis_title="Latency (seconds)",
    )

    st.plotly_chart(
        chart1,
        use_container_width=True,
    )


# ============================================================
# REQUEST HISTORY
# ============================================================

st.subheader("Request History")

display_cols = [
    column
    for column in [
        "id",
        "project_name",
        "agent",
        "model",
        "input_text",
        "input_tokens",
        "output_tokens",
        "tokens",
        "latency",
        "created_at",
    ]
    if column in filtered.columns
]


history = filtered[
    display_cols
].head(100).copy()


# ============================================================
# FORMAT LATENCY
# ============================================================

if "latency" in history.columns:
    history["latency"] = (
        pd.to_numeric(
            history["latency"],
            errors="coerce",
        )
        .round(3)
    )


# ============================================================
# RENAME HISTORY COLUMNS
# ============================================================

history = history.rename(
    columns={
        "id": "Request",
        "project_name": "Project",
        "agent": "Agent",
        "model": "Model",
        "input_text": "Question",
        "input_tokens": "Input Tokens",
        "output_tokens": "Output Tokens",
        "tokens": "Total Tokens",
        "latency": "Latency (sec)",
        "created_at": "Created At",
    }
)


# ============================================================
# DISPLAY HISTORY
# ============================================================

st.dataframe(
    history,
    use_container_width=True,
    hide_index=True,
)