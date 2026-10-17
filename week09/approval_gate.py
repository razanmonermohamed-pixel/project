import os
import sys


def request_approval(action_name, action_details):
    """
    Ask the user to approve a consequential action.
    Returns True if approved, False otherwise.
    """
    print("\n" + "=" * 60)
    print("APPROVAL REQUIRED")
    print("=" * 60)
    print(f"Action: {action_name}")
    print(f"Details: {action_details}")
    print("=" * 60)

    # لو الكود بيتشغل تلقائي (بدون human input)، نرجع False
    if not sys.stdin.isatty():
        print("[AUTO] No human present - action denied.")
        return False

    try:
        response = input("Do you approve this action? (yes/no): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n[INTERRUPTED] Action denied.")
        return False

    if response in ("yes", "y"):
        print("[APPROVED] Proceeding...")
        return True

    print("[DENIED] Action cancelled.")
    return False