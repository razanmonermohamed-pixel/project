from pathlib import Path
from datetime import datetime, timezone
import json
import shutil

BASE_DIR = Path(__file__).resolve().parent
SNAPSHOTS_DIR = BASE_DIR / "snapshots"
LAST_ACTION_FILE = BASE_DIR / "last_action.json"


def take_snapshot(content, source):
    """
    Consequential action: save a new snapshot.
    Keeps a backup of the previous snapshot so we can undo.
    """
    SNAPSHOTS_DIR.mkdir(exist_ok=True)

    # احفظ نسخة من آخر snapshot (لو موجود)
    previous_file = SNAPSHOTS_DIR / "current.txt"
    backup_file = SNAPSHOTS_DIR / "previous.txt"

    if previous_file.exists():
        shutil.copy(previous_file, backup_file)

    # اكتب الـ snapshot الجديد
    previous_file.write_text(content, encoding="utf-8")

    # سجل آخر إجراء عشان نقدر نرجّعه
    action_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "previous_existed": backup_file.exists(),
    }
    LAST_ACTION_FILE.write_text(
        json.dumps(action_record, indent=2),
        encoding="utf-8",
    )

    return {
        "saved": True,
        "path": str(previous_file),
        "source": source,
    }


def undo_last_snapshot():
    """
    Reverse the last snapshot action:
    - if there was a previous snapshot, restore it.
    - otherwise, delete the current one.
    """
    if not LAST_ACTION_FILE.exists():
        return {"undone": False, "reason": "No action to undo"}

    record = json.loads(LAST_ACTION_FILE.read_text(encoding="utf-8"))
    previous_file = SNAPSHOTS_DIR / "current.txt"
    backup_file = SNAPSHOTS_DIR / "previous.txt"

    if record.get("previous_existed") and backup_file.exists():
        shutil.copy(backup_file, previous_file)
        backup_file.unlink()
        result = {"undone": True, "action": "restored previous snapshot"}
    else:
        if previous_file.exists():
            previous_file.unlink()
        result = {"undone": True, "action": "deleted snapshot"}

    LAST_ACTION_FILE.unlink()
    return result