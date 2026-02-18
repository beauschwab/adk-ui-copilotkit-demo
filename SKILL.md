---
name: adk-ui-copilotkit-demo
description: Knowsee - Enterprise knowledge assistant built with Google Agent Development Kit (ADK) and CopilotKit. Multi-agent AI with RAG, web search, and data analytics.
---

# Knowsee - ADK UI CopilotKit Demo

This repository demonstrates a production-ready fullstack reference implementation for building AI assistants with Google Agent Development Kit (ADK) and CopilotKit using AG-UI protocol, A2A (Agent-to-Agent) patterns, and Generative UI.

## Installed Agent Skills

This project includes the following specialized agent skills to enhance development:

### 1. Google ADK Python (`google-adk-python`)
Expert guidance on the Google Agent Development Kit (ADK) for Python. Use this skill when working with:
- Building agents, using tools, streaming, callbacks
- Tutorials, deployment, or advanced architecture with Google ADK
- Agent configuration and model integration

**Source**: https://github.com/cnemri/google-genai-skills

### 2. CopilotKit (`copilotkit`)
CopilotKit integration patterns for providers, runtime wiring, hooks, and shared state. Use when:
- Implementing `useCoAgent`, `useCopilotAction`, `useLangGraphInterrupt`
- Building agent-native product UX
- Working with human-in-the-loop (HITL) patterns with LangGraph

**Source**: https://github.com/outlinedriven/odin-codex-plugin

### 3. Frontend Design (`frontend-design`)
Create distinctive, production-grade frontend interfaces with high design quality. Use when:
- Building web components, pages, or applications
- Creating websites, landing pages, dashboards, React components
- Styling/beautifying any web UI with exceptional aesthetics

**Source**: https://github.com/anthropics/skills

## When to use this skill

Use this skill when working on the Knowsee project, which involves:
- Multi-agent orchestration with isolated contexts
- RAG (Retrieval-Augmented Generation) with team-scoped permissions
- Real-time streaming via AG-UI protocol
- Interactive generative UI components
- Google Vertex AI integration (Gemini models, RAG Engine)
- Next.js frontend with CopilotKit
- FastAPI backend with Google ADK

## Note on Confluence and Jira Skills

Confluence and Jira skills were requested but are not currently available in public skill registries. If specific Atlassian integrations are needed, they would need to be implemented as custom skills or tools within the existing agent architecture.
