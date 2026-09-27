import logging
from pathlib import Path


def setup_logger(log_file: str):
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        force=True
    )

    return logging.getLogger("pipeline")