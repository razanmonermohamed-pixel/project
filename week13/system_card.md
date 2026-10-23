 System Card: Smart Website Monitoring Agent

1. System Purpose
The system is an AI agent designed to monitor website content and answer user questions using Retrieval-Augmented Generation (RAG). It detects changes, establishes baselines, and cites its sources.

 2. System Evolution (The Journey)
- **Week 4 (The Foundation):** Built the core Agentic Loop and ReAct reasoning pattern.
- **Week 5 (Framework):** Explored CrewAI to understand multi-agent orchestration.
- **Week 6 (Knowledge):** Integrated RAG and evaluated retrieval and citations.
- **Week 7 (Planning):** Tested different reasoning strategies (Decompose, Planner+Critic).
- **Week 8 (Agents):** Proved a single agent is more robust than a multi-agent crew for this task.
- **Week 9 & 10 (Safety):** Added human oversight and defended against prompt injection.
- **Week 11 & 12 (Production):** Wired the CI/CD pipeline and deployed the agent as a FastAPI service.

 3. Capabilities
- **Retrieval:** Searches the knowledge base for relevant facts (Achieved 100% hit rate).
- **Generation:** Answers queries using only the retrieved facts.
- **Citation:** Provides exact document IDs (e.g., `[DOC-05]`) for every claim.
- **Refusal (Ungrounded):** Safely outputs "NOT FOUND" when the answer is not in the knowledge base.
- **API Deployment:** Serves responses via a FastAPI endpoint (`/chat`).

 4. Boundaries and Constraints
- **Knowledge Base Scope:** The agent only knows what is inside `website_monitoring.txt`.
- **Input Limit:** Maximum query length is 500 characters (Budget).
- **Timeout Limit:** Maximum processing time is 300 seconds.
- **No External Network Access:** The agent does not browse the internet; it relies solely on the local Ollama LLM and the local knowledge base.

5. Failure Modes and Recovery
- **Prompt Injection Attack:** Mitigated by a regex-based Guardrail. If a malicious document (e.g., `DOC-12`) enters the system, it is blocked before reaching the LLM.
- **LLM Timeout:** Handled by FastAPI's `asyncio.wait_for` timeout (returns 504 Gateway Timeout).
- **Ollama Downtime:** Handled by returning a 500 Internal Server Error. The system is stateless and can be restarted easily.

 6. Evaluation & Monitoring
- **CI/CD Gate:** A test suite runs on every commit (Capability, Safety, Regression). The build fails if any metric drops below 100%.
- **Health Check:** A `/health` endpoint allows external monitors to verify the service is running.