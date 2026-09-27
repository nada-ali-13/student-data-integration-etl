from pathlib import Path
import pandas as pd


def extract_csv(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    data = pd.read_csv(file_path)

    if data.empty:
        raise ValueError("CSV file is empty")

    return data