"""
Retriever Utilities for Multi-Agent System

This module provides retrieval utilities for accessing ChromaDB
collections and implementing different RAG/CAG strategies.
"""

from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from app.config import settings


class RetrieverManager:
    """Manager for document retrievers across different agent types."""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize the retriever manager.
        
        Args:
            persist_directory: Path to ChromaDB persistence directory
        """
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIR
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Cache for retrievers
        self._retrievers = {}
    
    def get_retriever(
        self,
        collection_name: str,
        k: Optional[int] = None
    ):
        """
        Get a retriever for a specific collection.
        
        Args:
            collection_name: Name of the ChromaDB collection
            k: Number of documents to retrieve (defaults to settings.TOP_K_RESULTS)
            
        Returns:
            LangChain retriever instance
        """
        k = k or settings.TOP_K_RESULTS
        cache_key = f"{collection_name}_{k}"
        
        if cache_key not in self._retrievers:
            # Create LangChain Chroma vectorstore
            vectorstore = Chroma(
                client=self.chroma_client,
                collection_name=collection_name,
                embedding_function=self.embeddings
            )
            
            # Create retriever
            self._retrievers[cache_key] = vectorstore.as_retriever(
                search_kwargs={"k": k}
            )
        
        return self._retrievers[cache_key]
    
    def get_billing_retriever(self, k: Optional[int] = None):
        """
        Get retriever for billing documents (Hybrid RAG/CAG strategy).
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            Retriever for billing collection
        """
        return self.get_retriever("billing_docs", k)
    
    def get_technical_retriever(self, k: Optional[int] = None):
        """
        Get retriever for technical documents (Pure RAG strategy).
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            Retriever for technical collection
        """
        return self.get_retriever("technical_docs", k)
    
    def get_policy_retriever(self, k: Optional[int] = None):
        """
        Get retriever for policy documents (Pure CAG strategy).
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            Retriever for policy collection
        """
        return self.get_retriever("policy_docs", k)
    
    def retrieve_documents(
        self,
        collection_name: str,
        query: str,
        k: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            collection_name: Name of the ChromaDB collection
            query: User query
            k: Number of documents to retrieve
            
        Returns:
            List of retrieved documents with metadata
        """
        retriever = self.get_retriever(collection_name, k)
        documents = retriever.get_relevant_documents(query)
        
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source": doc.metadata.get("source", "unknown")
            }
            for doc in documents
        ]
    
    def load_all_documents(self, collection_name: str) -> List[Dict]:
        """
        Load all documents from a collection (for CAG strategy).
        
        Args:
            collection_name: Name of the ChromaDB collection
            
        Returns:
            List of all documents in the collection
        """
        try:
            collection = self.chroma_client.get_collection(collection_name)
            
            # Get all documents
            results = collection.get(
                include=["documents", "metadatas"]
            )
            
            documents = []
            for i, doc in enumerate(results["documents"]):
                documents.append({
                    "content": doc,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {},
                    "source": results["metadatas"][i].get("source", "unknown") if results["metadatas"] else "unknown"
                })
            
            return documents
        
        except Exception as e:
            print(f"Error loading documents from {collection_name}: {e}")
            return []
    
    def get_collection_stats(self, collection_name: str) -> Dict:
        """
        Get statistics about a collection.
        
        Args:
            collection_name: Name of the ChromaDB collection
            
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.chroma_client.get_collection(collection_name)
            count = collection.count()
            
            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata
            }
        except Exception as e:
            return {
                "name": collection_name,
                "error": str(e)
            }
    
    def list_collections(self) -> List[str]:
        """
        List all available collections.
        
        Returns:
            List of collection names
        """
        collections = self.chroma_client.list_collections()
        return [col.name for col in collections]


# Global retriever manager instance
_retriever_manager: Optional[RetrieverManager] = None


def get_retriever_manager() -> RetrieverManager:
    """
    Get the global retriever manager instance (singleton).
    
    Returns:
        RetrieverManager instance
    """
    global _retriever_manager
    
    if _retriever_manager is None:
        _retriever_manager = RetrieverManager()
    
    return _retriever_manager


# Convenience functions
def get_billing_retriever(**kwargs):
    """Get billing documents retriever."""
    return get_retriever_manager().get_billing_retriever(**kwargs)


def get_technical_retriever(**kwargs):
    """Get technical documents retriever."""
    return get_retriever_manager().get_technical_retriever(**kwargs)


def get_policy_retriever(**kwargs):
    """Get policy documents retriever."""
    return get_retriever_manager().get_policy_retriever(**kwargs)


def retrieve_documents(collection_name: str, query: str, **kwargs) -> List[Dict]:
    """Retrieve documents from a collection."""
    return get_retriever_manager().retrieve_documents(collection_name, query, **kwargs)


def load_all_documents(collection_name: str) -> List[Dict]:
    """Load all documents from a collection."""
    return get_retriever_manager().load_all_documents(collection_name)


if __name__ == "__main__":
    """Test retriever configuration when run directly."""
    print("Testing Retriever Configuration...")
    print("=" * 60)
    
    try:
        manager = get_retriever_manager()
        
        # List collections
        collections = manager.list_collections()
        print(f"\nAvailable collections: {collections}")
        
        # Get stats for each collection
        for collection_name in collections:
            stats = manager.get_collection_stats(collection_name)
            print(f"\n{collection_name}:")
            if "error" in stats:
                print(f"  Error: {stats['error']}")
            else:
                print(f"  Documents: {stats['count']}")
                print(f"  Metadata: {stats.get('metadata', {})}")
        
        print("\n" + "=" * 60)
        print("✓ Retriever configuration successful!")
        
    except Exception as e:
        print(f"\n✗ Retriever configuration failed: {e}")
        print("Have you run the ingestion script (ingest_data.py)?")

