import pandas as pd


def integrate_data(
    csv_data: pd.DataFrame,
    api_data: pd.DataFrame,
    database_data: pd.DataFrame,
    web_scraping_data: pd.DataFrame,
    mongodb_data: pd.DataFrame
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

    integrated = pd.merge(
        integrated,
        web_scraping_data,
        on="student_id",
        how="left"
    )

    integrated = pd.merge(
        integrated,
        mongodb_data,
        on="student_id",
        how="left"
    )

    # integrated = pd.concat(
    #     [csv_data, api_data, database_data, web_scraping_data, mongodb_data],
    #     ignore_index=True,
    #     sort=False
    # )

    return integrated