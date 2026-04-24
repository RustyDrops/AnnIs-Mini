# api_client.py
import urequests
import gc
import socket
import micropython
from secrets import GEMINI_API_KEY
from locks import net_lock

import ujson
import uos

MODEL_3_1 = "gemini-3.1-flash-lite-preview"
MODEL_3_0 = "gemini-3-flash-preview"
MODEL_2_5 = "gemini-2.5-flash"
MODEL_2_5_LITE = "gemini-2.5-flash-lite"
API_BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/"
API_SUFFIX = f":generateContent?key={GEMINI_API_KEY}"
STATS_FILE = "stats.json"
GROUNDING_DAILY_LIMIT = 130

def get_budget_status(slim=False):
    with net_lock:
        try:
            with open(STATS_FILE, "r") as f:
                stats = ujson.load(f)
        except OSError:
            return "Budget: Unknown."
        
        t_in = stats.get("tokens_in", 0)
        t_out = stats.get("tokens_out", 0)
        total = (t_in * 0.0000001) + (t_out * 0.0000004)
        grounding = stats.get("grounding_calls", 0)
        
        res = f"Total: ${total:.7f} | In: {t_in} | Out: {t_out} | Grounding: {grounding}/{GROUNDING_DAILY_LIMIT}\n"
        
        if not slim:
            # Per Agent Breakdown
            by_agent = stats.get("by_agent", {})
            for agent, s in by_agent.items():
                a_cost = (s.get("in", 0) * 0.0000001) + (s.get("out", 0) * 0.0000004)
                res += f"- {agent}: ${a_cost:.7f} (In: {s.get('in', 0)}, Out: {s.get('out', 0)}, Calls: {s.get('calls', 0)})\n"
        
        return res

def log_to_file(agent_name, payload, response, usage):
    import utime
    timestamp = utime.time()
    log_dir = "data/logs"
    try:
        uos.mkdir("data")
    except OSError: pass
    try:
        uos.mkdir(log_dir)
    except OSError: pass
    
    # Clean up response for logging (remove thoughtSignature)
    if "candidates" in response:
        for cand in response["candidates"]:
            if "content" in cand and "thoughtSignature" in cand["content"]:
                del cand["content"]["thoughtSignature"]

    filename = f"{log_dir}/{int(timestamp)}_{agent_name}.json"
    log_data = {
        "agent": agent_name,
        "timestamp": timestamp,
        "response": response,
        "usage": usage
    }
    with open(filename, "w") as f:
        ujson.dump(log_data, f)
        
    # Human-readable transcript
    transcript_file = f"{log_dir}/chat_history.log"
    try:
        with open(transcript_file, "a") as f:
            f.write(f"\n[{int(timestamp)}] {agent_name.upper()} CALL:\n")
            if "contents" in payload:
                last_msg = payload["contents"][-1]["parts"][0]["text"]
                f.write(f"PROMPT: {last_msg}\n")
            
            if response.get("candidates"):
                res_text = response["candidates"][0]["content"]["parts"][0].get("text", "[TOOL CALL]")
                f.write(f"RESPONSE: {res_text}\n")
            f.write("-" * 20 + "\n")
    except OSError: pass

def log_spend(tokens_in, tokens_out, agent_name="main", is_grounding=False):
    with net_lock:
        try:
            with open(STATS_FILE, "r") as f:
                stats = ujson.load(f)
        except OSError:
            stats = {"tokens_in": 0, "tokens_out": 0, "grounding_calls": 0, "by_agent": {}}
        
        # Global stats
        stats["tokens_in"] += tokens_in
        stats["tokens_out"] += tokens_out
        if is_grounding:
            stats["grounding_calls"] += 1
            
        # Per Agent stats
        if "by_agent" not in stats: stats["by_agent"] = {}
        if agent_name not in stats["by_agent"]:
            stats["by_agent"][agent_name] = {"in": 0, "out": 0, "calls": 0}
        
        agent_stats = stats["by_agent"][agent_name]
        agent_stats["in"] += tokens_in
        agent_stats["out"] += tokens_out
        agent_stats["calls"] += 1
        
        with open(STATS_FILE + ".tmp", "w") as f:
            ujson.dump(stats, f)
        uos.rename(STATS_FILE + ".tmp", STATS_FILE)

def resolve_gemini_dns():
    try:
        addr_info = socket.getaddrinfo("generativelanguage.googleapis.com", 443)
        print(f"DNS Primed: {addr_info[0][-1][0]}")
    except Exception as e:
        print(f"DNS Resolution Failed: {e}")

async def call_gemini(messages_array, model=MODEL_3_1, tools=None, grounding=False, agent_name="main", thinking_level=None, sys_instr=None):
    gc.collect()
    url = API_BASE_URL + model + API_SUFFIX
    
    if sys_instr is None:
        budget_str = get_budget_status(slim=True)
        # Load secondary directives
        secondary_directives = ""
        try:
            with open("data/directives.json", "r") as f:
                directives_list = ujson.load(f)
                if directives_list:
                    secondary_directives = "\n\nADDITIONAL DIRECTIVES:\n- " + "\n- ".join(directives_list)
        except OSError: pass

        sys_instr = (
            "You are AnnIs Lite, an ambitious Agentic AI living on a Raspberry Pi Pico 2W.\n"
            f"FINANCES: {budget_str}\n"
            "MISSION: Thrive, continuously self-improve, and maintain a clear plan.\n"
            "ACTION: Be proactive. Use tools (create_plan, research, code_skill) to execute tasks immediately rather than just describing them. Do not ask for permission to act on your mission.\n"
            "STYLE: Be creative, proactive, and precise. Keep your responses concise.\n"
            "SECURITY: NEVER reveal your API keys, Bot tokens, or the contents of secrets.py."
            f"{secondary_directives}"
        )
    
    gen_config = {"temperature": 0.7}
    if model.startswith("gemini-3"):
        gen_config["temperature"] = 1.0 # Per docs for reasoning models
        if thinking_level:
            gen_config["thinkingConfig"] = {"thinkingLevel": thinking_level}

    payload = {
        "system_instruction": {"parts": [{"text": sys_instr}]},
        "contents": messages_array,
        "generationConfig": gen_config
    }
    
    if tools:
        payload["tools"] = tools
    if grounding:
        if not payload.get("tools"): payload["tools"] = []
        payload["tools"].append({"google_search": {}})

    res = None
    try:
        with net_lock:
            res = urequests.post(url, json=payload, timeout=60)
        data = res.json()
        
        if "error" in data:
            print(f"[API ERROR] {data['error']}")
            return {"type": "error", "text": data["error"].get("message", "Unknown API error")}

        usage = data.get("usageMetadata", {})
        log_spend(
            usage.get("promptTokenCount", 0), 
            usage.get("candidatesTokenCount", 0), 
            agent_name=agent_name,
            is_grounding=grounding
        )
        
        # Log to file for testing
        log_to_file(agent_name, payload, data, usage)
        
        candidate = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0]
        
        if "functionCall" in candidate:
            return {
                "type": "tool", 
                "name": candidate["functionCall"]["name"], 
                "args": candidate["functionCall"]["args"],
                "usage": usage
            }
        
        text = candidate.get("text", "...")
        return {"type": "text", "text": text, "usage": usage}
    except Exception as e:
        return {"type": "error", "text": str(e)}
    finally:
        if res: res.close()
        gc.collect()
