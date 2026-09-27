# Student Data Pipeline

## 1. Project Overview

This project is a data pipeline that processes student data from three different sources. It cleans, integrates, validates, and saves the result as CSV files.

The pipeline supports incremental processing. When a final output already exists, only records with new `student_id` values are processed.

## 2. Architecture

The project is organized into separate layers, with each layer responsible for a specific task:

```text
student_data_pipeline/
├── main.py                         # Pipeline entry point
├── config.json                     # Paths and API settings
├── mock_api.py                     # Local mock API
├── app/
│   ├── sources/                    # Data extraction from sources
│   ├── transformation/             # Cleaning, transformation, and integration
│   ├── validation/                 # Data quality validation
│   ├── output/                     # Output file writing
│   └── utils/                      # Logging and metrics
├── data/
│   ├── raw/                        # Raw input data
│   ├── processed/                  # Final processed data
│   └── rejected/                   # Rejected records
├── database/                       # SQLite database creation
├── logs/                           # Pipeline logs
└── tests/                          # Project tests
```

Execution starts in `main.py`. It calls the extraction modules, then performs cleaning, integration, transformation, validation, and finally writes the output files.

## 3. Data Sources

The pipeline uses the following three data sources:

1. **CSV:** `data/raw/students.csv`, which contains basic student information such as `student_id`, `age`, `major`, and `city`.
2. **REST API:** A local mock service at `http://127.0.0.1:8000/students`. It provides fields such as `gpa`, `attendance`, and `status`.
3. **SQLite Database:** `database/students.db`. Student enrollment, course, score, and semester data are extracted from the `enrollments` and `courses` tables.

The three sources are joined using `student_id`.

## 4. ETL Pipeline

### Extract

The extraction stage reads the CSV file, sends a GET request to the API, and runs a SQL query against the SQLite database. Each source checks that data is available before returning it.

### Transform

The transformation stage includes:

- Removing exact duplicate rows.
- Normalizing column names to lowercase and replacing spaces with `_`.
- Removing extra whitespace and normalizing text values.
- Converting numeric columns such as `student_id`, `age`, `gpa`, `attendance`, and `score` to numeric types.
- Filling missing numeric values with the column median.
- Creating `performance_level` based on GPA.
- Creating `attendance_status` based on attendance percentage.

### Validate

The pipeline checks that `student_id` exists and is not missing, and that numeric values are within valid ranges. Invalid records do not stop the pipeline; they are written to the rejected-records file with a reason for rejection.

### Integrate

CSV data is joined with API data using a `left join` on `student_id`. The result is then joined with the database data using the same key. This preserves CSV records even when a matching record is not available in another source.

### Load

Valid records are saved to `data/processed/final_dataset.csv`. Rejected records are saved to `data/rejected/rejected_records.csv`, and execution information is written to `logs/pipeline.log`.

Before saving, the pipeline compares `student_id` values with the existing final dataset to avoid processing the same records again.

## 5. Data Quality

The project applies the following quality rules:

- The `student_id` column must exist.
- `student_id` must not be missing.
- Age must be between 16 and 80 when provided.
- GPA must be between 0 and 4 when provided.
- Attendance must be between 0 and 100 when provided.
- Score must be between 0 and 100 when provided.
- Duplicate rows are counted for metrics and exact duplicates are removed during cleaning.
- Source-level `student_id` errors are reported, including a missing column, missing values, or duplicate IDs.
- Each rejected record includes an `error_reason` field explaining why it was rejected.

## 6. Installation

It is recommended to create a virtual environment first:

```bash
python -m venv .venv
```

On Windows, activate it with:

```bash
.venv\Scripts\activate
```

Install the project requirements:

```bash
pip install -r requirements.txt
```

Create the SQLite database when needed:

```bash
python database/create_database.py
```

## 7. Running

Because the API source is local, start the mock API in a separate terminal:

```bash
python mock_api.py
```

Then run the pipeline in another terminal:

```bash
python main.py
```

Run the test suite with:

```bash
pytest -q
```

## 8. Output

- `data/processed/final_dataset.csv`: The final dataset after integration, cleaning, transformation, and validation.
- `data/rejected/rejected_records.csv`: Records that failed the quality rules, including their `error_reason`.
- `logs/pipeline.log`: Execution logs, errors, and metrics.
- Terminal output: A summary of extracted, integrated, valid, and rejected records, as well as duplicates and missing values.

## Questions and Answers

### 1. Why do we need a Data Pipeline when working with multiple sources?

Each source may use a different format and schema, and may contain missing, duplicated, or invalid values. A data pipeline provides a consistent and repeatable process for extracting, cleaning, integrating, and validating data instead of handling every source manually.

### 2. What is the difference between Raw Data and Processed Data?

**Raw Data** is data as received from the source, before cleaning, normalization, or validation. **Processed Data** has been cleaned, standardized, integrated, and validated, making it ready for analysis or further use.

### 3. What is the difference between Extract, Transform, and Load?

- **Extract:** Read data from the CSV file, API, and database.
- **Transform:** Clean and standardize the data, fill missing values, and create derived columns.
- **Load:** Save the resulting data to the output files or another final storage system.

This project also includes **Validate** and **Integrate** stages to ensure quality and combine the sources before loading.

### 4. What problems did you face while integrating the data?

The main challenges were different schemas across sources, records present in one source but missing from another, duplicates, missing values, and invalid values such as out-of-range GPA or attendance. These issues were handled by normalizing column names and types, using a `left join` on `student_id`, and validating the integrated data.

### 5. How did you handle Missing Values?

Missing numeric values are allowed through validation when they do not violate another rule, and are then filled with the column median during transformation. A missing `student_id` is treated as an error and the record is rejected because this field is required for integration.

### 6. How did you handle Duplicate Records?

Duplicate rows are counted for metrics, and exact duplicate rows are removed during cleaning. Incremental processing also compares `student_id` values with the existing final dataset to avoid adding previously processed records again.

### 7. How did you handle Invalid Records?

Values are checked against logical ranges: age must be 16 to 80, GPA must be 0 to 4, and attendance and score must be 0 to 100. An invalid record is excluded from the final dataset and saved in the rejected-records file with a clear `error_reason`.

### 8. Why should the Extraction layer be separated from the Transformation layer?

Separation makes each layer simpler and easier to test and maintain. The extraction method can be changed, for example from CSV to a database, without rewriting the cleaning and transformation logic. It also allows the same transformations to be reused with different sources.

### 9. Why is Data Validation an essential part of data engineering?

Invalid data leads to unreliable analysis and decisions. Validation detects errors early, prevents unreasonable values from reaching the final dataset, and provides a record explaining why each invalid row was rejected.

### 10. How can the pipeline be developed to run periodically and automatically?

It can be scheduled with Windows Task Scheduler, cron, or a workflow tool such as Apache Airflow. Retry handling, alerts, success and failure monitoring, and last-run tracking can also be added. Incremental processing should be retained to avoid reprocessing old data.

### 11. How can the pipeline handle millions of records?

The pipeline can process data in batches, read and write chunks instead of loading everything into memory, and add indexes on `student_id`. Integration can be moved into a database or distributed engine such as Spark. Staging storage, parallel processing, and persistent checkpoints can also improve scalability.

### 12. What is the difference between Batch Processing and Streaming Processing?

**Batch Processing** processes a group of records at scheduled intervals, such as once every hour or day. It is suitable for files and periodic workloads.
