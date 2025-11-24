"""
Test the API endpoints with the correct model
"""
import asyncio
import os
from dotenv import load_dotenv

# Force reload environment
load_dotenv(override=True)

from app import groq, rag, prompts, utils

async def test_plan():
    """Test plan generation with current Groq model"""
    print("Testing plan generation...")
    print(f"Using model: {os.getenv('GROQ_MODEL')}")
    
    # Get RAG context
    context = rag.retrieve_context(
        age_months=24,
        domain='communication',
        extra_info='struggles with two-word combinations',
        budget=6000
    )
    
    print(f"\nRAG context length: {len(context)} chars")
    print(f"RAG context preview: {context[:200]}...\n")
    
    # Build prompt
    system_prompt = prompts.plan_system_prompt(context)
    user_message = "Create an intervention plan for a 24-month-old child in the communication domain.\n\nAdditional context: struggles with two-word combinations"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    # Call Groq
    try:
        response_text = await groq.chat(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        print("Raw response:")
        print(response_text)
        print("\n" + "="*60)
        
        # Parse JSON
        response_json = utils.extract_or_repair_json(response_text)
        
        print("\n=== INTERVENTION PLAN ===\n")
        print(f"Goals:\n{response_json.get('Goals', 'N/A')}\n")
        print(f"Strategies:\n{response_json.get('Strategies', 'N/A')}\n")
        print(f"Advice for Parents:\n{response_json.get('Advice for Parents', 'N/A')}\n")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_plan())
