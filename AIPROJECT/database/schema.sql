CREATE TABLE IF NOT EXISTS projects (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    description TEXT,

    start_date TEXT,

    deadline TEXT,

    status TEXT DEFAULT 'Active'

);



CREATE TABLE IF NOT EXISTS team_members (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    role TEXT,

    workload INTEGER DEFAULT 0

);



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

);



CREATE TABLE IF NOT EXISTS sprints (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER,

    sprint_name TEXT,

    goal TEXT,

    start_date TEXT,

    end_date TEXT,


    FOREIGN KEY(project_id)
    REFERENCES projects(id)

);



CREATE TABLE IF NOT EXISTS meetings (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER,

    meeting_title TEXT,

    notes TEXT,

    summary TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,


    FOREIGN KEY(project_id)
    REFERENCES projects(id)

);



CREATE TABLE IF NOT EXISTS bugs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER,

    title TEXT,

    description TEXT,

    severity TEXT,

    priority TEXT,

    status TEXT DEFAULT 'Open',


    FOREIGN KEY(project_id)
    REFERENCES projects(id)

);



CREATE TABLE IF NOT EXISTS ai_logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER,

    agent TEXT,
    model TEXT,
    input_text TEXT,
    output_text TEXT,
    tokens INTEGER,
    latency REAL,
    cost REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS sprint_history (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER,

    sprint_duration TEXT,

    sprint_plan TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE IF NOT EXISTS timeline (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER,

    week TEXT,

    task_name TEXT,

    status TEXT DEFAULT 'Pending',

    FOREIGN KEY(project_id)
    REFERENCES projects(id)

);

CREATE TABLE IF NOT EXISTS project_risks (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER,

    risk_analysis TEXT,

    FOREIGN KEY(project_id)
    REFERENCES projects(id)

);

CREATE TABLE IF NOT EXISTS workload_balance (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER,

    workload_analysis TEXT,

    FOREIGN KEY(project_id)
    REFERENCES projects(id)

);


----------------------------------------------------------
-- Daily Standup History
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS standup_history (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER,

    project_name TEXT,

    updates TEXT,

    summary TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


----------------------------------------------------------
-- Meeting Summary History
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS meeting_history (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER,

    project_name TEXT,

    meeting_notes TEXT,

    meeting_summary TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


----------------------------------------------------------
-- Deadline Prediction History
----------------------------------------------------------

CREATE TABLE IF NOT EXISTS deadline_history (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER,

    project_name TEXT,

    project_details TEXT,

    prediction TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);