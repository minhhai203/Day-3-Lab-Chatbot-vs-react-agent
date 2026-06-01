import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.local_provider import LocalProvider

def test_local_phi3():
    load_dotenv()
    model_name = os.getenv("OLLAMA_MODEL", "phi3:latest")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    
    print("--- Testing Local Provider with Ollama ---")
    print(f"Model: {model_name}")
    print(f"Base URL: {base_url}")

    try:
        provider = LocalProvider(model_name=model_name, base_url=base_url)
        
        prompt = "Explain what an AI Agent is in one sentence."
        print(f"\nUser: {prompt}")
        print("Assistant: ", end="", flush=True)
        
        for chunk in provider.stream(prompt):
            print(chunk, end="", flush=True)
        print("\n\n✅ Local Provider is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")

if __name__ == "__main__":
    test_local_phi3()
