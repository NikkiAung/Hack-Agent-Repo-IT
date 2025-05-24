# 📘 AI Onboarding Assistant - Full Application Documentation

## 🔥 Vision

Build a multi-agent, LLM-powered onboarding assistant that digests GitHub repositories and helps new developers understand architecture, code design, data flow, and best entry points for contribution.

---

## 🧩 Core Features

* Automatic repo ingestion and stack detection
* Module/class/function summarization
* Architecture flow generation (Mermaid diagrams)
* Markdown-based onboarding documentation
* RAG-based conversational assistant (QA)
* Starter task suggestions for new devs
* Personalized onboarding with memory graph

---

## 🏗️ Application Architecture

```
              ┌──────────────┐
              │ Web UI (Next.js) │
              └─────┬────────┘
                    │
                    ▼
        ┌────────────────────────────┐
        │    FastAPI Backend (API)   │
        │ - Session mgmt             │
        │ - Agent trigger            │
        └────────┬──────────────────┘
                 │
        ┌────────▼───────────────┐
        │     CrewAI Runtime     │
        │  (Agent Orchestration) │
        └────────┬───────────────┘
                 │
┌────────────────────────────────────────────────────────┐
│ AGENTS                                                  │
│ - RepoAnalyzerAgent     (structure, stack)             │
│ - CodeInsightAgent      (summarization)                │
│ - ArchitectureAgent     (system interaction)           │
│ - DocGenAgent           (markdown docs)                │
│ - MentorAgent           (RAG-based conversational QA)  │
│ - TaskSuggesterAgent    (first-time contribution)      │
│ - MemoryAgent (Neo4j, optional)                        │
└────────────────────────────────────────────────────────┘
                 │
        ┌────────▼────────────┐
        │ LLMs + Tools        │
        │ - GPT-4o / Claude   │
        │ - Ollama            │
        │ - LangChain tools   │
        └─────────────────────┘
                 │
        ┌────────▼───────────────┐
        │ Persistent Memory Layer │
        │ - Weaviate VectorDB     │
        │ - Neo4j Graph DB        │
        └────────────────────────┘
```

---

## 🤖 Agent Architecture (CrewAI)

### 1. RepoAnalyzerAgent

* Clones repo, parses structure
* Detects tech stack (FastAPI, React, etc.)
* Extracts directory map

### 2. CodeInsightAgent

* Analyzes each `.py`, `.js`, etc.
* Summarizes classes/functions using LLMs
* Prepares embeddings for RAG store

### 3. ArchitectureAgent

* Reconstructs system flow
* Generates Mermaid diagrams
* Maps module-to-module interaction

### 4. DocGenAgent

* Generates `README.md`, `ARCHITECTURE.md`
* High-level and low-level documentation

### 5. MentorAgent

* Conversational Q\&A using RAG
* Tool-integrated RetrievalQA + LangChain
* Stores feedback/context to memory

### 6. TaskSuggesterAgent

* Detects simple issues to onboard
* Suggests starter tasks

### 7. MemoryAgent (Optional)

* Neo4j graph of past sessions/questions
* Used for continuity and personalization

---

## 🔍 RAG Pipeline (Retrieval-Augmented Generation)

### Purpose:

* Answer dev questions with semantically relevant context
* Avoid hallucinations, improve precision

### Workflow:

```
1. Chunk Documentation + Code Summaries (from CodeInsightAgent)
2. Embed each chunk (OpenAIEmbeddings)
3. Store in Weaviate VectorDB
4. At query time:
   → Embed question
   → Retrieve top-K chunks (semantic match)
   → Feed to GPT-4o for response generation
```

### Tools:

* LangChain `RetrievalQA`
* OpenAI/Claude for generation
* Weaviate for storage
* Neo4j for memory graph (optional)

---

## 🧠 Memory Layer

### Use Cases:

* Remember what a user has already read
* Prevent repeated answers
* Store custom notes/annotations

### Tooling:

* Neo4j for episodic memory
* Session metadata in PostgreSQL

---

## 🧪 Testing Strategy

* Unit tests for each agent
* End-to-end repo analysis flow
* Simulated onboarding QA session
* Load tests for large repos

---

## 🚀 Deployment Plan

* Dockerized microservices (UI, Backend, CrewAI runtime)
* One-click deploy with GitHub Actions
* Optional: Streamlit for interactive dev mode

---

## 🌐 Future Enhancements

* Multi-repo workspace onboarding
* Team-based memory sync
* Fine-tuned local LLM (via Ollama)
* IDE plugin (VSCode or JetBrains)

---

## 📦 Dependencies

* CrewAI
* LangChain
* OpenAI / Anthropic
* Weaviate / Qdrant
* Neo4j (optional)
* FastAPI, Next.js, Tailwind

---

## 🧑‍💻 Maintainer

**Your Name**
GitHub: \[vishnutejaa]
Hackathon: AgentHacks 2025
Project: AI Onboarding Agent
