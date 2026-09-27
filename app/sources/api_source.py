import requests
import pandas as pd


def extract_api(url: str, timeout: int = 5) -> pd.DataFrame:
    try:
        response = requests.get(url, timeout=timeout)

        response.raise_for_status()

        data = response.json()

        if not data:
            raise ValueError("API returned empty response")

        if not isinstance(data, list):
            raise ValueError("API response must be a list")

        return pd.DataFrame(data)

    except requests.exceptions.Timeout as error:
        raise RuntimeError("API request timed out") from error

    except requests.exceptions.ConnectionError as error:
        raise RuntimeError("Could not connect to API") from error

    except requests.exceptions.HTTPError as error:
        raise RuntimeError(f"HTTP error: {error}") from error

    except ValueError as error:
        raise RuntimeError(f"Invalid API response: {error}") from error