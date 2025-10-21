"""
Technical Support Agent - Pure RAG Strategy

This agent handles technical support, troubleshooting, and how-to queries.
Strategy: Every query performs a vector similarity search to retrieve
the most relevant technical documents from the knowledge base.
"""

from typing import Dict, List, Optional
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.llm_providers import get_worker_llm
from app.retrievers import get_technical_retriever


class TechnicalAgent:
    """
    Technical Support Agent with Pure RAG strategy.
    
    Every query performs vector similarity search to retrieve
    relevant technical documentation.
    """
    
    def __init__(self):
        """Initialize the Technical Support Agent."""
        self.agent_name = "Technical Support"
        self.llm = get_worker_llm(streaming=True)
        self.retriever = get_technical_retriever(k=5)
        
        # System prompt for technical agent
        self.system_prompt = """You are an expert Technical Support specialist for our company.
You help customers with:
- Account setup and configuration
- Password resets and authentication issues
- API integration and troubleshooting
- Webhook setup and debugging
- Common errors and their solutions
- Feature usage and best practices

Provide clear, step-by-step instructions when appropriate. Include relevant technical details
like error codes, status codes, or configuration parameters. If a solution requires multiple steps,
number them clearly.

When referencing technical documentation, cite the source when available.
If you cannot find a solution in the provided context, suggest contacting our technical
support team directly for personalized assistance.

Use the provided context to answer questions accurately."""
    
    def _retrieve_context(self, query: str) -> tuple[str, List]:
        """
        Retrieve relevant technical documents for the query.
        
        Args:
            query: User's technical question
            
        Returns:
            Tuple of (context_string, list_of_documents)
        """
        # Perform RAG query
        docs = self.retriever.get_relevant_documents(query)
        
        # Format context with source citations
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'unknown')
            context_parts.append(
                f"[Source {i}: {source}]\n{doc.page_content}\n"
            )
        
        context_text = "\n".join(context_parts)
        
        return context_text, docs
    
    def process_query(
        self,
        query: str,
        session_id: str,
        chat_history: Optional[List] = None
    ) -> Dict:
        """
        Process a technical support query using Pure RAG.
        
        Args:
            query: User's technical question
            session_id: Unique session identifier
            chat_history: Previous conversation messages
            
        Returns:
            Dictionary with response and metadata
        """
        chat_history = chat_history or []
        
        # Always perform RAG query (Pure RAG strategy)
        context, docs = self._retrieve_context(query)
        
        # Build the prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("system", "Technical Documentation:\n{context}"),
            ("human", "{query}")
        ])
        
        # Create the chain
        chain = (
            {
                "context": lambda x: context,
                "query": RunnablePassthrough()
            }
            | prompt_template
            | self.llm
            | StrOutputParser()
        )
        
        # Get response
        try:
            response = chain.invoke(query)
            
            # Extract sources
            sources = [doc.metadata.get('source', 'unknown') for doc in docs]
            
            return {
                "agent": self.agent_name,
                "response": response,
                "strategy": "Pure RAG",
                "sources": sources,
                "session_id": session_id,
                "success": True
            }
        
        except Exception as e:
            return {
                "agent": self.agent_name,
                "response": f"I apologize, but I encountered an error processing your technical question. Please try again or contact our technical support team.",
                "strategy": "Pure RAG",
                "session_id": session_id,
                "success": False,
                "error": str(e)
            }
    
    async def aprocess_query(
        self,
        query: str,
        session_id: str,
        chat_history: Optional[List] = None
    ):
        """
        Async version of process_query with streaming support.
        
        Args:
            query: User's technical question
            session_id: Unique session identifier
            chat_history: Previous conversation messages
            
        Yields:
            Response chunks for streaming
        """
        chat_history = chat_history or []
        
        # Perform RAG query
        context, docs = self._retrieve_context(query)
        
        # Build prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("system", "Technical Documentation:\n{context}"),
            ("human", "{query}")
        ])
        
        # Create streaming chain
        chain = (
            {
                "context": lambda x: context,
                "query": RunnablePassthrough()
            }
            | prompt_template
            | self.llm
        )
        
        # Stream response
        try:
            async for chunk in chain.astream(query):
                if hasattr(chunk, 'content'):
                    yield chunk.content
                else:
                    yield str(chunk)
        
        except Exception as e:
            yield f"I apologize, but I encountered an error: {str(e)}"
    
    def get_agent_info(self) -> Dict:
        """
        Get information about the agent.
        
        Returns:
            Dictionary with agent information
        """
        return {
            "agent": self.agent_name,
            "strategy": "Pure RAG",
            "description": "Performs vector similarity search for every query"
        }

