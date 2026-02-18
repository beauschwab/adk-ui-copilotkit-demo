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

### 10. LangGraph (`langgraph`)
Expert in LangGraph - the production-grade framework for building stateful, multi-actor AI applications. Use when:
- Building agents with LangGraph or LangChain
- Creating stateful agent graphs with ReAct patterns
- Implementing graph construction, state management, cycles and branches
- Working with persistence using checkpointers
- Implementing human-in-the-loop patterns

**Source**: https://github.com/sickn33/antigravity-awesome-skills

### 11. React Flow Fundamentals (`reactflow-fundamentals`)
Build customizable node-based editors and interactive diagrams with React Flow. Use when:
- Building node-based UIs, flow diagrams, or workflow editors
- Creating interactive graphs with React Flow
- Working with nodes, edges, controls, and interactivity
- Building data pipeline visualizations or state machine diagrams

**Source**: https://github.com/thebushidocollective/han

### 12. React Flow Custom Nodes (`reactflow-custom-nodes`)
Create fully customized nodes and edges with React Flow. Use when:
- Creating custom React Flow nodes, edges, and handles
- Building resizable nodes or node toolbars
- Implementing advanced node customization
- Working with custom node components and behaviors

**Source**: https://github.com/thebushidocollective/han

### 13. shadcn/ui Components (`shadcn-ui`)
Complete shadcn/ui component library patterns with accessible React components. Use when:
- Setting up shadcn/ui or installing components
- Building forms with React Hook Form and Zod validation
- Customizing themes with Tailwind CSS
- Implementing UI patterns like buttons, dialogs, dropdowns, tables
- Creating accessible UI components with Radix UI

**Source**: https://github.com/giuseppe-trisciuoglio/developer-kit

### 14. Drag-and-Drop Interfaces (`implementing-drag-drop`)
Implements drag-and-drop and sortable interfaces with React/TypeScript. Use when:
- Building Trello-style kanban boards with draggable cards
- Creating sortable lists with drag handles
- Implementing file upload zones with drag-and-drop
- Building reorderable grids or dashboard widgets
- Creating interactive UIs requiring direct manipulation

**Source**: https://github.com/ancoleman/ai-design-components

## When to use this skill

Use this skill when working on the Knowsee project, which involves:
- Multi-agent orchestration with isolated contexts
- RAG (Retrieval-Augmented Generation) with team-scoped permissions
- Real-time streaming via AG-UI protocol
- Interactive generative UI components
- Google Vertex AI integration (Gemini models, RAG Engine)
- Next.js frontend with CopilotKit
- FastAPI backend with Google ADK
