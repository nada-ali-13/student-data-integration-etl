import sqlite3
import pandas as pd


def extract_database(database_path: str) -> pd.DataFrame:
    connection = sqlite3.connect(database_path)

    query = """
        SELECT
            e.student_id,
            c.course_name AS course,
            e.score,
            e.semester
        FROM enrollments e
        JOIN courses c
            ON e.course_id = c.course_id
    """

    data = pd.read_sql_query(query, connection)

    connection.close()

    if data.empty:
        raise ValueError("Database returned no data")

    return data