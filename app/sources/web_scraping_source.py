from bs4 import BeautifulSoup
import requests
import pandas as pd


def scrape_students(web_scraping_url: str) -> pd.DataFrame:
    response = requests.get(
        web_scraping_url,
        timeout=10
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    students = []

    rows = soup.find_all("tr")

    for row in rows:
        cols = row.find_all("td")

        if not cols:
            continue

        student = []

        for col in cols:
            student.append(
                col.get_text(strip=True)
            )

        students.append(student)

    return pd.DataFrame(
        students,
        columns=["student_id", "Major", "Department", "Duration (Years)", "Degree Type"]
    )