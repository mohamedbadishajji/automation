#  OliveSoft RFP & Tender Intelligence Backend

An AI-driven backend API designed to automate the Request for Proposal (RFP) lifecycle. It integrates web scraping, NLP document extraction, agentic prospect research (via n8n), Qdrant vector similarity search (RAG), and human-in-the-loop proposal refinement.

---

##  Tech Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
* **Database:** PostgreSQL with [SQLAlchemy ORM](https://www.sqlalchemy.org/)
* **Vector Database:** [Qdrant](https://qdrant.tech/) (RAG Matching)
* **Automation & Agents:** [n8n](https://n8n.io/) Webhook Workflows
* **Async & Storage:** `aiofiles` for streaming presentation downloads (`.pptx`, `.pdf`)
* **Validation:** Pydantic V2

---

##  Key Features

- ** automated Tender Ingestion:** Idempotent scraping endpoints that prevent duplicate entries using `source_url` hash checks.
- ** NLP Structured Extraction:** Ingests entity-extracted data (skills, budgets, roles, certifications, and compliance requirements) from tender PDFs.
- ** Vector Search & RAG Matching:** Links internal assets (CVs, past project references, tool stacks) stored in Qdrant to incoming RFPs.
- ** Agentic Prospect Research:** Webhook integration with n8n autonomous web agents to extract company revenue, competitors, key partners, and budget ranges.
- ** Proposal Draft Generation & Streaming:** Auto-increments versions ($v1 \rightarrow v2$), computes coverage score matrices, and streams `.pptx` and `.pdf` file downloads.
- ** Human-in-the-Loop Refinement:** Real-time `PATCH` endpoints allowing sales teams to refine generated slides prior to client submission.

---

## 🔄 Tender State Machine

The system manages tenders through a structured status workflow:


[ DETECTED ] ──(Trigger Agent)──> [ RESEARCHING ]
│
(n8n Webhook)
▼
[ GENERATING_PROPOSAL ] ◄───────── [ RESEARCHED ]
│
(n8n Webhook)
▼
[ PROPOSAL_READY ] ──(Human Edit)──> [ DOWNLOAD PPTX/PDF ]
