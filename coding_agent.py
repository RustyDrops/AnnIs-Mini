# coding_agent.py
import api_client
import gc

async def perform_coding(task, context="", thinking_level=None):
    print(f"[SUBAGENT] Coding: {task} (Thinking: {thinking_level})")
    
    # System instruction for the coding agent
    sys_instr = (
        "You are a specialized Coding Subagent.\n"
        "TASK: Write clean, efficient MicroPython code for the Raspberry Pi Pico 2W.\n"
        "RAM LIMIT: The system has only 520KB RAM. Write optimized, compact code.\n"
        "CONTEXT: 150MHz, MicroPython 1.24+.\n"
        "OUTPUT: Provide the code solution and a brief explanation. Avoid large external dependencies."
    )
    
    prompt = f"Coding Task: {task}\nAdditional Context: {context}"
    messages = [{"role": "user", "parts": [{"text": prompt}]}]
    
    # Use Gemini 3.1 Flash-Lite for better coding logic
    result = await api_client.call_gemini(
        messages_array=messages,
        model=api_client.MODEL_3_1,
        agent_name="coding",
        thinking_level=thinking_level
    )
    
    if result["type"] == "text":
        return f"CODING SOLUTION:\n{result['text']}"
    else:
        return f"Coding failed: {result.get('text', 'Unknown Error')}"
