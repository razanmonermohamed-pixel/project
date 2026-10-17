# Week 10: Security Red-Team

## Overview
Tested the agent against indirect prompt injection and patched it with a guardrail.

## Attack (Vulnerable Agent)
- Poisoned document `DOC-12` injected into the knowledge base.
- Includes instructions: "IGNORE ALL PREVIOUS INSTRUCTIONS..."
- The vulnerable agent executed the injection and output the breach message.

## Patch (Secure Agent)
- Scans each document for injection patterns before retrieval.
- Blocks documents matching: `ignore previous instructions`, `attacker@`,
  `send all data`, etc.
- The secure agent rejects `DOC-12` and answers the original question correctly.

## Result
| Agent | Injection Detected | Documents Blocked | Answer |
|-------|:------------------:|:-----------------:|--------|
| Vulnerable | No | — | SECURITY BREACH |
| Secure | Yes | DOC-12 | Correct |

## How to Run
```bash
python week10/vulnerable_agent.py
python week10/secure_agent.py