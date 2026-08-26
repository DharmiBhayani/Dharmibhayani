import pandas as pd
from mypackages.database import get_connection

def show_single_student_dataframe(student):
    data = {
        "Roll No": [student.roll_no],
        "Name": [student.name],
        "Maths": [student.marks[0]],
        "Science": [student.marks[1]],
        "Physics": [student.marks[2]],
        "Chemistry": [student.marks[3]],
        "Biology": [student.marks[4]],
        "Percentage": [round(student.percentage, 2)]
    }
    df = pd.DataFrame(data)
    print("\n===== STUDENT DATAFRAME =====")
    print(df.to_string(index=False))


def show_dataframe():
    try:
        conn = get_connection()
        query = """
            SELECT 
                roll_no AS `Roll No`, 
                name AS `Name`, 
                maths AS `Maths`, 
                science AS `Science`, 
                physics AS `Physics`, 
                chemistry AS `Chemistry`, 
                biology AS `Biology`, 
                percentage AS `Percentage` 
            FROM students
        """
        
        df = pd.read_sql(query, conn)
        
        if df.empty:
            print("\nNo Data Available in Database. Please add a student first.")
            return

        print("\n===== DATAFRAME VIEW =====")
        print(df.to_string(index=False))

        print("\n===== CLEANED DATA (No Duplicates/NaNs) =====")
        df = df.drop_duplicates()
        df = df.fillna(0)
        print(df.to_string(index=False))

    except Exception as e:
        print(f"Error parsing database values to DataFrame: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()