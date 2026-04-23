# telegram_bot.py
import urequests
import machine
import gc
from secrets import BOT_TOKEN, CHAT_ID
from locks import net_lock

# PRE-CALCULATED URL
TX_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_telegram_msg(text):
    """Robust outbound sender with leak prevention."""
    import shim
    if getattr(shim, 'TERMINAL_MODE', False):
        print(f"\n[BOT]: {text}\n")
        return

    gc.collect()
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    
    res = None
    try:
        import sys_mgmt
        sys_mgmt.boost_cpu()
        
        # Pico 2W Watchdog feed
        machine.WDT(timeout=8388).feed()
        with net_lock:
            res = urequests.post(TX_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
        machine.WDT(timeout=8388).feed()
        
    except Exception as e:
        print(f"Telegram Tx Error: {e}")
        
    finally:
        if res: res.close()
        try:
            import sys_mgmt
            sys_mgmt.idle_cpu()
        except: pass
        gc.collect()
