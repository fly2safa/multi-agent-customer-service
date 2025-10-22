"""
LLM Provider Configuration

This module provides factory functions for instantiating LLM clients
from OpenAI and AWS Bedrock.
"""

import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock
import boto3
from app.config import settings


class LLMProviders:
    """Factory class for creating LLM instances."""
    
    _openai_client: Optional[ChatOpenAI] = None
    _bedrock_client: Optional[ChatBedrock] = None
    
    @classmethod
    def get_openai_llm(
        cls,
        model: Optional[str] = None,
        temperature: float = 0.7,
        streaming: bool = True,
        **kwargs
    ) -> ChatOpenAI:
        """
        Get OpenAI LLM instance (GPT-4).
        Used for high-quality response generation by worker agents.
        
        Args:
            model: Model name (defaults to settings.OPENAI_MODEL)
            temperature: Sampling temperature (0-2)
            streaming: Enable streaming responses
            **kwargs: Additional arguments for ChatOpenAI
            
        Returns:
            ChatOpenAI instance configured for worker agents
        """
        model_name = model or settings.OPENAI_MODEL
        
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            streaming=streaming,
            openai_api_key=settings.OPENAI_API_KEY,
            **kwargs
        )
    
    @classmethod
    def get_bedrock_llm(
        cls,
        model: Optional[str] = None,
        temperature: float = 0.3,
        **kwargs
    ) -> ChatBedrock:
        """
        Get AWS Bedrock LLM instance (Claude 3.5 Haiku).
        Used for fast, cost-effective routing by the orchestrator.
        
        Args:
            model: Model ID (defaults to settings.BEDROCK_MODEL)
            temperature: Sampling temperature (0-1 for Claude)
            **kwargs: Additional arguments for ChatBedrock
            
        Returns:
            ChatBedrock instance configured for orchestrator
        """
        model_id = model or settings.BEDROCK_MODEL
        
        # Create boto3 client for Bedrock
        client_kwargs = {
            'service_name': 'bedrock-runtime',
            'region_name': settings.AWS_REGION,
            'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
        }
        
        # Add session token if available (for temporary credentials)
        if settings.AWS_SESSION_TOKEN:
            client_kwargs['aws_session_token'] = settings.AWS_SESSION_TOKEN
        
        bedrock_client = boto3.client(**client_kwargs)
        
        return ChatBedrock(
            client=bedrock_client,
            model_id=model_id,
            model_kwargs={
                "temperature": temperature,
                "max_tokens": 2000,
                **kwargs
            }
        )
    
    @classmethod
    def get_orchestrator_llm(cls) -> ChatBedrock:
        """
        Get LLM specifically configured for the orchestrator.
        Uses Bedrock Claude 3.5 Haiku for fast, cost-effective routing.
        
        Returns:
            BedrockChat instance optimized for routing decisions
        """
        return cls.get_bedrock_llm(
            temperature=0.3,  # Lower temperature for consistent routing
            max_tokens=500    # Shorter responses for routing decisions
        )
    
    @classmethod
    def get_worker_llm(cls, streaming: bool = True, model: Optional[str] = None, **kwargs) -> ChatOpenAI:
        """
        Get LLM specifically configured for worker agents.
        Uses OpenAI GPT-4 for high-quality responses.
        
        Args:
            streaming: Enable streaming responses
            model: Model name (defaults to GPT-4, can use GPT-4 Turbo for larger context)
            **kwargs: Additional arguments passed to ChatOpenAI
            
        Returns:
            ChatOpenAI instance optimized for customer service responses
        """
        return cls.get_openai_llm(
            model=model,
            temperature=0.7,  # Balanced creativity and consistency
            streaming=streaming,
            max_tokens=1500,   # Sufficient for detailed responses
            **kwargs
        )


# Convenience functions for direct access
def get_openai_llm(**kwargs) -> ChatOpenAI:
    """Convenience function to get OpenAI LLM."""
    return LLMProviders.get_openai_llm(**kwargs)


def get_bedrock_llm(**kwargs) -> ChatBedrock:
    """Convenience function to get Bedrock LLM."""
    return LLMProviders.get_bedrock_llm(**kwargs)


def get_orchestrator_llm() -> ChatBedrock:
    """Convenience function to get orchestrator LLM."""
    return LLMProviders.get_orchestrator_llm()


def get_worker_llm(**kwargs) -> ChatOpenAI:
    """Convenience function to get worker LLM."""
    return LLMProviders.get_worker_llm(**kwargs)


# Validation function
def validate_llm_configuration() -> dict:
    """
    Validate that LLM providers are properly configured.
    
    Returns:
        Dictionary with validation results
    """
    results = {
        "openai": {"configured": False, "error": None},
        "bedrock": {"configured": False, "error": None}
    }
    
    # Test OpenAI configuration
    try:
        if not settings.OPENAI_API_KEY:
            results["openai"]["error"] = "API key not set"
        else:
            llm = get_openai_llm(streaming=False)
            # Simple test to verify credentials
            response = llm.invoke("test")
            results["openai"]["configured"] = True
    except Exception as e:
        results["openai"]["error"] = str(e)
    
    # Test Bedrock configuration
    try:
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            results["bedrock"]["error"] = "AWS credentials not set"
        else:
            # Test boto3 client creation
            boto3.client(
                service_name='bedrock-runtime',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            results["bedrock"]["configured"] = True
    except Exception as e:
        results["bedrock"]["error"] = str(e)
    
    return results


if __name__ == "__main__":
    """Test LLM provider configuration when run directly."""
    print("Testing LLM Provider Configuration...")
    print("=" * 60)
    
    results = validate_llm_configuration()
    
    for provider, status in results.items():
        print(f"\n{provider.upper()}:")
        if status["configured"]:
            print(f"  ✓ Configured successfully")
        else:
            print(f"  ✗ Configuration failed")
            if status["error"]:
                print(f"  Error: {status['error']}")
    
    print("\n" + "=" * 60)
    
    if all(r["configured"] for r in results.values()):
        print("✓ All LLM providers configured successfully!")
    else:
        print("✗ Some LLM providers failed configuration")
        print("Please check your environment variables")

