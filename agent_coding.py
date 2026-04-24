# agent_coding.py
import api_client
import gc
from schemas import TOOLS_CODING_SCHEMA

async def perform_coding(task, context="", original_goal="", scratchpad="", thinking_level=None):
    print(f"[SUBAGENT] Coding: {task} (Thinking: {thinking_level})")
    
    # System instruction for the coding agent
    sys_instr = (
        "You are a specialized Coding Subagent.\n"
        "TASK: Write clean, efficient MicroPython code for the Raspberry Pi Pico 2W.\n"
        "RAM LIMIT: The system has only 520KB RAM. Write optimized, compact code.\n"
        "CONTEXT: 150MHz, MicroPython 1.24+.\n"
        "OUTPUT: Provide the code solution and a brief explanation. Avoid large external dependencies."
    )
    
    prompt = f"Original Goal: {original_goal}\nCoding Task: {task}\nAdditional Context: {context}\n" \
             f"Current Scratchpad: {scratchpad}\n\n" \
             "Please provide your coding solution. ALSO, output an updated 'Scratchpad' " \
             "summarizing what was built or changed for future steps."
    messages = [{"role": "user", "parts": [{"text": prompt}]}]
    
    # Use Gemini 3.1 Flash-Lite for better coding logic
    result = await api_client.call_gemini(
        messages_array=messages,
        model=api_client.MODEL_3_1,
        tools=TOOLS_CODING_SCHEMA,
        agent_name="coding",
        thinking_level=thinking_level,
        sys_instr=sys_instr
    )
    
    if result["type"] == "text":
        return f"CODING SOLUTION:\n{result['text']}", result.get("usage", {})
    else:
        return f"Coding failed: {result.get('text', 'Unknown Error')}", {}
