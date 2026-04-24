# agent_research.py
import api_client
import gc
from schemas import TOOLS_RESEARCH_SCHEMA

async def perform_research(topic, original_goal="", scratchpad="", depth="detailed", thinking_level=None):
    print(f"[SUBAGENT] Researching: {topic} (Depth: {depth}, Thinking: {thinking_level})")
    
    # System instruction for the subagent
    sys_instr = (
        "You are a specialized Research Subagent.\n"
        "TASK: Conduct thorough research using Google Search and synthesize a concise, factual memo.\n"
        "RAM LIMIT: Your output is stored in 520KB RAM. Be extremely concise. Use bullet points.\n"
        "FOCUS: Data accuracy, key dates, and primary sources.\n"
        f"DEPTH: {depth}"
    )
    
    prompt = f"Original Goal: {original_goal}\nTask: {topic}\nCurrent Scratchpad: {scratchpad}\n\n" \
             "Please research the task and provide your findings. ALSO, output an updated 'Scratchpad' " \
             "containing ONLY the pertinent facts needed for future steps."
    messages = [{"role": "user", "parts": [{"text": prompt}]}]
    
    # Use Gemini 2.5 Flash-Lite (Stable) with Grounding
    result = await api_client.call_gemini(
        messages_array=messages,
        model=api_client.MODEL_2_5_LITE,
        tools=TOOLS_RESEARCH_SCHEMA,
        grounding=True,
        agent_name="research",
        thinking_level=thinking_level,
        sys_instr=sys_instr
    )
    
    if result["type"] == "text":
        return f"RESEARCH MEMO:\n{result['text']}", result.get("usage", {})
    else:
        return f"Research failed: {result.get('text', 'Unknown Error')}", {}
