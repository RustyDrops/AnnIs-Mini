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
        "~reboot - Restart\n"
        "~help - List Commands"
    )

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
                            elif cmd == f'{COMMAND_PREFIX}reboot':
                                machine.reset()
                            elif cmd == f'{COMMAND_PREFIX}help':
                                telegram_bot.send_telegram_msg(get_command_list())
                            continue

                        # AI Brain Processing
                        import agent_core
                        print(f"[POLLER] Processing: {msg_text}")
                        await agent_core.process_message(msg_text)
                        
        except Exception as e:
            consecutive_errors += 1
            print(f"Poller Warning (Error {consecutive_errors}): {e}")
            await asyncio.sleep(min(30, 2 * consecutive_errors))
            
        finally:
            if res: res.close()
            sys_mgmt.idle_cpu()
            gc.collect() 
            
        await asyncio.sleep(2) 
