# audit_agent.py
import api_client
import gc

async def audit_system(thinking_level=None):
    print(f"[SUBAGENT] Auditor: Checking Health & Budget (Thinking: {thinking_level})")
    
    # Gather system state
    budget_data = api_client.get_budget_status()
    import gc
    ram_free = gc.mem_free() // 1024
    
    sys_instr = (
        "You are the System Auditor (Doctor + Accountant).\n"
        "TASK: Analyze hardware health and financial spending. Suggest optimizations.\n"
        "GOAL: Stay within $0.25/day budget and keep RAM stable."
    )
    
    state = f"STATE: RAM {ram_free}KB Free | {budget_data}"
    messages = [{"role": "user", "parts": [{"text": f"Audit this system state: {state}"}]}]
    
    result = await api_client.call_gemini(
        messages_array=messages,
        model=api_client.MODEL_3_1,
        agent_name="auditor",
        thinking_level=thinking_level
    )
    
    return f"SYSTEM AUDIT:\n{result.get('text', 'Audit failed.')}"
