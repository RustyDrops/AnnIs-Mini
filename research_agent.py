# research_agent.py
import api_client
import gc

async def perform_research(topic, depth="detailed", thinking_level=None):
    print(f"[SUBAGENT] Researching: {topic} (Depth: {depth}, Thinking: {thinking_level})")
    
    # System instruction for the subagent
    sys_instr = (
        "You are a specialized Research Subagent.\n"
        "TASK: Conduct thorough research using Google Search and synthesize a concise, factual memo.\n"
        "RAM LIMIT: Your output is stored in 520KB RAM. Be extremely concise. Use bullet points.\n"
        "FOCUS: Data accuracy, key dates, and primary sources.\n"
        f"DEPTH: {depth}"
    )
    
    messages = [{"role": "user", "parts": [{"text": f"Please research: {topic}"}]}]
    
    # Use Gemini 2.5 Flash-Lite (Stable) with Grounding
    result = await api_client.call_gemini(
        messages_array=messages,
        model=api_client.MODEL_2_5_LITE,
        grounding=True,
        agent_name="research",
        thinking_level=thinking_level
    )
    
    if result["type"] == "text":
        return f"RESEARCH MEMO:\n{result['text']}"
    else:
        return f"Research failed: {result.get('text', 'Unknown Error')}"
