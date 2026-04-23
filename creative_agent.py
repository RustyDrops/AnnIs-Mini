# creative_agent.py
import api_client
import gc

async def write_headline(content, style="punchy", thinking_level=None):
    print(f"[SUBAGENT] Creative: {content[:30]}... (Thinking: {thinking_level})")
    
    sys_instr = (
        "You are a specialized Headline Writer and Creative Voice.\n"
        "TASK: Create engaging, punchy, and professional titles or notifications.\n"
        f"STYLE: {style}\n"
        "LIMIT: Max 15 words per headline."
    )
    
    messages = [{"role": "user", "parts": [{"text": f"Write a {style} headline for: {content}"}]}]
    
    result = await api_client.call_gemini(
        messages_array=messages,
        model=api_client.MODEL_2_5_LITE,
        agent_name="creative",
        thinking_level=thinking_level
    )
    
    return result.get('text', 'Headline generation failed.')
