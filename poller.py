# poller.py
import uasyncio as asyncio
import urequests
import machine
import gc
import telegram_bot
import sys_mgmt
import micropython
from secrets import BOT_TOKEN, CHAT_ID
from locks import net_lock

# PRE-CALCULATED URL
POLL_BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
COMMAND_PREFIX = micropython.const("~")

def get_command_list():
    return (
        "~ping - Health Check\n"
        "~budget - Spent Costs\n"
        "~cnew - Clear Context\n"
        "~c <num> - Keep <num> context turns\n"
        "~creset - Clear Custom Directives\n"
        "~auto <on/off> - Autonomous Mode\n"
        "~reboot - Restart\n"
        "~help - List Commands"
    )

# Global state for autonomous mode
auto_active = False

async def autonomous_task(wdt):
    global auto_active
    import agent_autonomous
    while True:
        if auto_active:
            try:
                await agent_autonomous.autonomous_cycle()
            except Exception as e:
                print(f"[AUTO] Cycle Error: {e}")
            # Wait 30 mins between cycles to save budget
            for _ in range(180): # 180 * 10s = 30 mins
                if not auto_active: break
                await asyncio.sleep(10)
                wdt.feed()
        else:
            await asyncio.sleep(10)
            wdt.feed()

async def telegram_poller(wdt):
    offset = 0
    consecutive_errors = 0
    print("Telegram Poller: Monitoring Signal...")
    
    while True:
        wdt.feed()
        res = None
        try:
            url = f"{POLL_BASE_URL}?offset={offset}&timeout=5"
            with net_lock:
                sys_mgmt.boost_cpu()
                res = urequests.get(url, timeout=10)
                data = res.json()
            
            consecutive_errors = 0 # Reset on success
            
            if data.get('ok') and data.get('result'):
                for update in data['result']:
                    offset = update['update_id'] + 1
                    if 'message' in update and 'text' in update['message']:
                        sender_id = update['message'].get('from', {}).get('id')
                        msg_text = update['message']['text']
                        
                        print(f"[POLLER] Message from {sender_id}: {msg_text}")
                        
                        # Security: Only respond to the authorized CHAT_ID
                        if str(sender_id) != str(CHAT_ID):
                            print(f"[POLLER] Unauthorized sender: {sender_id}")
                            continue 
                        
                        if msg_text.startswith(COMMAND_PREFIX):
                            cmd = msg_text.lower().strip()
                            if cmd == f'{COMMAND_PREFIX}ping':
                                mem_free = gc.mem_free() // 1024
                                telegram_bot.send_telegram_msg(f"Pico OK | {mem_free}KB Free | 150MHz Fixed")
                            elif cmd == f'{COMMAND_PREFIX}budget':
                                import api_client
                                status = api_client.get_budget_status()
                                telegram_bot.send_telegram_msg(status)
                            elif cmd == f'{COMMAND_PREFIX}cnew':
                                import memory
                                memory.clear_context()
                                telegram_bot.send_telegram_msg("Context cleared.")
                            elif cmd.startswith(f'{COMMAND_PREFIX}c '):
                                try:
                                    turns = int(cmd.split(' ')[1])
                                    import memory
                                    memory.slice_context(turns)
                                    telegram_bot.send_telegram_msg(f"Context sliced to {turns} turns.")
                                except ValueError:
                                    telegram_bot.send_telegram_msg("Invalid number.")
                            elif cmd == f'{COMMAND_PREFIX}creset':
                                import uos as os
                                try:
                                    os.remove("data/directives.json")
                                    telegram_bot.send_telegram_msg("Custom directives cleared.")
                                except OSError:
                                    telegram_bot.send_telegram_msg("No custom directives found.")
                            elif cmd.startswith(f'{COMMAND_PREFIX}auto '):
                                global auto_active
                                mode = cmd.split(' ')[1]
                                if mode == 'on':
                                    auto_active = True
                                    telegram_bot.send_telegram_msg("Autonomous Mode: ENGAGED. I will now self-initiate missions.")
                                elif mode == 'off':
                                    auto_active = False
                                    telegram_bot.send_telegram_msg("Autonomous Mode: DISENGAGED.")
                            elif cmd == f'{COMMAND_PREFIX}reboot':
                                machine.reset()
                            elif cmd == f'{COMMAND_PREFIX}help':
                                telegram_bot.send_telegram_msg(get_command_list())
                            continue

                        # AI Brain Processing
                        import agent_core
                        
                        # Ticket Intercept Logic
                        if msg_text.startswith('#Q'):
                            parts = msg_text.split(' ', 1)
                            ticket_id = parts[0]
                            human_answer = parts[1] if len(parts) > 1 else ""
                            filename = ticket_id.replace('#Q', '')
                            filepath = f"data/human_queue/{filename}.json"
                            
                            try:
                                import ujson
                                import uos as os
                                with open(filepath, 'r') as f:
                                    queue_data = ujson.load(f)
                                orig_question = queue_data.get('question', 'Unknown Question')
                                os.remove(filepath)
                                
                                import memory
                                memory.clear_context()
                                
                                msg_text = f"[SYSTEM: Resume Task. Human answered {ticket_id} ('{orig_question}'): {human_answer}]"
                                print(f"[POLLER] Intercepted Ticket: {ticket_id}")
                            except OSError:
                                print(f"[POLLER] Ticket {ticket_id} not found.")

                        print(f"[POLLER] Processing: {msg_text}")
                        try:
                            # 120 second safety timeout for the entire chain
                            await asyncio.wait_for(agent_core.process_message(msg_text), 120)
                        except asyncio.TimeoutError:
                            telegram_bot.send_telegram_msg("System Alert: Processing timed out (120s). Chain aborted to prevent hang.")
                        except Exception as e:
                            telegram_bot.send_telegram_msg(f"Process Error: {e}")
                        
        except Exception as e:
            consecutive_errors += 1
            print(f"Poller Warning (Error {consecutive_errors}): {e}")
            await asyncio.sleep(min(30, 2 * consecutive_errors))
            
        finally:
            if res: res.close()
            sys_mgmt.idle_cpu()
            gc.collect() 
            
        await asyncio.sleep(2) 
