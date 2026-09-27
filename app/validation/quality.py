import pandas as pd


def validate_source_ids(data: pd.DataFrame):
    errors = []

    if "student_id" not in data.columns:
        return ["Missing student_id column"]

    if data["student_id"].isna().any():
        errors.append("student_id contains NULL values")

    if data["student_id"].duplicated().any():
        errors.append("student_id contains duplicates")

    return errors


def validate_data(data: pd.DataFrame):
    valid_rows = []
    rejected_rows = []

    for _, row in data.iterrows():

        reasons = []

        student_id = row.get("student_id")
        age = row.get("age")
        gpa = row.get("gpa")
        attendance = row.get("attendance")
        score = row.get("score")

        if pd.isna(student_id):
            reasons.append("Missing student_id")

        if pd.notna(age) and not 16 <= age <= 80:
            reasons.append("Invalid Age")

        if pd.notna(gpa) and not 0 <= gpa <= 4:
            reasons.append("Invalid GPA")

        if pd.notna(attendance) and not 0 <= attendance <= 100:
            reasons.append("Invalid Attendance")

        if pd.notna(score) and not 0 <= score <= 100:
            reasons.append("Invalid Score")

        if reasons:
            rejected = row.to_dict()
            rejected["error_reason"] = "; ".join(reasons)
            rejected_rows.append(rejected)
        else:
            valid_rows.append(row.to_dict())

    return (
        pd.DataFrame(valid_rows, columns=data.columns),
        pd.DataFrame(rejected_rows)
    )