# Complete Testing Guide

This guide walks you through testing the Multi-Agent Customer Service application from start to finish.

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- OpenAI API key
- AWS credentials with Bedrock access

## Part 1: Backend Setup and Testing

### Step 1: Create Virtual Environment

```bash
cd backend
python -m venv venv
```

### Step 2: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt.

### Step 3: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

**Expected:** Installation completes without errors (may take 2-3 minutes).

### Step 4: Configure Environment

```bash
# Copy example file
cp env.example .env

# Edit .env file with your credentials
# Use notepad, vim, or any text editor
notepad .env  # Windows
# or
nano .env     # macOS/Linux
```

**Required values in .env:**
- `OPENAI_API_KEY=sk-...` (your OpenAI API key)
- `AWS_ACCESS_KEY_ID=...` (your AWS access key)
- `AWS_SECRET_ACCESS_KEY=...` (your AWS secret key)
- `AWS_REGION=us-east-1` (or your preferred region)

### Step 5: Ingest Data

```bash
python ingest_data.py
```

**Expected output:**
```
======================================================================
DOCUMENT INGESTION PIPELINE
======================================================================
Data directory: C:\...\data\mock_documents
ChromaDB directory: C:\...\backend\chroma_db

======================================================================
Processing category: BILLING
======================================================================
Loading billing documents from ...
Loaded 5 documents
Chunking documents...
Created 47 chunks
Generating embeddings and storing in ChromaDB...
✓ Successfully ingested 47 chunks for billing

[Similar output for technical and policy categories]

======================================================================
INGESTION COMPLETE
======================================================================
Total chunks ingested: 123
Collections created: 3

Verifying collections...
  - billing_docs: 47 documents
  - technical_docs: 58 documents
  - policy_docs: 18 documents

✓ Pipeline completed successfully!
```

**If you get errors:**
- OpenAI error: Check your `OPENAI_API_KEY` in `.env`
- File not found: Make sure you're in the `backend/` directory

### Step 6: Test LLM Configuration

```bash
python test_llm_setup.py
```

**Expected output:**
```
Testing LLM Provider Configuration...
======================================================================

1. Environment Variables:
   OPENAI_API_KEY: ✓ Set
   AWS_ACCESS_KEY_ID: ✓ Set
   AWS_SECRET_ACCESS_KEY: ✓ Set
   AWS_REGION: us-east-1

2. LLM Provider Validation:

   OPENAI:
      ✓ Configured successfully

   BEDROCK:
      ✓ Configured successfully

3. ChromaDB Collections:
   ✓ Found 3 collections:
      - billing_docs: 47 documents
      - technical_docs: 58 documents
      - policy_docs: 18 documents

======================================================================
SUMMARY
======================================================================
✓ All LLM providers are configured correctly!

You can now:
  1. Run the data ingestion: python ingest_data.py
  2. Start the API server: python -m app.main
======================================================================
```

**Optional:** Test with a simple query (choose yes when prompted)

**If tests fail:**
- OpenAI: Verify API key is valid
- Bedrock: Verify AWS credentials and region
- ChromaDB: Run `ingest_data.py` first

### Step 7: Test Individual Agents

```bash
python test_agents.py
```

**Expected output:**
```
======================================================================
AGENT TESTING SUITE
======================================================================

======================================================================
TESTING BILLING AGENT (Hybrid RAG/CAG)
======================================================================

Loading billing documents from ...
Loaded 5 documents
...

1. First Query (RAG - Initial Retrieval):
   Query: What are the pricing plans available?
   Strategy: RAG (Initial)
   Response: We offer three comprehensive pricing plans...

2. Second Query (CAG - Using Cache):
   Query: What's included in the Enterprise plan?
   Strategy: CAG (Cached)
   Response: The Enterprise plan is our most comprehensive...

3. Cache Statistics:
   {'cached_sessions': 1, 'agent': 'Billing Support', 'strategy': 'Hybrid RAG/CAG'}

[Similar output for Technical and Policy agents]

======================================================================
TESTING STREAMING RESPONSES
======================================================================

Query: "How do I set up webhooks?"
Streaming response:
----------------------------------------------------------------------
To set up webhooks for your account, follow these steps...
[Response streams word by word]
----------------------------------------------------------------------
✓ Streaming completed successfully

======================================================================
TEST SUMMARY
======================================================================
✓ PASS - Billing Agent
✓ PASS - Technical Agent
✓ PASS - Policy Agent
✓ PASS - Streaming

======================================================================
✓ ALL TESTS PASSED

All three agents are working correctly with their respective strategies:
  - Billing Agent: Hybrid RAG/CAG (caches after first query)
  - Technical Agent: Pure RAG (searches every time)
  - Policy Agent: Pure CAG (all docs in memory)
======================================================================
```

### Step 8: Test Orchestrator

```bash
python test_orchestrator.py
```

**Expected output:**
```
======================================================================
LANGGRAPH ORCHESTRATOR TESTING SUITE
======================================================================

======================================================================
TESTING ROUTING ACCURACY
======================================================================

BILLING Queries:
----------------------------------------------------------------------
✓ Query: "What are your pricing plans?"
  → Routed to: Billing Support
  → Strategy: Hybrid RAG/CAG

✓ Query: "How much does the Enterprise plan cost?"
  → Routed to: Billing Support
  → Strategy: CAG (Cached)

[15 total test queries...]

======================================================================
Routing Accuracy: 14/15 (93.3%)
======================================================================

[Additional tests for full workflow, streaming, and context]

======================================================================
TEST SUMMARY
======================================================================
✓ PASS - Routing Accuracy
✓ PASS - Full Workflow
✓ PASS - Streaming
✓ PASS - Conversation Context

======================================================================
✓ ALL TESTS PASSED

The orchestrator is working correctly:
  - Routes queries to appropriate agents
  - Handles streaming responses
  - Maintains conversation context
  - Uses Bedrock Claude for cost-effective routing
======================================================================
```

### Step 9: Start Backend Server

```bash
python -m app.main
```

**Expected output:**
```
Policy Agent: Loaded 18 policy documents into memory
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**KEEP THIS TERMINAL RUNNING!**

---

## Part 2: API Testing (Optional)

Open a **NEW terminal** (keep backend running in the first one).

### Step 1: Activate Virtual Environment

```bash
cd backend
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux
```

### Step 2: Run API Tests

```bash
python test_api.py
```

**Expected output:**
```
======================================================================
FASTAPI ENDPOINT TESTING SUITE
======================================================================

API URL: http://localhost:8000

======================================================================
TESTING HEALTH CHECK
======================================================================
✓ Status: ok
  OpenAI Configured: True
  AWS Configured: True
  LLM Providers: {'openai': True, 'bedrock': True}

======================================================================
TESTING NON-STREAMING CHAT
======================================================================

Query: "What are your pricing plans?"
✓ Agent: Billing Support
  Strategy: RAG (Initial)
  Processing Time: 2.34s
  Response: We offer three comprehensive pricing plans...

[Additional test queries...]

======================================================================
TESTING STREAMING CHAT
======================================================================

Query: "What features are included in the Professional plan?"

Streaming Response:
----------------------------------------------------------------------
The Professional plan includes...
[Streams in real-time]
----------------------------------------------------------------------
✓ Streaming completed successfully

[Tests for session management and routing endpoint...]

======================================================================
TEST SUMMARY
======================================================================
✓ PASS - Health Check
✓ PASS - Non-Streaming Chat
✓ PASS - Streaming Chat
✓ PASS - Session Management
✓ PASS - Routing Test Endpoint

======================================================================
✓ ALL TESTS PASSED

The API is working correctly!
======================================================================
```

---

## Part 3: Frontend Testing

Open another **NEW terminal** (keep backend running).

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

**Expected:** Installation completes (may take 1-2 minutes on first run).

### Step 2: Configure Environment

```bash
cp env.example .env.local
```

The default value (`NEXT_PUBLIC_API_URL=http://localhost:8000`) should work if your backend is running on port 8000.

### Step 3: Start Frontend

```bash
npm run dev
```

**Expected output:**
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- info Loaded env from C:\...\frontend\.env.local
- event compiled client and server successfully
```

**KEEP THIS TERMINAL RUNNING!**

---

## Part 4: Browser Testing

### Step 1: Open Browser

Navigate to: `http://localhost:3000`

You should see a clean chat interface with:
- Header: "Multi-Agent Customer Service"
- Welcome message with example queries
- Input field at the bottom

### Step 2: Test Billing Agent (Hybrid RAG/CAG)

**First Query:**
- Type: `What are your pricing plans?`
- Press Enter or click Send button
- **Watch:** Response streams word-by-word in real-time
- **Verify:** Gets information about Starter, Professional, and Enterprise plans
- **Note:** This query performs RAG retrieval (slower first time)

**Follow-up Query:**
- Type: `What's included in the Enterprise plan?`
- **Watch:** Response streams (should be slightly faster)
- **Verify:** Details about Enterprise features
- **Note:** This uses cached context from first query (CAG strategy)

### Step 3: Test Technical Agent (Pure RAG)

**Query 1:**
- Type: `How do I reset my password?`
- **Watch:** Streaming response
- **Verify:** Step-by-step password reset instructions
- **Note:** Performs vector search to find relevant docs

**Query 2:**
- Type: `How do I set up webhooks?`
- **Watch:** Streaming response
- **Verify:** Webhook setup instructions
- **Note:** New vector search (Pure RAG - doesn't use cache)

### Step 4: Test Policy Agent (Pure CAG)

**Query 1:**
- Type: `What's your privacy policy?`
- **Watch:** Very fast response (instant)
- **Verify:** Privacy policy details
- **Note:** All docs loaded in memory, no retrieval needed

**Query 2:**
- Type: `Are you GDPR compliant?`
- **Watch:** Instant response
- **Verify:** GDPR compliance information
- **Note:** Still using in-memory docs (Pure CAG)

### Step 5: Test Session Features

**Session Persistence:**
1. Refresh the browser page
2. **Verify:** Conversation history persists
3. Continue conversation from where you left off

**Clear Chat:**
1. Click "Clear Chat" button in header
2. **Verify:** Conversation history clears
3. Start a new conversation

### Step 6: Test Error Handling

**Simulate Error:**
1. Stop the backend server (CTRL+C in backend terminal)
2. Try sending a message in the browser
3. **Verify:** Error message appears with retry button
4. Restart backend (`python -m app.main`)
5. Click "Retry" button
6. **Verify:** Message sends successfully

---

## Success Criteria Checklist

### Backend Tests
- [ ] Virtual environment created and activated
- [ ] Dependencies installed without errors
- [ ] Data ingestion completed (123 chunks total)
- [ ] LLM configuration test passed
- [ ] All 3 agents tested successfully
- [ ] Orchestrator routing accuracy >80%
- [ ] Backend server starts without errors
- [ ] API tests all pass

### Frontend Tests
- [ ] Dependencies installed without errors
- [ ] Frontend starts on port 3000
- [ ] Chat interface loads correctly
- [ ] Streaming responses work smoothly

### Integration Tests
- [ ] Billing agent responds correctly
- [ ] Technical agent responds correctly
- [ ] Policy agent responds correctly
- [ ] Session persistence works
- [ ] Clear chat works
- [ ] Error handling works

---

## Common Issues and Solutions

### Issue: "ModuleNotFoundError"
**Solution:** 
```bash
pip install -r requirements.txt
```

### Issue: "OpenAI API Error"
**Solution:** 
- Check `OPENAI_API_KEY` in `backend/.env`
- Verify key is valid on OpenAI platform

### Issue: "Bedrock Access Denied"
**Solution:**
- Verify AWS credentials in `.env`
- Check IAM permissions for Bedrock access
- Ensure region supports Claude models (us-east-1 recommended)

### Issue: "ChromaDB Collections Not Found"
**Solution:**
```bash
cd backend
python ingest_data.py
```

### Issue: "Port Already in Use"
**Solution:**
- Change port in `backend/.env`: `PORT=8001`
- Update `frontend/.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8001`

### Issue: "Frontend Can't Connect to Backend"
**Solution:**
1. Verify backend is running (`python -m app.main`)
2. Check backend is on port 8000
3. Verify `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
4. Check for CORS errors in browser console

---

## Performance Benchmarks

**Expected Response Times:**
- Billing (first query - RAG): 2-4 seconds
- Billing (cached - CAG): 1-2 seconds
- Technical (RAG): 2-3 seconds
- Policy (CAG): 1-2 seconds (instant retrieval)

**Routing Decision:** <500ms (Bedrock Claude is fast!)

---

## Next Steps

After successful testing:
1. Review `EXAMPLE_QUERIES.md` for more test queries
2. Prepare your demo video showing:
   - Architecture overview
   - Live demonstration of all 3 agents
   - Code walkthrough
3. Push to GitHub
4. Record and upload video

Congratulations! Your multi-agent customer service system is working! 🎉

