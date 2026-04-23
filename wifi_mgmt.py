# wifi_mgmt.py
import network
import ntptime
import time
import machine
import uasyncio as asyncio
from secrets import WIFI_SSID, WIFI_PASS

async def connect_wifi_and_sync_time(wdt):
    wdt.feed()
    
    import rp2
    try: rp2.country('US')
    except: pass
    
    for _ in range(3):
        await asyncio.sleep(1.0)
        wdt.feed()
    
    wlan = network.WLAN(network.STA_IF)
    for i in range(3):
        try:
            wlan.active(False)
            await asyncio.sleep(1.0)
            wdt.feed()
            wlan.active(True)
            await asyncio.sleep(1.0)
            wdt.feed()
            wlan.connect(WIFI_SSID, WIFI_PASS)
            print("WiFi Radio Active.")
            break
        except OSError:
            if i == 2: raise
            print("WiFi HW Recovery...")
            for _ in range(5):
                await asyncio.sleep(1.0)
                wdt.feed()
                
    while not wlan.isconnected():
        wdt.feed()
        await asyncio.sleep(1)
        
    try:
        ntptime.settime()
        print("RTC Synced.")
        try:
            import api_client
            api_client.resolve_gemini_dns()
        except: pass
    except Exception as e: print(f"Sync Failed: {e}")
    print("WiFi Connected.")
