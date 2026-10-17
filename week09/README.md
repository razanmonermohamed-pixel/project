# Week 9: Human Oversight

## Overview
Adds approval gates, an audit trail, and reversible actions to the Smart Website Monitoring Agent.

## Architecture
Decision -> Approval Gate (human) -> Execute -> Audit Log
                                     -> Optional Undo

## Files
- approval_gate.py
- audit_trail.py
- reversible_action.py
- human_oversight_demo.py

## Demo Modes
1. Human oversight
2. Undo last snapshot
3. Clear audit log

## Audit Log Format (audit_log.jsonl)
```json
{"timestamp": "...", "event": "approval", "action": "save_snapshot", "approved": false}