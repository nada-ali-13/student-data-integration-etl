import json
import logging
from pathlib import Path

import pandas as pd

from app.sources.csv_source import extract_csv
from app.sources.api_source import extract_api
from app.sources.database_source import extract_database
from app.sources.web_scraping_source import scrape_students
from app.sources.mongodb_source import extract_mongodb_data

from app.transformation.cleaner import clean_data
from app.transformation.integration import integrate_data
from app.transformation.transformer import transform_data

from app.validation.quality import (
    validate_source_ids,
    validate_data
)

from app.output.csv_writer import save_csv

from app.utils.logger import setup_logger
from app.utils.metrics import PipelineMetrics
from app.transformation.incremental import get_new_records



def load_config():
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)


def run_pipeline():

    config = load_config()

    logger = setup_logger(
        config["paths"]["log"]
    )

    metrics = PipelineMetrics()

    logger.info("Pipeline started")

    # -------------------------
    # Extract
    # -------------------------

    logger.info("CSV extraction started")

    csv_data = extract_csv(
        Path(config["paths"]["csv"])
    )

    metrics.csv_records = len(csv_data)

    logger.info(
        f"CSV records: {len(csv_data)}"
    )

    logger.info("API extraction started")

    api_data = extract_api(
        config["api"]["url"],
        config["api"]["timeout"]
    )

    metrics.api_records = len(api_data)

    logger.info(
        f"API records: {len(api_data)}"
    )

    logger.info("Database extraction started")

    database_data = extract_database(
        config["paths"]["database"]
    )

    metrics.database_records = len(database_data)

    logger.info(
        f"Database records: {len(database_data)}"
    )

    logger.info("web scraping extraction started")

    web_scraping_data = scrape_students(
        config["paths"]["web_scraping"]
    )

    metrics.web_scraping_records = len(web_scraping_data)

    logger.info(
        f"Web scraping records: {len(web_scraping_data)}"
    )

    logger.info("mongodb extraction started")

    mongodb_data = extract_mongodb_data(
        config["paths"]["mongodb"]
    )

    metrics.mongodb_records = len(mongodb_data)

    logger.info(
        f"MongoDB records: {len(mongodb_data)}"
    )




    # -------------------------
    # Source Validation
    # -------------------------

    logger.info("Source validation started")

    csv_errors = validate_source_ids(csv_data)
    api_errors = validate_source_ids(api_data)

    if csv_errors:
        logger.warning(
            f"CSV validation errors: {csv_errors}"
        )

    if api_errors:
        logger.warning(
            f"API validation errors: {api_errors}"
        )

    # -------------------------
    # Cleaning
    # -------------------------

    logger.info("Cleaning started")

    metrics.duplicate_records = (
        csv_data.duplicated().sum()
        + api_data.duplicated().sum()
        + database_data.duplicated().sum()
        + web_scraping_data.duplicated().sum()
        + mongodb_data.duplicated().sum()
    )

    metrics.missing_values = (
    csv_data.isna().sum().sum()
    + api_data.isna().sum().sum()
    + database_data.isna().sum().sum()
    + web_scraping_data.isna().sum().sum()
    + mongodb_data.isna().sum().sum()
)

    csv_data = clean_data(csv_data)
    api_data = clean_data(api_data)
    database_data = clean_data(database_data)
    web_scraping_data = clean_data(web_scraping_data)
    mongodb_data = clean_data(mongodb_data)

    # -------------------------
    # Integration
    # -------------------------

    logger.info("Integration started")

    integrated_data = integrate_data(
        csv_data,
        api_data,
        database_data,
        web_scraping_data,  
        mongodb_data
    )

    metrics.integrated_records = len(
        integrated_data
    )

    logger.info(
        f"Integrated records: {len(integrated_data)}"
    )

    # -------------------------
    # Incremental Processing
    # -------------------------

    logger.info("Incremental processing started")

    integrated_data = get_new_records(
        integrated_data,
        config["paths"]["final_output"]
    )

    metrics.new_records = len(integrated_data)

    logger.info(
        f"New records to process: {len(integrated_data)}"
    )

    if integrated_data.empty:
        logger.info("No new records to process")

        summary = metrics.summary()

        print("\n-----------------------------------")
        print("PIPELINE EXECUTION SUMMARY")
        print("-----------------------------------")

        for key, value in summary.items():
            print(f"{key}: {value}")

        print("-----------------------------------")
        print("No new records. Pipeline completed successfully.")

        return

    # -------------------------
    # Validation
    # -------------------------

    logger.info("Final validation started")

    valid_data, rejected_data = validate_data(
        integrated_data
    )

    metrics.valid_records = len(valid_data)
    metrics.rejected_records = len(rejected_data)

    # -------------------------
    # Transformation
    # -------------------------

    logger.info("Transformation started")

    valid_data = transform_data(valid_data)

    # -------------------------
    # Data Lineage
    # -------------------------

    valid_data["source"] = (
        "CSV+API+DATABASE"
    )

    # -------------------------
    # Final Validation
    # -------------------------

    final_valid_data, final_rejected = validate_data(
        valid_data
    )


    if not final_rejected.empty:
        rejected_data = (
            __import__("pandas").concat(
                [rejected_data, final_rejected],
                ignore_index=True
            )
        )

    metrics.valid_records = len(
        final_valid_data
    )

    metrics.rejected_records = len(
        rejected_data
    )

    # -------------------------
    # Load
    # -------------------------

    final_output = Path(config["paths"]["final_output"])

    if final_output.exists() and final_output.stat().st_size > 0:
        try:
            existing_final_data = pd.read_csv(final_output)
        except pd.errors.EmptyDataError:
            existing_final_data = None

        if existing_final_data is not None:
            final_valid_data = pd.concat(
            [existing_final_data, final_valid_data],
                ignore_index=True
            )

    save_csv(
        final_valid_data,
        config["paths"]["final_output"]
    )

    save_csv(
        rejected_data,
        config["paths"]["rejected_output"]
    )

    logger.info("Final dataset created")

    # -------------------------
    # Metrics
    # -------------------------

    summary = metrics.summary()

    logger.info("PIPELINE EXECUTION SUMMARY")

    for key, value in summary.items():
        logger.info(f"{key}: {value}")

    print("\n-----------------------------------")
    print("PIPELINE EXECUTION SUMMARY")
    print("-----------------------------------")

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("-----------------------------------")
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()