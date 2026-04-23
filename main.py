# main.py
import shim  # PC Compatibility Layer
import micropython
micropython.opt_level(2)

import uasyncio as asyncio
import machine
import gc
import time

import sys_mgmt
import wifi_mgmt
import telegram_bot
import poller
import memory

# Watchdog timer for system-level recovery (8.3 seconds)
wdt = machine.WDT(timeout=8388)

async def start_up():
    print("Pico 2W Telegram Bot: Initializing...")
    
    # 0. Init Memory (Load context)
    memory.init_memory()
    
    # 1. Lock CPU to 150MHz for WiFi stability
    sys_mgmt.lock_system_frequency()
    
    # 2. Connect to WiFi and sync time
    await wifi_mgmt.connect_wifi_and_sync_time(wdt)
    
    # 3. Global GC Tuning
    gc.collect()
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    
    # 4. Notify Telegram
    mem_free = gc.mem_free() // 1024
    boot_msg = (
        "Pico 2W Bot: ONLINE\n"
        f"Speed: 150MHz | RAM: {mem_free}KB Free\n"
        f"Commands:\n{poller.get_command_list()}"
    )
    telegram_bot.send_telegram_msg(boot_msg)
    
    # 5. Start Loop
    print("Initialization Complete.")
    
    if getattr(shim, 'TERMINAL_MODE', False):
        import agent_core
        print("Master Loop Entry: TERMINAL")
        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() in ['exit', 'quit']: break
                await agent_core.process_message(user_input)
            except KeyboardInterrupt: break
            except Exception as e: print(f"Error: {e}")
    else:
        print("Master Loop Entry: TELEGRAM")
        await poller.telegram_poller(wdt)

if __name__ == "__main__":
    try:
        asyncio.run(start_up())
    except Exception as e:
        print(f"CRITICAL SYSTEM CRASH: {e}")
        time.sleep(5)
        machine.reset()
