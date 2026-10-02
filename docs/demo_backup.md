# Demo Backup Plan

If the live demo fails due to a network outage (e.g., Groq/Cohere APIs go down) or a Docker crash, follow this checklist:

1. **Local Screenshot Walkthrough**: Navigate to `docs/screenshots/` and show the pre-recorded interactions.
2. **Trace Review**: Open `logs/trace.jsonl` to demonstrate that the RAG pipeline is actively retrieving the correct chunks and passing them to the prompt.
3. **Architecture Presentation**: Fallback to discussing the `project_analysis.md` architecture map and explaining the RAG pipeline phases.
