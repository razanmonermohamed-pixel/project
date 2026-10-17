from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from approval_gate import request_approval
from audit_trail import log_event, read_audit_log, clear_audit_log
from reversible_action import take_snapshot, undo_last_snapshot


def run_oversight_demo():
    print("=" * 60)
    print("HUMAN OVERSIGHT DEMO")
    print("=" * 60)

    # 1. قرار الـ Agent: حفظ snapshot جديد
    new_content = "Website version: monitored by Smart Agent (test content)."
    action_name = "save_snapshot"
    action_details = f"Save new snapshot from 'demo_source'. Content length: {len(new_content)} chars"

    log_event("decision", action_name, action_details, approved=None)

    # 2. بوابة الموافقة
    approved = request_approval(action_name, action_details)

    # 3. تسجيل القرار
    log_event("approval", action_name, action_details, approved=approved)

    if not approved:
        print("\n[OVERSIGHT] Action was denied by human. Nothing changed.")
        print_audit_log_tail()
        return

    # 4. تنفيذ الإجراء الخطير
    result = take_snapshot(new_content, source="demo_source")
    log_event("execution", action_name, str(result), approved=True)
    print(f"\n[EXECUTED] Snapshot saved at: {result['path']}")

    # 5. عرض خيار التراجع
    print("\n[TIP] You can undo this action later with undo_last_snapshot().")

    print_audit_log_tail()


def print_audit_log_tail(n=5):
    events = read_audit_log()
    print(f"\n--- Last {min(n, len(events))} audit events ---")
    for e in events[-n:]:
        print(f"[{e['timestamp']}] {e['event']:<10} | {e['action']:<15} | approved={e['approved']}")


def run_undo_demo():
    print("\n" + "=" * 60)
    print("UNDO DEMO")
    print("=" * 60)

    result = undo_last_snapshot()
    log_event("undo", "undo_last_snapshot", str(result), approved=None)

    if result["undone"]:
        print(f"[UNDO] Action reversed: {result['action']}")
    else:
        print(f"[UNDO] Nothing to undo: {result.get('reason')}")

    print_audit_log_tail()


if __name__ == "__main__":
    print("Choose mode:")
    print("  1) Human oversight (approve/deny)")
    print("  2) Undo last snapshot")
    print("  3) Clear audit log and exit")

    choice = input("\nEnter choice (1/2/3): ").strip()

    if choice == "1":
        run_oversight_demo()
    elif choice == "2":
        run_undo_demo()
    elif choice == "3":
        clear_audit_log()
        print("Audit log cleared.")
    else:
        print("Invalid choice.")