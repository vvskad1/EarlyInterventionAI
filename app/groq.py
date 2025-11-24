"""
Async HTTP client for Groq's OpenAI-compatible Chat Completions API.
"""
import os
from typing import List, Dict, Optional, Any
import httpx


class GroqAPIError(Exception):
    """Custom exception for Groq API errors."""
    pass


async def chat(
    messages: List[Dict[str, str]],
    *,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    response_format: Optional[Dict[str, str]] = None,
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
    timeout: float = 60.0
) -> str:
    """
    Call Groq's chat completions API (OpenAI-compatible).
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        model: Model name (defaults to GROQ_MODEL env var or llama3-70b-8192)
        api_key: API key (defaults to GROQ_API_KEY env var)
        response_format: Optional format dict (e.g., {"type": "json_object"})
        temperature: Sampling temperature (0.0 - 2.0)
        max_tokens: Maximum tokens to generate (None = model default)
        timeout: Request timeout in seconds
        
    Returns:
        Generated text content from the model
        
    Raises:
        GroqAPIError: If the API request fails
    """
    # Get configuration from environment if not provided
    if api_key is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise GroqAPIError("GROQ_API_KEY environment variable is required")
    
    if model is None:
        model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    
    # Build request payload
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    
    if response_format is not None:
        payload["response_format"] = response_format
    
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    
    # Groq API endpoint (OpenAI-compatible)
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Make async request
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            # Check for errors
            if response.status_code != 200:
                error_detail = response.text
                raise GroqAPIError(
                    f"Groq API request failed with status {response.status_code}: {error_detail}"
                )
            
            # Parse response
            response_data = response.json()
            
            # Extract content from response
            try:
                content = response_data["choices"][0]["message"]["content"]
                return content
            except (KeyError, IndexError) as e:
                raise GroqAPIError(
                    f"Unexpected response structure from Groq API: {response_data}"
                )
    
    except httpx.TimeoutException:
        raise GroqAPIError(f"Request to Groq API timed out after {timeout} seconds")
    except httpx.RequestError as e:
        raise GroqAPIError(f"Request to Groq API failed: {str(e)}")
    except Exception as e:
        if isinstance(e, GroqAPIError):
            raise
        raise GroqAPIError(f"Unexpected error calling Groq API: {str(e)}")
