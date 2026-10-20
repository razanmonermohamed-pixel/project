from pathlib import Path
from datetime import datetime, timezone
import json

BASE_DIR = Path(__file__).resolve().parent
MEMORY_FILE = BASE_DIR / "memory.json"


def load_memory():
    """Load saved conversation memory from memory.json."""
    if not MEMORY_FILE.exists():
        return []

    try:
        with MEMORY_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_memory(question, answer):
    """Save a question-answer pair into memory.json."""
    memory = load_memory()

    memory.append({
        "question": question,
        "answer": answer,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    with MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(memory, file, ensure_ascii=False, indent=2)

    return memory


def clear_memory():
    """Delete all saved memory."""
    if MEMORY_FILE.exists():
        MEMORY_FILE.unlink()


if __name__ == "__main__":
    print("Memory file path:", MEMORY_FILE)
    print("Saved memories:", len(load_memory()))