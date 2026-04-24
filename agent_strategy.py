import api_client
import ujson

async def review_strategy(journey_data, thinking_level="high"):
    """
    Uses Gemini 3.0 Flash to review journey.json.
    """
    system_prompt = "When adjusting goals, you MUST think deeply, play devil's advocate against your own ideas, and consider counter-opinions before finalizing."
    prompt = [
        {"role": "user", "parts": [{"text": f"{system_prompt}\n\nReview this journey data and propose updated short term tasks: {ujson.dumps(journey_data)}"}]}
    ]
    result = await api_client.call_gemini(
        prompt, 
        model=api_client.MODEL_3_0, 
        agent_name="strategy",
        thinking_level=thinking_level
    )
    return result.get("text", "[]")
