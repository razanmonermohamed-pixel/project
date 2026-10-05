from pathlib import Path

import requests
from bs4 import BeautifulSoup
from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool


URL = "https://example.com"
SNAPSHOT_DIR = Path("../snapshots")
SNAPSHOT_FILE = SNAPSHOT_DIR / "example_com_crewai.txt"


@tool("check_website")
def check_website() -> str:
    """Check the website and compare it with the previous saved snapshot."""

    try:
        response = requests.get(
            URL,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        current_text = soup.get_text(" ", strip=True)

        SNAPSHOT_DIR.mkdir(exist_ok=True)

        if not SNAPSHOT_FILE.exists():

            SNAPSHOT_FILE.write_text(
                current_text,
                encoding="utf-8"
            )

            return (
                "Status: Baseline created. "
                "The first website snapshot has been saved."
            )

        previous_text = SNAPSHOT_FILE.read_text(
            encoding="utf-8"
        )

        if current_text == previous_text:

            return "Status: No changes detected."

        SNAPSHOT_FILE.write_text(
            current_text,
            encoding="utf-8"
        )

        return (
            "Status: Website change detected! "
            "The new snapshot has been saved."
        )

    except requests.RequestException as error:

        return f"Website access failed: {error}"


llm = LLM(
   model="ollama/llama3.1:8b",
    base_url="http://localhost:11434"
)


website_agent = Agent(
    role="Website Monitoring Agent",
    goal="Monitor the university website and report whether a change has occurred.",
    backstory=(
        "You are a website monitoring agent. "
        "Use the website checking tool and report the result clearly."
    ),
    tools=[check_website],
    llm=llm,
    verbose=True
)


monitoring_task = Task(
    description=(
        "Check the website at https://example.com using the "
        "check_website tool. Report whether a baseline was created, "
        "no change was detected, or a website change was detected."
    ),
    expected_output=(
        "A short report containing the website monitoring status."
    ),
    agent=website_agent
)


crew = Crew(
    agents=[website_agent],
    tasks=[monitoring_task],
    process=Process.sequential,
    verbose=True,
    tracing=True
)


if __name__ == "__main__":

    print("SMART WEBSITE MONITORING AGENT - CREWAI")
    print("-" * 50)

    result = crew.kickoff()

    print("\n===== CREWAI RESULT =====")
    print(result)