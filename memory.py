# memory.py
import ujson
import uos
import gc
from locks import state_lock

MEMORY_FILE = "context.json"
MAX_MESSAGES = 14  # 7 chats (User + Bot turns)
ram_buffer = [] 

def init_memory():
    global ram_buffer
    with state_lock:
        try:
            with open(MEMORY_FILE, 'r') as f:
                ram_buffer = ujson.load(f)
            print(f"Memory: Loaded {len(ram_buffer)} messages.")
        except OSError:
            ram_buffer = []

def add_message(role, text):
    global ram_buffer
    with state_lock:
        ram_buffer.append({"role": role, "parts": [{"text": text}]})
        
        # Keep only the last MAX_MESSAGES
        while len(ram_buffer) > MAX_MESSAGES:
            ram_buffer.pop(0)
            
        # Persist to flash so it survives reboot
        try:
            with open(MEMORY_FILE + ".tmp", 'w') as f:
                ujson.dump(ram_buffer, f)
            uos.rename(MEMORY_FILE + ".tmp", MEMORY_FILE)
        except Exception as e:
            print(f"Memory Save Error: {e}")

def get_full_context():
    return ram_buffer

def clear_context():
    global ram_buffer
    with state_lock:
        ram_buffer = []
        try:
            with open(MEMORY_FILE + ".tmp", 'w') as f:
                ujson.dump(ram_buffer, f)
            uos.rename(MEMORY_FILE + ".tmp", MEMORY_FILE)
        except Exception as e:
            print(f"Memory Save Error: {e}")

def slice_context(turns: int):
    global ram_buffer
    with state_lock:
        messages_to_keep = turns * 2
        if len(ram_buffer) > messages_to_keep:
            ram_buffer = ram_buffer[-messages_to_keep:]
            try:
                with open(MEMORY_FILE + ".tmp", 'w') as f:
                    ujson.dump(ram_buffer, f)
                uos.rename(MEMORY_FILE + ".tmp", MEMORY_FILE)
            except Exception as e:
                print(f"Memory Save Error: {e}")

def replace_context(messages):
    global ram_buffer
    with state_lock:
        ram_buffer = messages
        try:
            with open(MEMORY_FILE + ".tmp", 'w') as f:
                ujson.dump(ram_buffer, f)
            uos.rename(MEMORY_FILE + ".tmp", MEMORY_FILE)
        except Exception as e:
            print(f"Memory Save Error: {e}")
