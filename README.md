# Multi-Agent Customer Service AI

A sophisticated customer service application powered by a multi-agent AI system. This project demonstrates a modern, scalable architecture for handling diverse customer inquiries by routing them to specialized AI agents.

## Architecture

- **Backend**: FastAPI with LangGraph orchestration
- **AI Agents**: Orchestrator + 3 specialized workers
  - Billing Support (Hybrid RAG/CAG)
  - Technical Support (Pure RAG)
  - Policy & Compliance (Pure CAG)
- **Frontend**: Next.js with shadcn/ui
- **Vector Database**: ChromaDB
- **LLM Providers**: OpenAI GPT-4, AWS Bedrock Claude 3.5

## Features

- 🤖 Multi-agent system with intelligent query routing
- 💬 Real-time streaming chat interface
- 📚 Multiple retrieval strategies (RAG, CAG, Hybrid)
- 🔄 Stateful conversation management
- 🎨 Modern, responsive UI

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- OpenAI API key
- AWS credentials with Bedrock access

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd agent-proj2
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp env.example .env.local
# Edit .env.local if needed
```

### 4. Data Ingestion

```bash
cd backend
python ingest_data.py
```

This will process mock documents and create vector embeddings in ChromaDB.

## Running the Application

### Start Backend Server

```bash
cd backend
python -m app.main
```

The API will be available at `http://localhost:8000`

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:3000`

## Environment Variables

### Backend (.env)

```
OPENAI_API_KEY=your-openai-api-key
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
CHROMA_PERSIST_DIR=./chroma_db
```

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Example Queries

### Billing Agent
- "What's the pricing for the enterprise plan?"
- "How can I view my invoices?"
- "What payment methods do you accept?"

### Technical Support Agent
- "How do I reset my password?"
- "My API authentication is failing"
- "How to integrate the webhook system?"

### Policy & Compliance Agent
- "What's your data retention policy?"
- "Do you comply with GDPR?"
- "What are the terms of service?"

## Project Structure

```
agent-proj2/
├── backend/
│   ├── app/
│   │   ├── agents/          # Specialized AI agents
│   │   ├── graph/           # LangGraph orchestrator
│   │   ├── routes/          # API endpoints
│   │   ├── config.py        # Configuration
│   │   └── main.py          # FastAPI app
│   ├── ingest_data.py       # Data ingestion script
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js app directory
│   ├── components/          # React components
│   ├── lib/                 # Utilities
│   └── hooks/               # Custom hooks
├── data/
│   └── mock_documents/      # Knowledge base documents
└── README.md
```

## Technology Stack

- **Backend**: FastAPI, LangChain, LangGraph, ChromaDB
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui
- **AI/LLM**: OpenAI GPT-4, AWS Bedrock Claude 3.5
- **Database**: ChromaDB (vector database)

## Development

This project follows the Vibe Coding Strategy - a natural language-driven, iterative development approach guided by AI tools.

## License

MIT

## Author

Developed as a proof-of-concept for advanced AI engineering skills demonstration.

