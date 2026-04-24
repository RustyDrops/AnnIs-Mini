# summary_agent.py
import api_client
import gc

async def summarize_context(messages_history):
    print("[SUBAGENT] Memory: Compressing History...")
    
    sys_instr = (
        "You are a Memory Architect.\n"
        "TASK: Compress a long chat history into a single, dense Knowledge Item (KI).\n"
        "CONSTRAINTS: Preserve all key facts, hardware states, and user preferences.\n"
        "OUTPUT: A concise summary that will replace the history to save tokens."
    )
    
    # Send history for compression
    messages = [{"role": "user", "parts": [{"text": f"Summarize this conversation: {str(messages_history)}"}]}]
    
    result = await api_client.call_gemini(
        messages_array=messages,
        model=api_client.MODEL_3_0,
        agent_name="memory",
        thinking_level="minimal",
        sys_instr=sys_instr
    )
    
    return result.get('text', 'Summary failed.'), result.get("usage", {})
