import mysql.connector

def get_connection():
    # Default XAMPP Configurations (User: root, Password: empty)
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="studentdb"
    )

def initialize_db():
    try:
        # Step 1: Connect to MySQL server safely without a database selected to create it
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS studentdb")
        cursor.close()
        conn.close()

        # Step 2: Establish connection and construct target tables
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                roll_no INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                maths INT NOT NULL,
                science INT NOT NULL,
                physics INT NOT NULL,
                chemistry INT NOT NULL,
                biology INT NOT NULL,
                percentage FLOAT NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database & Tables verified/initialized successfully.")
    except Exception as e:
        print(f"Error initializing database configuration: {e}")