import sqlite3

from config.config import DATABASE_PATH


# ----------------------------------------
# DATABASE CONNECTION
# ----------------------------------------

def get_connection():
    return sqlite3.connect(DATABASE_PATH)


# ----------------------------------------
# INITIALIZE DATABASE
# ----------------------------------------

def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # ----------------------------------------
    # Projects
    # ----------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            start_date TEXT,
            deadline TEXT,
            status TEXT DEFAULT 'Active'
        )
    """)

    # ----------------------------------------
    # Tasks
    # ----------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Todo',
            assigned_to INTEGER,
            deadline TEXT,

            FOREIGN KEY(project_id)
                REFERENCES projects(id),

            FOREIGN KEY(assigned_to)
                REFERENCES team_members(id)
        )
    """)

    # ----------------------------------------
    # AI Logs
    # ----------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            agent TEXT,
            model TEXT,
            input_text TEXT,
            output_text TEXT,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            tokens INTEGER DEFAULT 0,
            latency REAL DEFAULT 0,
            cost REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(project_id)
                REFERENCES projects(id)
        )
    """)
    # ----------------------------------------
    # Project Documents
    # ----------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            file_name TEXT,
            file_path TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(project_id)
                REFERENCES projects(id)
        )
    """)

    # ========================================
    # MIGRATION: PROJECTS
    # ========================================

    cursor.execute("PRAGMA table_info(projects)")
    project_columns = [row[1] for row in cursor.fetchall()]

    if "name" not in project_columns:

        cursor.execute(
            "ALTER TABLE projects ADD COLUMN name TEXT"
        )

        if "project_name" in project_columns:

            cursor.execute("""
                UPDATE projects
                SET name = project_name
                WHERE name IS NULL
            """)

    # ========================================
    # MIGRATION: AI LOGS
    # ========================================

    cursor.execute("PRAGMA table_info(ai_logs)")
    ai_log_columns = [row[1] for row in cursor.fetchall()]

    if "input_tokens" not in ai_log_columns:

        cursor.execute("""
            ALTER TABLE ai_logs
            ADD COLUMN input_tokens INTEGER DEFAULT 0
        """)

    if "output_tokens" not in ai_log_columns:

        cursor.execute("""
            ALTER TABLE ai_logs
            ADD COLUMN output_tokens INTEGER DEFAULT 0
        """)

    if "tokens" not in ai_log_columns:

        cursor.execute("""
            ALTER TABLE ai_logs
            ADD COLUMN tokens INTEGER DEFAULT 0
        """)

    if "latency" not in ai_log_columns:

        cursor.execute("""
            ALTER TABLE ai_logs
            ADD COLUMN latency REAL DEFAULT 0
        """)

    if "cost" not in ai_log_columns:

        cursor.execute("""
            ALTER TABLE ai_logs
            ADD COLUMN cost REAL DEFAULT 0
        """)

    # ========================================
    # MIGRATION: TASKS
    # ========================================

    cursor.execute("PRAGMA table_info(tasks)")
    task_columns = [row[1] for row in cursor.fetchall()]

    if "project_id" not in task_columns:

        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN project_id INTEGER
        """)

    if "description" not in task_columns:

        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN description TEXT
        """)

    if "priority" not in task_columns:

        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN priority TEXT DEFAULT 'Medium'
        """)

    if "status" not in task_columns:

        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN status TEXT DEFAULT 'Todo'
        """)

    if "assigned_to" not in task_columns:

        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN assigned_to INTEGER
        """)

    if "deadline" not in task_columns:

        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN deadline TEXT
        """)

    # ========================================
    # FINISH DATABASE INITIALIZATION
    # ========================================

    conn.commit()
    conn.close()


# ----------------------------------------
# DELETE PROJECT
# ----------------------------------------

def delete_project(project_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # ------------------------------------
        # Delete related records
        # ------------------------------------

        cursor.execute(
            "DELETE FROM tasks WHERE project_id = ?",
            (project_id,)
        )

        cursor.execute(
            "DELETE FROM sprints WHERE project_id = ?",
            (project_id,)
        )

        cursor.execute(
            "DELETE FROM meetings WHERE project_id = ?",
            (project_id,)
        )

        cursor.execute(
            "DELETE FROM bugs WHERE project_id = ?",
            (project_id,)
        )

        cursor.execute(
            "DELETE FROM ai_logs WHERE project_id = ?",
            (project_id,)
        )

        cursor.execute(
            "DELETE FROM sprint_history WHERE project_id = ?",
            (project_id,)
        )

        cursor.execute(
            "DELETE FROM timeline WHERE project_id = ?",
            (project_id,)
        )

        cursor.execute(
            "DELETE FROM project_risks WHERE project_id = ?",
            (project_id,)
        )

        cursor.execute(
            "DELETE FROM workload_balance WHERE project_id = ?",
            (project_id,)
        )

        cursor.execute(
            "DELETE FROM standup_history WHERE project_id = ?",
            (project_id,)
        )

        cursor.execute(
            "DELETE FROM meeting_history WHERE project_id = ?",
            (project_id,)
        )

        cursor.execute(
            "DELETE FROM deadline_history WHERE project_id = ?",
            (project_id,)
        )

        cursor.execute(
            "DELETE FROM project_documents WHERE project_id = ?",
            (project_id,)
        )

        # ------------------------------------
        # Finally delete project
        # ------------------------------------

        cursor.execute(
            "DELETE FROM projects WHERE id = ?",
            (project_id,)
        )

        conn.commit()

        return True

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()


# ----------------------------------------
# SAVE AI LOG
# ----------------------------------------

def save_ai_log(
    project_id,
    agent,
    model,
    input_text,
    output_text,
    input_tokens=0,
    output_tokens=0,
    tokens=0,
    latency=0.0,
    cost=0.0
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ai_logs
        (
            project_id,
            agent,
            model,
            input_text,
            output_text,
            input_tokens,
            output_tokens,
            tokens,
            latency,
            cost
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        project_id,
        agent,
        model,
        input_text,
        output_text,
        input_tokens,
        output_tokens,
        tokens,
        latency,
        cost
    ))

    conn.commit()
    conn.close()


# ----------------------------------------
# GET ALL PROJECTS
# ----------------------------------------

def get_projects():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            description,
            deadline,
            status
        FROM projects
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ----------------------------------------
# GET TASKS
# ----------------------------------------

def get_tasks(project_id=None):

    conn = get_connection()
    cursor = conn.cursor()

    if project_id is not None:

        cursor.execute("""
            SELECT
                id,
                project_id,
                title,
                description,
                priority,
                status,
                assigned_to,
                deadline
            FROM tasks
            WHERE project_id = ?
            ORDER BY id DESC
        """, (project_id,))

    else:

        cursor.execute("""
            SELECT
                id,
                project_id,
                title,
                description,
                priority,
                status,
                assigned_to,
                deadline
            FROM tasks
            ORDER BY id DESC
        """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ----------------------------------------
# GET AI LOGS
# ----------------------------------------

def get_ai_logs(project_id=None):

    conn = get_connection()
    cursor = conn.cursor()

    if project_id:

        cursor.execute("""
            SELECT
                id,
                project_id,
                agent,
                model,
                input_text,
                output_text,
                input_tokens,
                output_tokens,
                tokens,
                latency,
                cost,
                created_at
            FROM ai_logs
            WHERE project_id = ?
            ORDER BY id DESC
        """, (project_id,))

    else:

        cursor.execute("""
            SELECT
                id,
                project_id,
                agent,
                model,
                input_text,
                output_text,
                input_tokens,
                output_tokens,
                tokens,
                latency,
                cost,
                created_at
            FROM ai_logs
            ORDER BY id DESC
        """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ----------------------------------------
# RUN DATABASE INITIALIZATION
# ----------------------------------------

if __name__ == "__main__":
    initialize_database()