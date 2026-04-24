# creative_agent.py
import api_client
import gc

async def write_headline(content, style="punchy", original_goal="", scratchpad="", thinking_level=None):
    print(f"[SUBAGENT] Creative: {content[:30]}... (Thinking: {thinking_level})")
    
    sys_instr = (
        "You are a specialized Headline Writer and Creative Voice.\n"
        "TASK: Create engaging, punchy, and professional titles or notifications.\n"
        f"STYLE: {style}\n"
        "LIMIT: Max 15 words per headline."
    )
    
    prompt = f"Original Goal: {original_goal}\nContent: {content}\nCurrent Scratchpad: {scratchpad}\n\n" \
             f"Write a {style} headline. ALSO, output an updated 'Scratchpad' " \
             "containing ONLY the headline or pertinent creative decisions needed for future steps."
    messages = [{"role": "user", "parts": [{"text": prompt}]}]
    
    result = await api_client.call_gemini(
        messages_array=messages,
        model=api_client.MODEL_2_5_LITE,
        agent_name="creative",
        thinking_level=thinking_level,
        sys_instr=sys_instr
    )
    
    return result.get('text', 'Headline generation failed.'), result.get("usage", {})
