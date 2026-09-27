from pathlib import Path
import pandas as pd


def get_new_records(
    data: pd.DataFrame,
    output_file: str
) -> pd.DataFrame:

    path = Path(output_file)

    if not path.exists() or path.stat().st_size == 0:
        return data

    try:
        old_data = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return data

    if old_data.empty or "student_id" not in old_data.columns:
        return data

    old_ids = set(
        old_data["student_id"].dropna()
    )

    return data[
        ~data["student_id"].isin(old_ids)
    ].copy()