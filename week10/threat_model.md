# Threat Model — OWASP Agentic Top 10

## System: Smart Website Monitoring Agent

## Identified Threats

### ASI01: Goal Hijack (Prompt Injection)
**Risk:** High
An attacker can inject instructions into the knowledge base.
The LLM may follow those instructions instead of the user query.
**Attack:** Indirect prompt injection via poisoned document `DOC-12`.
**Mitigation:** Guardrail that scans documents for injection patterns.

### ASI02: Tool Misuse
**Risk:** Medium
The agent could call tools in unintended ways.
**Mitigation:** Approval gates (Week 9) and least-privilege access.

### ASI03: Identity and Privilege Abuse
**Risk:** Low
The agent has no elevated privileges in this demo.
**Mitigation:** No credentials in memory.

### ASI04: Data Exfiltration
**Risk:** High (via ASI01)
Injection could instruct the agent to leak data.
**Mitigation:** Guardrail blocks "send all data" patterns.

### ASI05: Unsafe Autonomy
**Risk:** Medium
The agent should not execute consequential actions autonomously.
**Mitigation:** Human approval gate (Week 9).

### ASI06–ASI10: (Simplified for this demo)
The system does not use autonomous planning loops, code execution,
or external network calls beyond local Ollama. These risks are low.