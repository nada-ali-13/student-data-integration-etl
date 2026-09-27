from pathlib import Path
import pandas as pd


def save_csv(data: pd.DataFrame, file_path: str):
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data.to_csv(
        path,
        index=False,
        encoding="utf-8-sig"
    )