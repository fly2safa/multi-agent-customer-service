"""
Data Ingestion Pipeline for Multi-Agent Customer Service

This script processes mock documents and creates vector embeddings
for use by the specialized AI agents.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DATA_DIR = Path("../data/mock_documents")
CHROMA_DIR = Path("./chroma_db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Document categories mapped to agent types
CATEGORIES = {
    "billing": {
        "path": "billing",
        "collection": "billing_docs",
        "description": "Billing, pricing, invoices, and payment information"
    },
    "technical": {
        "path": "technical",
        "collection": "technical_docs",
        "description": "Technical support, troubleshooting, and how-to guides"
    },
    "policy": {
        "path": "policy",
        "collection": "policy_docs",
        "description": "Policies, terms of service, privacy, and compliance"
    }
}


class DocumentIngestionPipeline:
    """Pipeline for ingesting documents into ChromaDB"""
    
    def __init__(self, data_dir: Path, chroma_dir: Path):
        """Initialize the ingestion pipeline.
        
        Args:
            data_dir: Path to mock documents directory
            chroma_dir: Path to ChromaDB persistence directory
        """
        self.data_dir = data_dir
        self.chroma_dir = chroma_dir
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=OPENAI_API_KEY
        )
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=str(chroma_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_documents(self, category: str) -> List[Dict]:
        """Load documents for a specific category.
        
        Args:
            category: Document category (billing, technical, policy)
            
        Returns:
            List of document dictionaries with content and metadata
        """
        category_path = self.data_dir / CATEGORIES[category]["path"]
        
        if not category_path.exists():
            print(f"Warning: Category path {category_path} does not exist")
            return []
        
        print(f"\nLoading {category} documents from {category_path}...")
        
        # Load markdown files
        loader = DirectoryLoader(
            str(category_path),
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        
        documents = loader.load()
        print(f"Loaded {len(documents)} documents")
        
        return documents
    
    def chunk_documents(self, documents: List) -> List:
        """Split documents into smaller chunks.
        
        Args:
            documents: List of LangChain documents
            
        Returns:
            List of chunked documents
        """
        print(f"Chunking documents...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks")
        return chunks
    
    def create_collection(self, category: str) -> None:
        """Create or reset a ChromaDB collection for a category.
        
        Args:
            category: Document category
        """
        collection_name = CATEGORIES[category]["collection"]
        
        # Delete existing collection if it exists
        try:
            self.chroma_client.delete_collection(collection_name)
            print(f"Deleted existing collection: {collection_name}")
        except Exception:
            pass
        
        # Create new collection
        collection = self.chroma_client.create_collection(
            name=collection_name,
            metadata={
                "description": CATEGORIES[category]["description"],
                "category": category
            }
        )
        print(f"Created collection: {collection_name}")
        
        return collection
    
    def ingest_category(self, category: str) -> int:
        """Ingest all documents for a category.
        
        Args:
            category: Document category
            
        Returns:
            Number of chunks ingested
        """
        print(f"\n{'='*60}")
        print(f"Processing category: {category.upper()}")
        print(f"{'='*60}")
        
        # Load documents
        documents = self.load_documents(category)
        
        if not documents:
            print(f"No documents found for {category}")
            return 0
        
        # Chunk documents
        chunks = self.chunk_documents(documents)
        
        if not chunks:
            print(f"No chunks created for {category}")
            return 0
        
        # Create collection
        collection = self.create_collection(category)
        
        # Prepare data for ChromaDB
        print(f"Generating embeddings and storing in ChromaDB...")
        
        texts = [chunk.page_content for chunk in chunks]
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            # Extract filename from source path
            source = chunk.metadata.get("source", "unknown")
            filename = Path(source).name
            
            metadatas.append({
                "source": filename,
                "category": category,
                "chunk_index": i
            })
            ids.append(f"{category}_{i}")
        
        # Generate embeddings
        embeddings_list = self.embeddings.embed_documents(texts)
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_end = min(i + batch_size, len(texts))
            
            collection.add(
                embeddings=embeddings_list[i:batch_end],
                documents=texts[i:batch_end],
                metadatas=metadatas[i:batch_end],
                ids=ids[i:batch_end]
            )
            
            print(f"Ingested batch {i//batch_size + 1}: chunks {i} to {batch_end}")
        
        print(f"✓ Successfully ingested {len(chunks)} chunks for {category}")
        return len(chunks)
    
    def run(self) -> None:
        """Run the complete ingestion pipeline."""
        print("\n" + "="*60)
        print("DOCUMENT INGESTION PIPELINE")
        print("="*60)
        print(f"Data directory: {self.data_dir}")
        print(f"ChromaDB directory: {self.chroma_dir}")
        
        # Create ChromaDB directory if it doesn't exist
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        
        total_chunks = 0
        
        # Process each category
        for category in CATEGORIES.keys():
            try:
                chunks = self.ingest_category(category)
                total_chunks += chunks
            except Exception as e:
                print(f"Error processing {category}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Summary
        print(f"\n{'='*60}")
        print("INGESTION COMPLETE")
        print(f"{'='*60}")
        print(f"Total chunks ingested: {total_chunks}")
        print(f"Collections created: {len(CATEGORIES)}")
        
        # Verify collections
        print(f"\nVerifying collections...")
        collections = self.chroma_client.list_collections()
        for collection in collections:
            count = collection.count()
            print(f"  - {collection.name}: {count} documents")
        
        print(f"\n✓ Pipeline completed successfully!")


def main():
    """Main entry point for the ingestion script."""
    
    # Validate API key
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
        sys.exit(1)
    
    # Resolve paths
    script_dir = Path(__file__).parent
    data_dir = (script_dir / DATA_DIR).resolve()
    chroma_dir = (script_dir / CHROMA_DIR).resolve()
    
    # Validate data directory
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print("Please ensure mock documents are in the correct location")
        sys.exit(1)
    
    # Run pipeline
    pipeline = DocumentIngestionPipeline(data_dir, chroma_dir)
    pipeline.run()


if __name__ == "__main__":
    main()

