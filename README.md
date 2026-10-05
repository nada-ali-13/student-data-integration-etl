# Student Data Pipeline

## 1. Project Overview

This project processes student data from five sources: CSV, a REST API, a SQLite database, an HTML table, and MongoDB. It cleans, integrates, validates, and saves valid and rejected records as CSV files. It also tracks pipeline metrics and supports incremental processing.

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
2. **REST API:** The local mock service at `http://127.0.0.1:8000/students`, which provides fields such as `gpa`, `attendance`, and `status`.
3. **SQLite Database:** The database configured in `config.json`. Enrollment, course, score, and semester data are extracted from the `enrollments` and `courses` tables.
4. **HTML table:** The majors table in `web_scraping/majors.html`, served locally at the URL configured in `config.json`. It includes `student_id`, major, department, duration, and degree type.
5. **MongoDB:** The `students` collection in the `student_database` database, accessed through the MongoDB URI in `config.json`.

All five sources are integrated with left joins on `student_id`. That field must be present in each source, and its values must use compatible types for the joins.

## 4. ETL Pipeline

### Extract

The extraction stage reads the CSV file, sends a GET request to the API, queries SQLite, downloads and parses the configured HTML table, and reads documents from MongoDB. The API, HTML server, SQLite database, and MongoDB service must be available when the pipeline runs.

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

The CSV data is the left side of the integration. API, SQLite, HTML, and MongoDB data are each added with a `left join` on `student_id`, preserving CSV records when another source has no matching student. Source columns are cleaned before integration so names and key types are consistent.

### Load

Valid records are saved to `data/processed/final_dataset.csv`. Rejected records are saved to `data/rejected/rejected_records.csv`, and execution information is written to `logs/pipeline.log`.

Before processing, the pipeline compares `student_id` values with the existing final dataset and skips records already present. If there are no new records, it reports the metrics and exits without rewriting the output files. The final dataset includes a `source` field; its current value is the constant `CSV+API+DATABASE`.

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

Install the listed project requirements and the packages used by the HTML and MongoDB sources:

```bash
pip install -r requirements.txt
pip install beautifulsoup4 pymongo
```

Create the SQLite database when needed:

```bash
python database/create_database.py
```

Ensure the database file is at the path configured by `paths.database` in `config.json`. Currently, the creation script writes `students.db` in the working directory, while the default configuration points to `database/students.db`; make these paths match before running the pipeline.

MongoDB must be running at the configured URI, and the `student_database.students` collection must contain documents for the MongoDB extraction test to pass.

## 7. Running

Start each local service in its own terminal from the project root. First, start the mock API:

```bash
python mock_api.py
```

Next, serve the project directory so the HTML page is available at the configured port (`5500` by default):

```bash
python -m http.server 5500
```

Keep MongoDB running separately. Once the API and HTML server are available, run the pipeline in another terminal:

```bash
python main.py
```

Run the pipeline tests with:

```bash
python -m pytest -v tests/test_pipeline.py
```

The source extraction and integration tests also require the API, HTML server, SQLite database, and MongoDB collection to be available. The final-dataset test expects `data/processed/final_dataset.csv` to exist and contain records.

## 8. Output

- `data/processed/final_dataset.csv`: The final dataset after integration, cleaning, transformation, and validation.
- `data/rejected/rejected_records.csv`: Records that failed the quality rules, including their `error_reason`.
- `logs/pipeline.log`: Execution logs, errors, and metrics.
- Terminal output: A summary of extracted, integrated, valid, and rejected records, as well as duplicates and missing values.
- The `source` column currently contains the fixed label `CSV+API+DATABASE`.

## Questions and Answers

### 1. Why do we need a Data Pipeline when working with multiple sources?

Each source may use a different format and schema, and may contain missing, duplicated, or invalid values. A data pipeline provides a consistent and repeatable process for extracting, cleaning, integrating, and validating data instead of handling every source manually.

### 2. What is the difference between Raw Data and Processed Data?

**Raw Data** is data as received from the source, before cleaning, normalization, or validation. **Processed Data** has been cleaned, standardized, integrated, and validated, making it ready for analysis or further use.

### 3. What is the difference between Extract, Transform, and Load?

- **Extract:** Read data from the CSV file, API, database, HTML table, and MongoDB.
- **Transform:** Clean and standardize the data, fill missing values, and create derived columns.
- **Load:** Save the resulting data to the output files or another final storage system.

This project also includes **Validate** and **Integrate** stages to ensure quality and combine the sources before loading.

### 4. What problems did you face while integrating the data?

The main challenges were different schemas and key types across sources, records present in one source but missing from another, duplicates, missing values, and invalid values such as out-of-range GPA or attendance. These issues are handled by cleaning and normalizing the source data, joining on `student_id`, and validating the integrated data.

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
