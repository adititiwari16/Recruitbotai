import requests
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:latest"):
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
        
    def generate_response(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response using Ollama.
        
        Args:
            prompt (str): The input prompt for the model
            context (Optional[str]): Additional context for the model
            
        Returns:
            Dict[str, Any]: The model's response
        """
        try:
            # Prepare the full prompt with context if provided
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            # Make request to Ollama API
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                }
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse and return the response
            result = response.json()
            
            # Check if we got a valid response
            if not result.get("response"):
                logger.error("Ollama returned empty response")
                return {
                    "error": "Empty response from Ollama",
                    "success": False
                }
                
            return {
                "response": result.get("response", ""),
                "success": True
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with Ollama: {str(e)}")
            return {
                "error": f"Failed to communicate with Ollama: {str(e)}",
                "success": False
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Ollama response: {str(e)}")
            return {
                "error": f"Invalid response from Ollama: {str(e)}",
                "success": False
            }
        except Exception as e:
            logger.error(f"Unexpected error in Ollama client: {str(e)}")
            return {
                "error": f"Unexpected error: {str(e)}",
                "success": False
            }

# Create a singleton instance
ollama_client = OllamaClient()

def get_ollama_client() -> OllamaClient:
    """Get the singleton Ollama client instance."""
    return ollama_client 