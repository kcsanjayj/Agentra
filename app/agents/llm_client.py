"""
LLM Client for interacting with multiple AI model providers.

This module provides a unified interface for interacting with different
AI model providers (OpenAI, Anthropic, Google Gemini).
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from app.config import settings

logger = logging.getLogger(__name__)

class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self, api_key: str):
        """Initialize the client with API key."""
        self.api_key = api_key
        self.logger = logging.getLogger(f"llm.{self.__class__.__name__.lower()}")
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text based on the prompt."""
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """Get list of available models."""
        pass

class OpenAIClient(BaseLLMClient):
    """OpenAI API client."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
        
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def generate_text(self, prompt: str, model: str = "gpt-4", 
                           max_tokens: int = 4000, temperature: float = 0.7,
                           **kwargs) -> str:
        """Generate text using OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def get_available_models(self) -> List[str]:
        """Get available OpenAI models."""
        return ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]

class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API client."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not installed. Install with: pip install anthropic")
        
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def generate_text(self, prompt: str, model: str = "claude-3-sonnet",
                           max_tokens: int = 4000, temperature: float = 0.7,
                           **kwargs) -> str:
        """Generate text using Anthropic API."""
        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            self.logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    async def get_available_models(self) -> List[str]:
        """Get available Anthropic models."""
        return ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]

class GeminiClient(BaseLLMClient):
    """Google Gemini API client."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI library not installed. Install with: pip install google-generativeai")
        
        genai.configure(api_key=api_key)
    
    async def generate_text(self, prompt: str, model: str = "gemini-pro",
                           max_tokens: int = 4000, temperature: float = 0.7,
                           **kwargs) -> str:
        """Generate text using Google Gemini API."""
        try:
            model_obj = genai.GenerativeModel(model)
            
            # Configure generation parameters
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                **kwargs
            }
            
            response = await asyncio.to_thread(
                model_obj.generate_content,
                prompt,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            raise
    
    async def get_available_models(self) -> List[str]:
        """Get available Gemini models."""
        return ["gemini-pro", "gemini-pro-vision"]

class LLMManager:
    """Unified LLM manager for multiple providers."""
    
    def __init__(self):
        """Initialize the LLM manager."""
        self.clients: Dict[str, BaseLLMClient] = {}
        self.logger = logging.getLogger("llm.manager")
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize all available LLM clients."""
        # Initialize OpenAI client
        if settings.OPENAI_API_KEY:
            try:
                self.clients["openai"] = OpenAIClient(settings.OPENAI_API_KEY)
                self.logger.info("OpenAI client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        
        # Initialize Anthropic client
        if settings.ANTHROPIC_API_KEY:
            try:
                self.clients["anthropic"] = AnthropicClient(settings.ANTHROPIC_API_KEY)
                self.logger.info("Anthropic client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Anthropic client: {str(e)}")
        
        # Initialize Gemini client
        if settings.GEMINI_API_KEY:
            try:
                self.clients["gemini"] = GeminiClient(settings.GEMINI_API_KEY)
                self.logger.info("Gemini client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini client: {str(e)}")
    
    def get_client(self, provider: str) -> Optional[BaseLLMClient]:
        """Get client for specific provider."""
        return self.clients.get(provider)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self.clients.keys())
    
    async def generate_text(self, prompt: str, model: str = None,
                           provider: str = None, **kwargs) -> str:
        """
        Generate text using specified or default provider.
        
        Args:
            prompt: Text generation prompt
            model: Specific model to use (if None, uses provider default)
            provider: Provider to use (if None, tries available providers)
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        # Determine provider
        if provider:
            client = self.get_client(provider)
            if not client:
                raise ValueError(f"Provider '{provider}' not available")
        else:
            # Auto-select provider based on model or use first available
            if model:
                provider = settings.MODEL_PROVIDERS.get(model)
                client = self.get_client(provider) if provider else None
            
            if not client:
                # Use first available client
                if not self.clients:
                    raise ValueError("No LLM providers available")
                client = list(self.clients.values())[0]
        
        # Use default model if not specified
        if not model:
            available_models = await client.get_available_models()
            model = available_models[0]
        
        return await client.generate_text(prompt, model=model, **kwargs)
    
    async def get_all_available_models(self) -> Dict[str, List[str]]:
        """Get all available models from all providers."""
        models = {}
        for provider, client in self.clients.items():
            try:
                models[provider] = await client.get_available_models()
            except Exception as e:
                self.logger.error(f"Failed to get models from {provider}: {str(e)}")
                models[provider] = []
        
        return models
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if a provider is available."""
        return provider in self.clients
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers."""
        return {provider: True for provider in self.clients.keys()}

# Global LLM manager instance
llm_manager = LLMManager()

async def get_llm_response(prompt: str, model: str = None, **kwargs) -> str:
    """
    Convenience function to get LLM response.
    
    Args:
        prompt: The prompt to send to the LLM
        model: Model to use (optional)
        **kwargs: Additional parameters
        
    Returns:
        Generated text response
    """
    return await llm_manager.generate_text(prompt, model=model, **kwargs)
