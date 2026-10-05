import pandas as pd


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()

    # remove duplicates 
    data = data.drop_duplicates()

    # Normalize column names
    data.columns = (
        data.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Clean text columns
    text_columns = data.select_dtypes(
        include="object"
    ).columns

    for column in text_columns:
        data[column] = data[column].apply(
            lambda value: value.strip().title()
            if isinstance(value, str)
            else value
        )

    # Convert numeric columns
    numeric_columns = [
        "student_id",
        "age",
        "gpa",
        "attendance",
        "score"
    ]

    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    return data