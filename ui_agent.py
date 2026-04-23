# ui_agent.py
import api_client
import gc

async def design_ui(objective, hardware="Pico 2W OLED 128x64", thinking_level=None):
    print(f"[SUBAGENT] UI Design: {objective} (Thinking: {thinking_level})")
    
    sys_instr = (
        "You are a specialized UI/UX Architect for embedded systems.\n"
        f"HARDWARE: {hardware}\n"
        "TASK: Design a clean, high-contrast visual layout for small displays.\n"
        "CONSTRAINTS: Minimize pixel crowding. Use standard icons (ASCII or simple descriptions).\n"
        "OUTPUT: Provide the layout coordinates, font sizes, and a brief design rationale."
    )
    
    messages = [{"role": "user", "parts": [{"text": f"Design UI for: {objective}"}]}]
    
    result = await api_client.call_gemini(
        messages_array=messages,
        model=api_client.MODEL_3_1,
        agent_name="ui_ux",
        thinking_level=thinking_level
    )
    
    return f"UI DESIGN:\n{result.get('text', 'Failed to design UI.')}"
