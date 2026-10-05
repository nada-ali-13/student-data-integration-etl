from pathlib import Path

import pandas as pd

from app.sources.csv_source import extract_csv
from app.sources.api_source import extract_api
from app.sources.database_source import extract_database
from app.transformation.cleaner import clean_data
from app.transformation.integration import integrate_data
from app.validation.quality import validate_data
from app.utils.metrics import PipelineMetrics
from app.sources.web_scraping_source import scrape_students
from app.sources.mongodb_source import extract_mongodb_data


CSV_FILE = Path("data/raw/students.csv")
DB_FILE = "database/students.db"
API_URL = "http://127.0.0.1:8000/students"
WEB_SCRAPING_URL = "http://127.0.0.1:5500/web_scraping/majors.html"
MONGO_DB_PATH = "mongodb://localhost:27017/"


# def test_pipeline_summary_includes_new_records():
#     metrics = PipelineMetrics()

#     assert metrics.summary()["New Records"] == 0

#     metrics.new_records = 3

#     assert metrics.summary()["New Records"] == 3


def test_csv_loaded():
    data = extract_csv(CSV_FILE)

    assert not data.empty
    assert "student_id" in data.columns


def test_api_connected():
    data = extract_api(API_URL)

    assert not data.empty
    assert "student_id" in data.columns


def test_sqlite_extracted():
    data = extract_database(DB_FILE)

    assert not data.empty
    assert "student_id" in data.columns

def test_web_scraping_extracted():

    data = scrape_students(WEB_SCRAPING_URL)

    assert not data.empty
    assert "student_id" in data.columns

def test_mongo_extracted():
    data = extract_mongodb_data(MONGO_DB_PATH   )

    assert not data.empty
    assert "student_id" in data.columns


def test_duplicates_removed():
    data = extract_csv(CSV_FILE)

    cleaned = clean_data(data)
    cleaned = cleaned.drop_duplicates()

    assert len(cleaned) < len(data)


def test_missing_values_handled():
    data = pd.DataFrame({
        "student_id": [1, 2],
        "age": [20, None],
        "gpa": [3.5, None]
    })

    from app.transformation.transformer import fill_missing_values

    transformed = fill_missing_values(data)

    assert transformed.isna().sum().sum() == 0


def test_invalid_data_rejected():
    data = pd.DataFrame({
        "student_id": [1],
        "age": [100],
        "gpa": [5.0],
        "attendance": [110],
        "score": [150]
    })

    valid, rejected = validate_data(data)

    assert len(valid) == 0
    assert len(rejected) == 1
    assert "error_reason" in rejected.columns


def test_all_invalid_data_preserves_valid_schema():
    data = pd.DataFrame({
        "student_id": [1],
        "age": [100],
        "gpa": [5.0],
        "attendance": [110],
        "score": [150]
    })

    valid, rejected = validate_data(data)

    assert valid.empty
    assert list(valid.columns) == list(data.columns)
    assert len(rejected) == 1


def test_empty_final_output_reprocesses_all_records(tmp_path):
    data = pd.DataFrame({"student_id": [1, 2], "gpa": [3.0, 3.5]})
    output_file = tmp_path / "final_dataset.csv"
    data.head(0).to_csv(output_file, index=False)

    from app.transformation.incremental import get_new_records

    result = get_new_records(data, str(output_file))

    assert result.equals(data)


# def test_sources_integrated():
#     csv_data = extract_csv(CSV_FILE)
#     api_data = extract_api(API_URL)
#     database_data = extract_database(DB_FILE)
#     web_scraping_data = scrape_students(WEB_SCRAPING_URL)
#     mongodb_data = extract_mongodb_data(MONGO_DB_PATH) 

#     result = integrate_data(
#         csv_data,
#         api_data,
#         database_data,
#         web_scraping_data,
#         mongodb_data
#     )

#     assert not result.empty
#     assert "gpa" in result.columns
#     assert "attendance" in result.columns
#     assert "course" in result.columns


def test_final_dataset_created():
    output_file = Path("data/processed/final_dataset.csv")

    assert output_file.exists()

    data = pd.read_csv(output_file)

    assert not data.empty
    assert "student_id" in data.columns