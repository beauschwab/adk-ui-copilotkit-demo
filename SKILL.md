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

### 4. Skill Creator (`skill-creator`)
Guide for creating effective skills. Use when:
- Creating new skills that extend agent capabilities
- Updating existing skills with specialized knowledge
- Building custom skills for specific domains or workflows

**Source**: https://github.com/anthropics/skills

### 5. PowerPoint (`pptx`)
Create, edit, and analyze PowerPoint presentations. Use when:
- Creating slide decks, pitch decks, or presentations
- Reading, parsing, or extracting text from .pptx files
- Editing, modifying, or updating existing presentations
- Working with templates, layouts, speaker notes

**Source**: https://github.com/anthropics/skills

### 6. Excel Spreadsheets (`xlsx`)
Create, edit, and analyze Excel spreadsheets. Use when:
- Creating or editing .xlsx, .xlsm, .csv, or .tsv files
- Working with financial models, data analysis, or reporting
- Computing formulas, formatting, charting, or cleaning data
- Converting between tabular file formats

**Source**: https://github.com/anthropics/skills

### 7. Confluence Management (`confluence`)
Manage Confluence documentation with downloads, uploads, conversions, and diagrams. Use when:
- Downloading Confluence pages to Markdown
- Uploading documents to Confluence
- Converting Wiki Markup to/from Markdown
- Creating or updating Confluence pages

**Source**: https://github.com/spillwavesolutions/confluence-skill

### 8. Jira Issues (`jira-issues`)
Create, update, and manage Jira issues from natural language. Use when:
- Logging bugs or creating tickets
- Updating issue status or managing backlog
- Searching Jira issues or adding comments
- Working with Jira workflows

**Source**: https://github.com/skillcreatorai/ai-agent-skills

### 9. Plan Generator (`plan-generator`)
Creates structured plans from requirements with steps, dependencies, and risks. Use when:
- Planning new features or refactoring efforts
- Planning system migrations or architecture changes
- Breaking down complex requirements into actionable steps
- Validating existing plans

**Source**: https://github.com/oimiragieo/agent-studio

## When to use this skill

Use this skill when working on the Knowsee project, which involves:
- Multi-agent orchestration with isolated contexts
- RAG (Retrieval-Augmented Generation) with team-scoped permissions
- Real-time streaming via AG-UI protocol
- Interactive generative UI components
- Google Vertex AI integration (Gemini models, RAG Engine)
- Next.js frontend with CopilotKit
- FastAPI backend with Google ADK
