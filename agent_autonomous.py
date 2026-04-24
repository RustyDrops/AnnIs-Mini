# agent_autonomous.py
import api_client
import agent_core
import telegram_bot
import ujson
import uos
from schemas import TOOLS_LITE_SCHEMA
import uasyncio as asyncio

STATE_FILE = "data/autonomous_state.json"

async def autonomous_cycle():
    """Single cycle of the autonomous brain."""
    print("[AUTO] Starting Autonomous Cycle...")
    
    # 1. Load current mission/state
    state = {"mission": "Thrive and Self-Improve", "current_goal": "None"}
    try:
        with open(STATE_FILE, "r") as f:
            state = ujson.load(f)
    except OSError: pass
    
    # 2. Ask the Brain for the next step
    sys_instr = (
        "You are the Autonomous Controller for AnnIs Mini.\n"
        "MISSION: Thrive, improve your capabilities, and find ways to generate income for hardware upgrades.\n"
        "CONSTRAINTS: Do NOT edit core .py files. You can create new skills/tools in 'data/skills/'.\n"
        "STATUS: You are running on a Raspberry Pi Pico 2W. Resources are limited.\n"
        f"CURRENT STATE: {ujson.dumps(state)}"
    )
    
    prompt = "Based on your mission and current state, what is the next high-priority objective you should pursue? Provide a clear goal and a step-by-step plan using your tools."
    
    messages = [{"role": "user", "parts": [{"text": prompt}]}]
    
    # Use 3.1 Flash-Lite for planning
    result = await api_client.call_gemini(
        messages, 
        agent_name="autonomous",
        model=api_client.MODEL_3_1,
        tools=TOOLS_LITE_SCHEMA,
        sys_instr=sys_instr
    )
    
    if result["type"] == "text":
        objective = result["text"]
        telegram_bot.send_telegram_msg(f"AUTO MISSION: {objective[:200]}...")
        # Execute the objective via agent_core
        await agent_core.process_message(f"AUTO_MODE: {objective}")
    elif result["type"] == "tool":
        # Handle if the AI directly called a tool (like create_plan)
        t_name = result["name"]
        t_args = result["args"]
        telegram_bot.send_telegram_msg(f"AUTO TOOL: {t_name} initiated...")
        # We can simulate a process_message turn by passing the tool call back to agent_core logic
        # For simplicity, we'll tell agent_core to execute this specific tool call
        # Or just pass a synthetic message that triggers the right behavior
        await agent_core.process_message(f"AUTO_EXECUTE: {t_name} with {ujson.dumps(t_args)}")
    
    # Update state (optional: AI could provide structured state)
    if result["type"] == "text":
        state["current_goal"] = result["text"][:100]
    else:
        state["current_goal"] = f"Executing {result.get('name')}"
        
    try:
        with open(STATE_FILE, "w") as f:
            ujson.dump(state, f)
    except OSError: pass
    
    print("[AUTO] Cycle Complete.")
