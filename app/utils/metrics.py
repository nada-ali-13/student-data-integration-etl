import time


class PipelineMetrics:

    def __init__(self):
        self.start_time = time.time()
        self.csv_records = 0
        self.api_records = 0
        self.database_records = 0
        self.integrated_records = 0
        self.valid_records = 0
        self.rejected_records = 0
        self.duplicate_records = 0
        self.missing_values = 0

    def summary(self):
        processing_time = time.time() - self.start_time

        return {
            "CSV Records": self.csv_records,
            "API Records": self.api_records,
            "Database Records": self.database_records,
            "Integrated Records": self.integrated_records,
            "Valid Records": self.valid_records,
            "Rejected Records": self.rejected_records,
            "Duplicate Records": self.duplicate_records,
            "Missing Values": self.missing_values,
            "Processing Time": round(processing_time, 2)
        }