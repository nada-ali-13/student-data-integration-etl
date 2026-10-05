from pymongo import MongoClient
import pandas as pd


def extract_mongodb_data(db_path: str) -> pd.DataFrame:
    client = MongoClient(
        db_path
    )

    db = client["student_database"]

    collection = db["students"]

    documents = list(
        collection.find()
    )

    df = pd.DataFrame(documents)

    return df

