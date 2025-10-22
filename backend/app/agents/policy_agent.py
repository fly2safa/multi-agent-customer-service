"""
Policy & Compliance Agent - Pure CAG Strategy

This agent handles policy, compliance, and legal queries.
Strategy: Loads all policy documents once at initialization and keeps them
in memory for fast, consistent responses without per-query vector searches.
"""

from typing import Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.llm_providers import get_worker_llm
from app.retrievers import load_all_documents


class PolicyAgent:
    """
    Policy & Compliance Agent with Pure CAG strategy.
    
    Loads all policy documents at initialization and maintains them
    in memory for fast, consistent responses.
    """
    
    def __init__(self):
        """Initialize the Policy Agent and load all policy documents."""
        self.agent_name = "Policy & Compliance"
        # Use GPT-4 Turbo for large context (128K tokens) instead of GPT-4 (8K tokens)
        # This is necessary for Pure CAG strategy with all policy docs in context
        self.llm = get_worker_llm(streaming=True, model="gpt-4-turbo-preview")
        
        # Load all policy documents into memory (CAG strategy)
        self._load_policy_context()
        
        # System prompt for policy agent
        self.system_prompt = """You are a knowledgeable Policy & Compliance specialist for our company.
You provide information about:
- Terms of Service
- Privacy Policy
- GDPR compliance and data protection
- Data retention policies
- User rights and responsibilities
- Legal agreements and contracts
- Compliance requirements

Provide accurate, clear information based on our official policies. Use formal but friendly language.
When discussing legal matters, be precise and reference specific policy sections when available.
Always clarify that for specific legal advice, users should consult with a legal professional.

Use the provided policy documentation to answer questions accurately."""
    
    def _load_policy_context(self) -> None:
        """
        Load all policy documents into memory at initialization.
        This is the CAG (Context-Augmented Generation) strategy.
        """
        # Load all documents from policy collection
        docs = load_all_documents("policy_docs")
        
        # Format all documents into a single context string
        context_parts = []
        for doc in docs:
            source = doc.get('metadata', {}).get('source', 'unknown')
            content = doc.get('content', '')
            context_parts.append(
                f"=== {source} ===\n{content}\n"
            )
        
        self.policy_context = "\n".join(context_parts)
        self.total_docs = len(docs)
        
        print(f"Policy Agent: Loaded {self.total_docs} policy documents into memory")
    
    def process_query(
        self,
        query: str,
        session_id: str,
        chat_history: Optional[List] = None
    ) -> Dict:
        """
        Process a policy/compliance query using Pure CAG.
        
        Args:
            query: User's policy question
            session_id: Unique session identifier
            chat_history: Previous conversation messages
            
        Returns:
            Dictionary with response and metadata
        """
        chat_history = chat_history or []
        
        # Use pre-loaded context (Pure CAG - no vector search)
        context = self.policy_context
        
        # Build the prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("system", "Company Policies and Legal Documentation:\n{context}"),
            ("human", "{query}")
        ])
        
        # Create the chain
        chain = prompt_template | self.llm | StrOutputParser()
        
        # Get response
        try:
            response = chain.invoke({
                "context": context,
                "query": query
            })
            
            return {
                "agent": self.agent_name,
                "response": response,
                "strategy": "Pure CAG",
                "documents_in_context": self.total_docs,
                "session_id": session_id,
                "success": True
            }
        
        except Exception as e:
            return {
                "agent": self.agent_name,
                "response": f"I apologize, but I encountered an error processing your policy question. Please try again or contact our compliance team.",
                "strategy": "Pure CAG",
                "documents_in_context": 0,
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
            query: User's policy question
            session_id: Unique session identifier
            chat_history: Previous conversation messages
            
        Yields:
            Response chunks for streaming
        """
        chat_history = chat_history or []
        
        # Use pre-loaded context (Pure CAG)
        context = self.policy_context
        
        # Build prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("system", "Company Policies and Legal Documentation:\n{context}"),
            ("human", "{query}")
        ])
        
        # Create streaming chain
        chain = prompt_template | self.llm
        
        # Stream response
        try:
            async for chunk in chain.astream({
                "context": context,
                "query": query
            }):
                if hasattr(chunk, 'content'):
                    yield chunk.content
                else:
                    yield str(chunk)
        
        except Exception as e:
            yield f"I apologize, but I encountered an error: {str(e)}"
    
    def reload_policy_context(self) -> None:
        """
        Reload policy documents from the database.
        Useful if policies have been updated.
        """
        self._load_policy_context()
    
    def get_agent_info(self) -> Dict:
        """
        Get information about the agent.
        
        Returns:
            Dictionary with agent information
        """
        return {
            "agent": self.agent_name,
            "strategy": "Pure CAG",
            "description": "All policy documents loaded in memory for fast responses",
            "documents_loaded": self.total_docs
        }

