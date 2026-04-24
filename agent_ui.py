# ui_agent.py
import api_client
import gc

async def design_ui(objective, hardware="Pico 2W OLED 128x64", original_goal="", scratchpad="", thinking_level=None):
    print(f"[SUBAGENT] UI Design: {objective} (Thinking: {thinking_level})")
    
    sys_instr = (
        "You are a specialized UI/UX Architect for embedded systems.\n"
        f"HARDWARE: {hardware}\n"
        "TASK: Design a clean, high-contrast visual layout for small displays.\n"
        "CONSTRAINTS: Minimize pixel crowding. Use standard icons (ASCII or simple descriptions).\n"
        "OUTPUT: Provide the layout coordinates, font sizes, and a brief design rationale."
    )
    
    prompt = f"Original Goal: {original_goal}\nUI Objective: {objective}\nCurrent Scratchpad: {scratchpad}\n\n" \
             "Please design the UI. ALSO, output an updated 'Scratchpad' " \
             "containing ONLY the pertinent design constraints or coordinates needed for future steps."
    messages = [{"role": "user", "parts": [{"text": prompt}]}]
    
    result = await api_client.call_gemini(
        messages_array=messages,
        model=api_client.MODEL_3_1,
        agent_name="ui_ux",
        thinking_level=thinking_level,
        sys_instr=sys_instr
    )
    
    return f"UI DESIGN:\n{result.get('text', 'Failed to design UI.')}", result.get("usage", {})
