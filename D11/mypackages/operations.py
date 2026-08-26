from mypackages.student import Student
from mypackages.dataframeview import show_single_student_dataframe
from mypackages.database import get_connection

# CREATE
def add_student():
    # ROLL NUMBER USER INPUT
    while True:
        try:
            roll_no = int(input("Enter Roll No : "))
            if roll_no <= 0:
                print("Enter a valid roll number")
                continue

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT roll_no FROM students WHERE roll_no = %s", (roll_no,))
            if cursor.fetchone():
                print("Roll number already exists!")
                cursor.close()
                conn.close()
                continue
            
            cursor.close()
            conn.close()
            break
        except ValueError:
            print("Enter a valid integer roll number.")
        except Exception as e:
            print(f"Database error: {e}")
            return

    # NAME USER INPUT
    while True:
        name = input("Enter Name : ").strip()
        if name.replace(" ", "").isalpha() and len(name) > 0:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM students WHERE LOWER(name) = %s", (name.lower(),))
                if cursor.fetchone():
                    print("Student name already exists!")
                    cursor.close()
                    conn.close()
                    continue
                cursor.close()
                conn.close()
                break
            except Exception as e:
                print(f"Database error: {e}")
                return
        else:
            print("Enter a valid alphabetical name.")

    # MARKS USER INPUT
    marks = []
    subjects = ["Maths", "Science", "Physics", "Chemistry", "Biology"]

    for subject in subjects:
        while True:
            try:
                mark = int(input(f"Enter {subject} Marks : "))
                if mark < 0 or mark > 100:
                    print("Marks should be between 0 and 100.")
                    continue
                marks.append(mark)
                break
            except ValueError:
                print("Enter valid numerical marks.")

    # INSTANTIATE MODEL & PERSIST TO DB
    student = Student(roll_no, name, marks)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO students (roll_no, name, maths, science, physics, chemistry, biology, percentage) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (student.roll_no, student.name, marks[0], marks[1], marks[2], marks[3], marks[4], student.percentage)
        cursor.execute(query, values)
        conn.commit()
        print("\nStudent Added Successfully to MySQL Database!")
    except Exception as e:
        print(f"Failed insertion operational action: {e}")
    finally:
        cursor.close()
        conn.close()

# READ SINGLE VIA USER INPUT
def view_student():
    while True:
        try:
            roll_no = int(input("Enter Roll No to view : "))
            if roll_no <= 0:
                print("Enter a valid roll number.")
                continue
            break
        except ValueError:
            print("Enter a valid integer.")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE roll_no = %s", (roll_no,))
        row = cursor.fetchone()
        
        if row:
            marks = [row[2], row[3], row[4], row[5], row[6]]
            student = Student(row[0], row[1], marks)
            student.display()
            show_single_student_dataframe(student)
        else:
            print("Student Not Found.")
    except Exception as e:
        print(f"Database tracking error: {e}")
    finally:
        cursor.close()
        conn.close()

# READ ALL
def view_all_students():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        rows = cursor.fetchall()
        
        if not rows:
            print("No Student Data Available in database records.")
            return

        print("\n===== ALL REGISTERED STUDENTS =====")
        for row in rows:
            marks = [row[2], row[3], row[4], row[5], row[6]]
            student = Student(row[0], row[1], marks)
            student.display()
    except Exception as e:
        print(f"Database reading error: {e}")
    finally:
        cursor.close()
        conn.close()

# UPDATE VIA USER INPUT
def update_student():
    while True:
        try:
            roll = int(input("Enter Roll No to Update : "))
            if roll <= 0:
                print("Enter a valid roll number.")
                continue
            break
        except ValueError:
            print("Please enter an integer value.")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE roll_no = %s", (roll,))
        if not cursor.fetchone():
            print("Student Not Found.")
            cursor.close()
            conn.close()
            return

        while True:
            new_name = input("Enter New Name : ").strip()
            if new_name.replace(" ", "").isalpha() and len(new_name) > 0:
                break
            else:
                print("Enter a valid alphabetical name.")

        new_marks = []
        subjects = ["Maths", "Science", "Physics", "Chemistry", "Biology"]
        for sub in subjects:
            while True:
                try:
                    mark = int(input(f"Enter New {sub} Marks : "))
                    if mark < 0 or mark > 100:
                        print("Marks should be between 0 and 100.")
                        continue
                    new_marks.append(mark)
                    break
                except ValueError:
                    print("Enter valid numerical marks.")

        temp_student = Student(roll, new_name, new_marks)
        query = """
            UPDATE students 
            SET name = %s, maths = %s, science = %s, physics = %s, chemistry = %s, biology = %s, percentage = %s 
            WHERE roll_no = %s
        """
        cursor.execute(query, (new_name, new_marks[0], new_marks[1], new_marks[2], new_marks[3], new_marks[4], temp_student.percentage, roll))
        conn.commit()
        print("Student Data Record updated successfully.")
    except Exception as e:
        print(f"Database update event failure: {e}")
    finally:
        cursor.close()
        conn.close()

# DELETE VIA USER INPUT
def delete_student():
    while True:
        try:
            roll = int(input("Enter Roll No to Delete : "))
            if roll <= 0:
                print("Enter valid roll number.")
                continue
            break
        except ValueError:
            print("Please enter an integer value.")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE roll_no = %s", (roll,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print("Student Database Record Deleted Successfully.")
        else:
            print("Student record not found.")
    except Exception as e:
        print(f"Database execution error on deletion: {e}")
    finally:
        cursor.close()
        conn.close()