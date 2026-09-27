import sqlite3
from pathlib import Path

DB_PATH = Path("students.db")

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY,
    course_name TEXT NOT NULL,
    credit_hours INTEGER NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS enrollments (
    student_id INTEGER,
    course_id INTEGER,
    semester TEXT,
    score REAL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
)
""")

courses = [
    (1, "Python Programming", 3),
    (2, "Database Systems", 3),
    (3, "Artificial Intelligence", 4)
]

enrollments = [
    (1001, 1, "2026-1", 92),
    (1002, 1, "2026-1", 88),
    (1003, 2, "2026-1", 76),
    (1004, 2, "2026-1", 91),
    (1005, 3, "2026-1", 85),
    (1006, 3, "2026-1", 95),
    (1007, 1, "2026-1", 70),
    (1008, 2, "2026-1", 82),
    (1009, 3, "2026-1", 78),
    (1010, 1, "2026-1", 90)
]

cursor.executemany(
    """
    INSERT OR IGNORE INTO courses
    (course_id, course_name, credit_hours)
    VALUES (?, ?, ?)
    """,
    courses
)

cursor.executemany(
    """
    INSERT INTO enrollments
    (student_id, course_id, semester, score)
    VALUES (?, ?, ?, ?)
    """,
    enrollments
)

connection.commit()
connection.close()

print("Database created successfully.")