from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://example.com"
SNAPSHOT_DIR = Path("snapshots")
SNAPSHOT_FILE = SNAPSHOT_DIR / "example_com.txt"


def get_website_text(url):
    response = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(" ", strip=True)


def main():
    print("SMART WEBSITE MONITORING AGENT")
    print("-" * 40)
    print("Checking website:", URL)

    try:
        current_text = get_website_text(URL)
        SNAPSHOT_DIR.mkdir(exist_ok=True)

        if not SNAPSHOT_FILE.exists():
            SNAPSHOT_FILE.write_text(
                current_text,
                encoding="utf-8"
            )
            print("Status: Baseline created")
            print("The first website snapshot has been saved.")

        else:
            previous_text = SNAPSHOT_FILE.read_text(
                encoding="utf-8"
            )

            if current_text == previous_text:
                print("Status: No changes detected")

            else:
                print("Status: Website change detected!")
                SNAPSHOT_FILE.write_text(
                    current_text,
                    encoding="utf-8"
                )
                print("The new snapshot has been saved.")

        print("Monitoring completed.")

    except requests.RequestException as error:
        print("Website access failed:", error)


if __name__ == "__main__":
    main()