from pathlib import Path
from datetime import datetime, timezone
import json

BASE_DIR = Path(__file__).resolve().parent
AUDIT_FILE = BASE_DIR / "audit_log.jsonl"


def log_event(event_type, action, details, approved):
    """
    Append a single audit event to audit_log.jsonl.
    Each line is a JSON object (JSONL format).
    """
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "action": action,
        "details": details,
        "approved": approved,
    }

    with AUDIT_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event


def read_audit_log():
    """Return all audit events as a list of dicts."""
    if not AUDIT_FILE.exists():
        return []

    events = []
    with AUDIT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def clear_audit_log():
    """Delete the audit log."""
    if AUDIT_FILE.exists():
        AUDIT_FILE.unlink()