# shim.py
"""Compatibility layer to run MicroPython code on a standard PC."""
import sys
import os
import json
import time
import asyncio

# --- MOCK MICROPYTHON MODULES ---

class MockPin:
    IN = 1
    OUT = 2
    PULL_UP = 1
    def __init__(self, *args, **kwargs): pass
    def irq(self, *args, **kwargs): pass
    def value(self): return 0

class MockWDT:
    def __init__(self, *args, **kwargs): pass
    def feed(self): pass

class MockMachine:
    Pin = MockPin
    WDT = MockWDT
    def freq(self, *args): 
        if args: print(f"[MOCK] CPU Freq set to {args[0]}")
        return 150_000_000
    def reset(self):
        print("[MOCK] System Reset Requested.")
        sys.exit(0)

class MockNetwork:
    STA_IF = 1
    class WLAN:
        def __init__(self, *args): pass
        def active(self, *args): pass
        def connect(self, *args): pass
        def isconnected(self): return True
        def status(self): return 3 # Got IP

class MockNTPTime:
    def settime(self):
        print("[MOCK] Time synced with PC RTC.")

class MockRP2:
    def country(self, *args): pass

# --- INJECT MOCKS ---
try:
    import machine
except ImportError:
    sys.modules['machine'] = MockMachine()
    sys.modules['network'] = MockNetwork()
    sys.modules['ntptime'] = MockNTPTime()
    sys.modules['rp2'] = MockRP2()

# --- ALIAS STANDARD LIBRARIES ---
try: import uasyncio
except ImportError: sys.modules['uasyncio'] = asyncio

try: import ujson
except ImportError: sys.modules['ujson'] = json

try: import utime
except ImportError: sys.modules['utime'] = time

try: import uos
except ImportError:
    import os
    sys.modules['uos'] = os
    os.rename = os.replace # Fix for Windows rename-over-existing error

try: import urequests
except ImportError:
    import requests
    # Minimal shim for urequests.post/get response object
    class URequestsShim:
        def __init__(self, r): self.r = r
        def json(self): return self.r.json()
        def close(self): pass
        @property
        def text(self): return self.r.text
        
    class URequestsModule:
        def post(self, url, **kwargs):
            return URequestsShim(requests.post(url, **kwargs))
        def get(self, url, **kwargs):
            return URequestsShim(requests.get(url, **kwargs))
            
    sys.modules['urequests'] = URequestsModule()

try: import micropython
except ImportError:
    import gc
    def mock_threshold(x): pass
    gc.threshold = mock_threshold 
    gc.mem_free = lambda: 1024 * 1024 # Mock 1MB free
    gc.mem_alloc = lambda: 0
    
    class MockMicroPython:
        def const(self, x): return x
        def opt_level(self, x): pass
        def alloc_emergency_exception_buf(self, x): pass
        def schedule(self, f, arg): f(arg)
    sys.modules['micropython'] = MockMicroPython()

print("--- PC COMPATIBILITY LAYER ACTIVE ---")
TERMINAL_MODE = False
print("--- TELEGRAM POLLER MODE ENABLED ---")
