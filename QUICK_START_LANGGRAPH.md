# Quick Start: Testing the LangGraph Backend

## Prerequisites

Make sure you have completed the main setup:
- PostgreSQL running (`make db-up`)
- Environment files configured
- Dependencies installed

## Step 1: Start Both Backends

Open three terminal windows:

### Terminal 1: ADK Backend (Port 8000)
```bash
cd sagent
uv run uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Terminal 2: LangGraph Backend (Port 8001)
```bash
cd sagent_langgraph
uv run uvicorn sagent_langgraph.main:app --reload --port 8001
```

You should see:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
[create_graph] Building Knowsee LangGraph agent
[create_graph] PostgreSQL checkpointer configured
[create_graph] Knowsee graph compiled successfully
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Terminal 3: Frontend (Port 3000)
```bash
cd web
npm run dev
```

You should see:
```
  ▲ Next.js 15.1.3
  - Local:        http://localhost:3000

 ✓ Starting...
 ✓ Ready in 2.1s
```

## Step 2: Test Both Backends Work

### Test ADK Backend (Default)
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","agent":"knowsee_agent"}
```

### Test LangGraph Backend
```bash
curl http://localhost:8001/health
# Should return: {"status":"healthy","backend":"langgraph","agent":"knowsee_agent"}
```

## Step 3: Access the Web App

1. Open http://localhost:3000 in your browser
2. Sign up or log in
3. You should see the chat interface

## Step 4: Switch to LangGraph Backend

1. Click on your profile icon (top right)
2. Select "Settings" from the dropdown
3. Click on the "Developer" tab (icon: `</>`)
4. You'll see two backend options:
   - **Google ADK (Default)** - Currently active (green "Active" badge)
   - **LangGraph** - Experimental (yellow "Experimental" badge)
5. Click on the **LangGraph** option
6. Click "Save Changes" button (bottom right)
7. Refresh the page (F5 or Cmd+R)

## Step 5: Verify Backend Switch

### Check Browser Console
Open browser DevTools (F12) and look for console logs:
```
[CopilotKit:backend] switched to: langgraph
[CopilotKit:route] routing to langgraph backend: http://localhost:8001
```

### Send a Test Message
1. Type a simple message like "Hello!"
2. Check the terminal running LangGraph backend
3. You should see log messages like:
```
[run_agent] user=test@example.com, thread=xxx, msgs=1
[root_agent] Processing user message
```

### Check Network Tab
1. Open DevTools → Network tab
2. Send another message
3. Find the request to `/api/copilotkit`
4. Check Request Headers - you should see:
```
x-agent-backend: langgraph
x-user-id: your-email@example.com
```

## Step 6: Switch Back to ADK

1. Go back to Settings → Developer
2. Select **Google ADK (Default)**
3. Click "Save Changes"
4. Refresh the page
5. Verify in console: `[CopilotKit:route] routing to adk backend: http://localhost:8000`

## Troubleshooting

### Backend Not Starting

**Error**: `DATABASE_URL environment variable is required`
**Fix**: Make sure PostgreSQL is running (`make db-up`) and `.env.development` has correct DATABASE_URL

**Error**: `Module not found: langgraph`
**Fix**: Install dependencies: `cd sagent_langgraph && uv sync`

### Requests Not Routing

**Issue**: Messages go to wrong backend
**Check**:
1. LocalStorage has correct value: Open DevTools → Application → Local Storage → `agent-backend`
2. Headers are being sent: Network tab → Request Headers
3. Route.ts is reading header: Check server logs

**Fix**: Clear localStorage and try again:
```javascript
localStorage.removeItem('agent-backend')
```

### Port Conflicts

**Error**: `Address already in use`
**Fix**: Change ports in commands:
```bash
# ADK on different port
uv run uvicorn main:app --reload --port 8002

# Update web/.env.development
AGENT_URL=http://localhost:8002
```

## Testing Specific Features

### Web Search
1. Switch to desired backend
2. Send: "What's the weather in Paris?"
3. Both backends should respond with search results

### Team Knowledge (RAG)
1. Ensure you have RAG corpora configured
2. Send: "Search our internal documents for X"
3. Both backends should query Vertex AI RAG

### Data Analytics
1. Ensure BigQuery is configured
2. Send: "List available datasets"
3. Both backends should return dataset list

## Performance Comparison

Send the same query to both backends and compare:

**ADK Backend**:
- Response time: ~2-3 seconds (typical)
- Extended thinking: Native support
- Tool delegation: AgentTool pattern

**LangGraph Backend**:
- Response time: ~2-4 seconds (typical)
- Extended thinking: Simulated
- Tool delegation: StateGraph routing

## Next Steps

- Try more complex queries with both backends
- Compare response quality
- Test file uploads
- Monitor resource usage
- Report any issues you find

## Need Help?

- Check logs in all three terminals
- Look for errors in browser console
- Review `sagent_langgraph/README.md` for detailed docs
- Check `IMPLEMENTATION_SUMMARY.md` for architecture details
