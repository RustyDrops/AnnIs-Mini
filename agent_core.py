import api_client
import memory
import telegram_bot
import gc
from schemas import TOOLS_LITE_SCHEMA
import agent_research
import agent_coding
import agent_ui
import agent_creative
import agent_audit

MAX_RESPONSE_CHARS = 3000

async def process_message(text):
    turn_in = 0
    turn_out = 0
    
    def add_usage(u):
        nonlocal turn_in, turn_out
        turn_in += u.get("promptTokenCount", 0)
        turn_out += u.get("candidatesTokenCount", 0)

    # Check for automatic summary before adding new message
    if len(memory.get_full_context()) >= 12:
        import agent_summary
        summary, s_usage = await agent_summary.summarize_context(memory.get_full_context())
        add_usage(s_usage)
        memory.replace_context([{"role": "user", "parts": [{"text": f"PREVIOUS CONTEXT SUMMARY:\n{summary}"}]}])
        telegram_bot.send_telegram_msg("Memory Archiving: Conversation compressed to save tokens.")

    memory.add_message("user", text)
    
    # 0. Check for Auto-Execute (Synthetically injected tool calls from Autonomous Brain)
    if text.startswith("AUTO_EXECUTE:"):
        import ujson
        try:
            parts = text.split(" with ", 1)
            t_name = parts[0].replace("AUTO_EXECUTE: ", "")
            t_args = ujson.loads(parts[1])
            result = {"type": "tool", "name": t_name, "args": t_args}
            print(f"[BRAIN] Auto-Executing: {t_name}")
        except:
            print("[BRAIN] Failed to parse AUTO_EXECUTE string.")
            return
    else:
        # 1. First Pass (Main Agent)
        print("[BRAIN] Thinking...")
        context = memory.get_full_context()
        result = await api_client.call_gemini(context, tools=TOOLS_LITE_SCHEMA)
        add_usage(result.get("usage", {}))
    
    # 2. Agentic Loop (Delegation Chain)
    max_turns = 10
    turn = 0
    while result["type"] == "tool" and turn < max_turns:
        turn += 1
        
        agent_res = ""
        gc.collect()
        
        if result["name"] == "create_plan":
            steps = result["args"].get("steps", [])
            
            # Capture the goal from the input 'text'
            original_goal = text
            
            # Task Boundary Wipe
            memory.clear_context()
            
            # Seed with BOTH the Goal and the Plan
            seed_msg = f"OBJECTIVE: {original_goal}\n\nPLAN: {str(steps)}"
            memory.add_message("user", f"SYSTEM: Task Boundary Started.\n{seed_msg}")
            
            total_steps = len(steps)
            telegram_bot.send_telegram_msg(f"PLAN: Executing {total_steps} steps...")
            
            plan_scratchpad = ""
            for i, step in enumerate(steps):
                agent = step.get("agent")
                task = step.get("task")
                t_level = step.get("thinking_level")
                print(f"[BRAIN] Step {i+1}/{total_steps}: {agent} -> {task}")
                
                step_res = ""
                u_step = {}
                if agent == "research": step_res, u_step = await agent_research.perform_research(task, original_goal=original_goal, scratchpad=plan_scratchpad, thinking_level=t_level)
                elif agent == "coding": step_res, u_step = await agent_coding.perform_coding(task, original_goal=original_goal, scratchpad=plan_scratchpad, thinking_level=t_level)
                elif agent == "ui": step_res, u_step = await agent_ui.design_ui(task, original_goal=original_goal, scratchpad=plan_scratchpad, thinking_level=t_level)
                elif agent == "creative": step_res, u_step = await agent_creative.write_headline(task, original_goal=original_goal, scratchpad=plan_scratchpad, thinking_level=t_level)
                elif agent == "audit": step_res, u_step = await agent_audit.audit_system(original_goal=original_goal, scratchpad=plan_scratchpad, thinking_level=t_level)
                
                add_usage(u_step)
                if len(step_res) > MAX_RESPONSE_CHARS: step_res = step_res[:MAX_RESPONSE_CHARS] + "..."
                plan_scratchpad = step_res
                gc.collect()
            
            memory.add_message("user", f"SYSTEM: Plan Execution Complete.\nFinal Scratchpad:\n{plan_scratchpad}")

        elif result["name"] == "research":
            telegram_bot.send_telegram_msg(f"RESEARCH: {result['args'].get('topic')}...")
            agent_res, u_res = await agent_research.perform_research(
                result["args"].get("topic"), 
                original_goal=text, scratchpad="",
                thinking_level=result["args"].get("thinking_level")
            )
            add_usage(u_res)
        elif result["name"] == "code_skill":
            telegram_bot.send_telegram_msg(f"CODING: {result['args'].get('task')}...")
            agent_res, u_res = await agent_coding.perform_coding(
                result["args"].get("task"),
                original_goal=text, scratchpad="",
                thinking_level=result["args"].get("thinking_level")
            )
            add_usage(u_res)
        elif result["name"] == "design_ui":
            telegram_bot.send_telegram_msg(f"UI DESIGN: {result['args'].get('objective')}...")
            agent_res, u_res = await agent_ui.design_ui(
                result["args"].get("objective"),
                original_goal=text, scratchpad="",
                thinking_level=result["args"].get("thinking_level")
            )
            add_usage(u_res)
        elif result["name"] == "write_headline":
            agent_res, u_res = await agent_creative.write_headline(
                result["args"].get("content"),
                style=result["args"].get("style", "punchy"),
                original_goal=text, scratchpad=""
            )
            add_usage(u_res)
        elif result["name"] == "audit_system":
            telegram_bot.send_telegram_msg("AUDIT: Checking system health...")
            agent_res, u_res = await agent_audit.audit_system(
                original_goal=text, scratchpad="",
                thinking_level=result["args"].get("thinking_level")
            )
            add_usage(u_res)
        elif result["name"] == "update_directives":
            new_directive = result["args"].get("directive")
            try:
                import ujson
                directives = []
                try:
                    with open("data/directives.json", "r") as f:
                        directives = ujson.load(f)
                except OSError: pass
                
                if new_directive not in directives:
                    directives.append(new_directive)
                    with open("data/directives.json", "w") as f:
                        ujson.dump(directives, f)
                    agent_res = f"Directive saved: {new_directive}"
                else:
                    agent_res = "Directive already exists."
            except Exception as e:
                agent_res = f"Error saving directive: {e}"
        elif result["name"] == "save_skill":
            name = result["args"].get("name")
            code = result["args"].get("code")
            try:
                import uos
                try: uos.mkdir("data/skills")
                except: pass
                filepath = f"data/skills/{name}"
                with open(filepath, "w") as f:
                    f.write(code)
                agent_res = f"Skill saved to {filepath}"
                telegram_bot.send_telegram_msg(f"NEW SKILL: {name} saved.")
            except Exception as e:
                agent_res = f"Error saving skill: {e}"

        if agent_res:
            if len(agent_res) > MAX_RESPONSE_CHARS: agent_res = agent_res[:MAX_RESPONSE_CHARS] + "..."
            memory.add_message("user", f"SYSTEM: {result['name']} Result:\n{agent_res}")

        # Re-think with the new context
        print(f"[BRAIN] Loop Turn {turn}...")
        context = memory.get_full_context()
        result = await api_client.call_gemini(context, tools=TOOLS_LITE_SCHEMA)
        add_usage(result.get("usage", {}))

    # 3. Final Output
    if result["type"] == "text":
        stats = f"\n\n[Turn Tokens: {turn_in} In | {turn_out} Out]"
        final_text = result["text"] + stats
        memory.add_message("model", result["text"]) # Save clean text to memory
        telegram_bot.send_telegram_msg(final_text)
    elif result["type"] == "tool":
        msg = f"Chain Limit: I was about to call {result['name']} but hit the turn limit."
        telegram_bot.send_telegram_msg(msg)
    else:
        msg = f"System Error: {result.get('text', 'Unknown failure')}"
        telegram_bot.send_telegram_msg(msg)
    
    gc.collect()
