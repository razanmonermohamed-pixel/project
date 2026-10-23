# Week 12: Applied Agents & Deployment (AgentOps)

## Overview
Converted the local agent into a production-ready web service using FastAPI and Uvicorn.

## Features
- **FastAPI Service**: Exposes `/health` and `/chat` endpoints.
- **Health Check**: `/health` returns server status for monitoring.
- **Budgets**: Limits input query length to 500 chars.
- **Timeouts**: Kills requests that take longer than 300 seconds.
- **Security**: Integrates the Week 10 guardrail to block prompt injection.

## Architecture
Client -> FastAPI (/chat) -> Secure Agent -> Ollama -> Response

## How to Run
1. Install dependencies:
```bash
pip install fastapi uvicorn