import api_client
import ujson

async def scout_api(query, thinking_level="low"):
    """
    Uses Gemini 2.5 Flash-Lite to search for Free Tier APIs using Grounding.
    """
    prompt = [
        {"role": "user", "parts": [{"text": f"Search the web specifically for a 'Free Tier API' that matches this query: {query}. Respond with a JSON object containing keys: api_name, url, is_free."}]}
    ]
    result = await api_client.call_gemini(
        prompt, 
        model=api_client.MODEL_2_5_LITE,
        grounding=True,
        agent_name="api_scout",
        thinking_level=thinking_level
    )
    return result.get("text", "{}")
