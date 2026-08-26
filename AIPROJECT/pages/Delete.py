import streamlit as st

from database.database import (
    get_projects,
    delete_project
)

projects = get_projects()

project_names = {
    project[1]: project[0]
    for project in projects
}

selected_project = st.selectbox(
    "Select Project",
    list(project_names.keys())
)

project_id = project_names[selected_project]

if st.button("🗑 Delete Project"):

    delete_project(project_id)

    st.success("Project deleted successfully!")

    st.rerun()