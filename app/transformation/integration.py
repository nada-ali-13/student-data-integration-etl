import pandas as pd


def integrate_data(
    csv_data: pd.DataFrame,
    api_data: pd.DataFrame,
    database_data: pd.DataFrame
) -> pd.DataFrame:

    integrated = pd.merge(
        csv_data,
        api_data,
        on="student_id",
        how="left"
    )

    integrated = pd.merge(
        integrated,
        database_data,
        on="student_id",
        how="left"
    )

    return integrated