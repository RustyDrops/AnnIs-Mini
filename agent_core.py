import api_client
import memory
import telegram_bot
import gc
from schemas import TOOLS_SCHEMA
import research_agent
import coding_agent
import ui_agent
import creative_agent
import audit_agent

MAX_RESPONSE_CHARS = 3000

async def process_message(text):
    # Check for automatic summary before adding new message
    if len(memory.get_full_context()) >= 20:
        import summary_agent
        summary = await summary_agent.summarize_context(memory.get_full_context())
        memory.messages = [{"role": "user", "parts": [{"text": f"PREVIOUS CONTEXT SUMMARY:\n{summary}"}]}]
        memory.save_memory()
        telegram_bot.send_telegram_msg("Memory Archiving: Conversation compressed to save tokens.")

    memory.add_message("user", text)
    
    # 1. First Pass (Main Agent)
    print("[BRAIN] Thinking...")
    context = memory.get_full_context()
    result = await api_client.call_gemini(context, tools=TOOLS_SCHEMA)
    
    # 2. Agentic Loop (Delegation Chain)
    max_turns = 10
    turn = 0
    while result["type"] == "tool" and turn < max_turns:
        turn += 1
        
        agent_res = ""
        gc.collect()
        
        if result["name"] == "create_plan":
            steps = result["args"].get("steps", [])
            total_steps = len(steps)
            telegram_bot.send_telegram_msg(f"PLAN: Executing {total_steps} steps...")
            
            for i, step in enumerate(steps):
                agent = step.get("agent")
                task = step.get("task")
                t_level = step.get("thinking_level")
                print(f"[BRAIN] Step {i+1}/{total_steps}: {agent} -> {task}")
                
                step_res = ""
                if agent == "research": step_res = await research_agent.perform_research(task, thinking_level=t_level)
                elif agent == "coding": step_res = await coding_agent.perform_coding(task, thinking_level=t_level)
                elif agent == "ui": step_res = await ui_agent.design_ui(task, thinking_level=t_level)
                elif agent == "creative": step_res = await creative_agent.write_headline(task, thinking_level=t_level)
                elif agent == "audit": step_res = await audit_agent.audit_system(thinking_level=t_level)
                
                if len(step_res) > MAX_RESPONSE_CHARS: step_res = step_res[:MAX_RESPONSE_CHARS] + "..."
                memory.add_message("user", f"SYSTEM (Plan Step {i+1}): {step_res}")
                gc.collect()

        elif result["name"] == "research":
            telegram_bot.send_telegram_msg(f"RESEARCH: {result['args'].get('topic')}...")
            agent_res = await research_agent.perform_research(
                result["args"].get("topic"), 
                thinking_level=result["args"].get("thinking_level")
            )
        elif result["name"] == "code_skill":
            telegram_bot.send_telegram_msg(f"CODING: {result['args'].get('task')}...")
            agent_res = await coding_agent.perform_coding(
                result["args"].get("task"),
                thinking_level=result["args"].get("thinking_level")
            )
        elif result["name"] == "design_ui":
            telegram_bot.send_telegram_msg(f"UI DESIGN: {result['args'].get('objective')}...")
            agent_res = await ui_agent.design_ui(
                result["args"].get("objective"),
                thinking_level=result["args"].get("thinking_level")
            )
        elif result["name"] == "write_headline":
            agent_res = await creative_agent.write_headline(
                result["args"].get("content"),
                style=result["args"].get("style", "punchy")
            )
        elif result["name"] == "audit_system":
            telegram_bot.send_telegram_msg("AUDIT: Checking system health...")
            agent_res = await audit_agent.audit_system(
                thinking_level=result["args"].get("thinking_level")
            )

        if agent_res:
            if len(agent_res) > MAX_RESPONSE_CHARS: agent_res = agent_res[:MAX_RESPONSE_CHARS] + "..."
            memory.add_message("user", f"SYSTEM: {result['name']} Result:\n{agent_res}")

        # Re-think with the new context
        print(f"[BRAIN] Loop Turn {turn}...")
        context = memory.get_full_context()
        result = await api_client.call_gemini(context, tools=TOOLS_SCHEMA)

    # 3. Final Output
    if result["type"] == "text":
        memory.add_message("model", result["text"])
        telegram_bot.send_telegram_msg(result["text"])
    elif result["type"] == "tool":
        msg = f"Chain Limit: I was about to call {result['name']} but hit the turn limit."
        telegram_bot.send_telegram_msg(msg)
    else:
        msg = f"System Error: {result.get('text', 'Unknown failure')}"
        telegram_bot.send_telegram_msg(msg)
    
    gc.collect()
