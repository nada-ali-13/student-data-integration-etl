import pandas as pd


def fill_missing_values(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()

    if "gpa" in data.columns:
        data["gpa"] = data["gpa"].fillna(
            data["gpa"].median()
        )

    if "attendance" in data.columns:
        data["attendance"] = data["attendance"].fillna(
            data["attendance"].median()
        )

    if "age" in data.columns:
        data["age"] = data["age"].fillna(
            data["age"].median()
        )

    if "score" in data.columns:
        data["score"] = data["score"].fillna(
            data["score"].median()
        )

    return data


def create_derived_columns(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()

    def performance(gpa):
        if gpa >= 3.5:
            return "Excellent"
        elif gpa >= 3.0:
            return "Very Good"
        elif gpa >= 2.5:
            return "Good"
        elif gpa >= 2.0:
            return "Acceptable"
        return "At Risk"

    data["performance_level"] = data["gpa"].apply(performance)

    data["attendance_status"] = data["attendance"].apply(
        lambda value: "Good" if value >= 75 else "Low"
    )

    return data


def transform_data(data: pd.DataFrame) -> pd.DataFrame:
    data = fill_missing_values(data)
    data = create_derived_columns(data)

    return data