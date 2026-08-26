import streamlit as st

from database.database import get_projects, get_ai_logs


st.set_page_config(
    page_title="Task Planner History",
    page_icon="📋",
    layout="wide",
)

st.title("📋 Task Planner History")

st.info(
    "View previous questions and AI answers from the Task Planner."
)


# ---------------------------------------------------------
# Load Projects
# ---------------------------------------------------------

projects = get_projects()

if not projects:
    st.warning("No projects found.")
    st.stop()


project_names = {
    project[1]: project[0]
    for project in projects
}


selected_project = st.selectbox(
    "📁 Select Project",
    list(project_names.keys())
)

project_id = project_names[selected_project]


# ---------------------------------------------------------
# Load AI History
# ---------------------------------------------------------

logs = get_ai_logs(project_id)


# ---------------------------------------------------------
# Only Task Planner History
# ---------------------------------------------------------

task_planner_logs = [
    log for log in logs
    if log[2] == "Task Planner"
]


# ---------------------------------------------------------
# Display History
# ---------------------------------------------------------

st.subheader("Previous Questions")


if not task_planner_logs:
    st.info(
        "No Task Planner history available for this project."
    )
    st.stop()


for log in task_planner_logs:

    with st.container(border=True):

        st.markdown("### Question")
        st.write(log[4])

        st.markdown("### AI Answer")
        st.write(log[5])

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Model", log[3])

        with col2:
            st.metric("📥 Input Tokens", log[6])

        with col3:
            st.metric("📤 Output Tokens", log[7])

        with col4:
            st.metric("🔢 Total Tokens", log[8])

        st.caption(
            f"Latency: {log[9]:.3f} sec"
        )

        st.caption(
            f"Created: {log[11]}"
        )