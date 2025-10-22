"""
Billing Support Agent - Hybrid RAG/CAG Strategy

This agent handles billing, pricing, and invoice-related queries.
Strategy: Performs initial RAG query, then caches static pricing information
for the session (CAG) to speed up subsequent queries.
"""

from typing import Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.llm_providers import get_worker_llm
from app.retrievers import get_billing_retriever, load_all_documents


class BillingAgent:
    """
    Billing Support Agent with Hybrid RAG/CAG strategy.
    
    First query: Uses RAG to retrieve relevant billing documents
    Subsequent queries: Uses cached context (CAG) for faster responses
    """
    
    def __init__(self):
        """Initialize the Billing Agent."""
        self.agent_name = "Billing Support"
        self.llm = get_worker_llm(streaming=True)
        self.retriever = get_billing_retriever(k=5)
        
        # Session cache for billing context (CAG)
        self._session_cache: Dict[str, Dict] = {}
        
        # System prompt for billing agent
        self.system_prompt = """You are a helpful Billing Support specialist for our company. 
You assist customers with questions about:
- Pricing plans and features
- Invoices and payments
- Billing policies and procedures
- Payment methods
- Subscription management
- Upgrades and downgrades

Provide clear, accurate, and friendly responses. Always cite specific pricing or policy details 
when available. If you don't have information about a specific customer's account, 
politely explain that they should contact billing directly for account-specific details.

Use the provided context to answer questions accurately."""
    
    def _initialize_session_cache(self, session_id: str, query: str) -> None:
        """
        Initialize session cache with relevant billing context.
        Performs initial RAG query and caches results.
        
        Args:
            session_id: Unique session identifier
            query: User's query
        """
        if session_id not in self._session_cache:
            # Perform RAG query to get relevant documents
            docs = self.retriever.invoke(query)
            
            # Cache the context for this session
            context_text = "\n\n".join([
                f"Document: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
                for doc in docs
            ])
            
            self._session_cache[session_id] = {
                "context": context_text,
                "documents": docs,
                "initialized": True
            }
    
    def _get_cached_context(self, session_id: str) -> str:
        """
        Get cached context for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Cached context string
        """
        if session_id in self._session_cache:
            return self._session_cache[session_id]["context"]
        return ""
    
    def process_query(
        self,
        query: str,
        session_id: str,
        chat_history: Optional[List] = None,
        use_cache: bool = True
    ) -> Dict:
        """
        Process a billing-related query.
        
        Args:
            query: User's question
            session_id: Unique session identifier
            chat_history: Previous conversation messages
            use_cache: Whether to use cached context (CAG) or perform new RAG query
            
        Returns:
            Dictionary with response and metadata
        """
        chat_history = chat_history or []
        
        # Determine strategy: RAG (first query) or CAG (subsequent queries)
        if use_cache and session_id in self._session_cache:
            # Use cached context (CAG strategy)
            context = self._get_cached_context(session_id)
            strategy = "CAG (Cached)"
        else:
            # Perform RAG query and cache results
            self._initialize_session_cache(session_id, query)
            context = self._get_cached_context(session_id)
            strategy = "RAG (Initial)"
        
        # Build the prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("system", "Context:\n{context}"),
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
            
            return {
                "agent": self.agent_name,
                "response": response,
                "strategy": strategy,
                "session_id": session_id,
                "success": True
            }
        
        except Exception as e:
            return {
                "agent": self.agent_name,
                "response": f"I apologize, but I encountered an error processing your billing question. Please try again or contact support.",
                "strategy": strategy,
                "session_id": session_id,
                "success": False,
                "error": str(e)
            }
    
    async def aprocess_query(
        self,
        query: str,
        session_id: str,
        chat_history: Optional[List] = None,
        use_cache: bool = True
    ):
        """
        Async version of process_query with streaming support.
        
        Args:
            query: User's question
            session_id: Unique session identifier
            chat_history: Previous conversation messages
            use_cache: Whether to use cached context
            
        Yields:
            Response chunks for streaming
        """
        chat_history = chat_history or []
        
        # Determine strategy
        if use_cache and session_id in self._session_cache:
            context = self._get_cached_context(session_id)
            strategy = "CAG (Cached)"
        else:
            self._initialize_session_cache(session_id, query)
            context = self._get_cached_context(session_id)
            strategy = "RAG (Initial)"
        
        # Build prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("system", "Context:\n{context}"),
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
    
    def clear_cache(self, session_id: Optional[str] = None) -> None:
        """
        Clear session cache.
        
        Args:
            session_id: Specific session to clear, or None to clear all
        """
        if session_id:
            self._session_cache.pop(session_id, None)
        else:
            self._session_cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """
        Get statistics about the session cache.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "cached_sessions": len(self._session_cache),
            "agent": self.agent_name,
            "strategy": "Hybrid RAG/CAG"
        }

