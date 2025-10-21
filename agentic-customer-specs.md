# Project Specification: Advanced Customer Service AI
## Project Goals and Objectives

The primary goal of this project is to develop a sophisticated, proof-of-concept customer service application powered by a multi-agent AI system. The application will demonstrate a modern, scalable architecture for handling diverse customer inquiries by routing them to specialized AI agents.

## Key Objectives:

**Build a Multi-Agent System**: Create a hierarchical agent workflow where a central orchestrator intelligently routes user queries to specialized worker agents.  

**Implement Advanced Retrieval**: Showcase different augmented generation strategies (RAG, CAG, and Hybrid) tailored to the specific needs of each specialized agent.

**Leverage a Multi-Provider LLM Strategy**: Integrate and utilize LLMs from both OpenAI and AWS Bedrock, assigning them to roles strategically to optimize for cost and performance.    

**Develop a Full-Stack Application**: Construct a complete, end-to-end application with a modern web interface and a robust backend API.    

**Create a Portfolio-Ready Project**: The final deliverable should be a high-quality project suitable for showcasing advanced AI engineering skills.

## 2. Minimum Viable Product (MVP) Requirements
The MVP will be a fully functional chat application that fulfills the core objectives.

### 2.1. Backend (Python/FastAPI)

**API Server**: A FastAPI application that exposes a primary /chat endpoint for handling user messages.  

**Stateful Agentic Core**: An agentic workflow built with LangGraph that manages the conversation state, including chat history and session-specific context.  

**Orchestrator Agent**: A supervisor agent responsible for analyzing incoming queries and routing them to the appropriate worker agent.   

**Specialized Worker Agents**:
* **Billing Support Agent**: Implements a Hybrid RAG/CAG model to answer questions about pricing and invoices, caching static policy information for the session after an initial RAG query.
* **Technical Support Agent**: Implements a Pure RAG model to answer questions from a dynamic knowledge base of technical documents, bug reports, and forum posts.
* **Policy & Compliance Agent**: Implements a Pure CAG model to provide fast, consistent answers based on static documents like Terms of Service and Privacy Policies.
* **Data Ingestion Pipeline**: A Python script (ingest_data.py) to process mock documents, create vector embeddings, and load them into a persistent ChromaDB database.  

### 2.2. Frontend (Next.js)

**Chat Interface**: A clean, user-friendly chat interface built with Next.js and a modern UI library (e.g., shadcn/ui).    
**Core Functionality**:
* Display of conversation history between the user and the AI.
* A text input field for users to submit messages.
* Real-time, streaming display of the AI's response.

## 3. Technology Stack
The project will be built exclusively with the following technologies:

- Backend Framework: Python with FastAPI    
- AI/LLM Framework: LangChain, specifically using LangGraph for agent orchestration and LangChain Expression Language (LCEL) for building chains.    
- Vector Database: ChromaDB (running locally with persistence).

- Frontend Framework: Next.js with React.    
- LLM Providers:
    - OpenAI: For high-quality response generation (e.g., GPT-5).
    - AWS Bedrock: For fast, cost-effective routing (e.g., Claude 3 Haiku, AWS Nova Lite/Micro).  

## 4 . Development Methodology
The project must be developed following one of two specified AI-assisted coding methodologies. The developer must choose one and adhere to its principles throughout the development process.

### Option 1: Vibe Coding Strategy

- **Description**: A natural language-driven, iterative approach where the developer describes the desired software behavior in plain language prompts, and AI tools generate the code. The developer's role is to act as a "conductor," guiding, shaping, and validating the AI-generated output in a conversational loop. ***NOTE:*** NO MAX MODE! 
- **Link**: https://github.com/snarktank/ai-dev-tasks/tree/main 

### Option 2: BMAD-METHOD

- The **Breakthrough Method for Agile AI-Driven Development (BMAD)** is a structured framework that uses a virtual team of specialized AI agent personas (e.g., Analyst, Product Manager, Architect, Developer) to plan and execute software development. 
- **Link**: https://github.com/bmad-code-org/BMAD-METHOD

## 5. Submission Requirements
To complete the project, the following items must be submitted:

### GitHub Repository:

A public GitHub repository containing the complete, well-documented source code for both the frontend and backend applications.

The repository must include a README.md file with clear instructions on how to set up the environment, install dependencies, and run the application locally.

### Unlisted YouTube Video:

A short (5-10 minute) unlisted YouTube video demonstrating the final application.

The video must include:

- A brief overview of the project's architecture and goals.

- A live demonstration of the chat application, showcasing a query being correctly routed to each of the three specialized agents.

- A walkthrough of the key sections of the source code, explaining the implementation of the LangGraph orchestrator, the different agent retrieval strategies, and the frontend-backend connection.