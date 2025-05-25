from clean_agentic_rag import CleanAgenticRAG

# Initialize
rag = CleanAgenticRAG()

# Ingest your repository
rag.ingest_repository("/path/to/your/repo")

# Query with automatic prompt expansion
response = rag.query("How does auth work?", agent_type="code_analyst")
print(response)

# Multi-agent analysis
all_responses = rag.multi_agent_query("Explain the architecture")