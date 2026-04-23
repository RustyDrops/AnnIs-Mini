# sys_mgmt.py
import machine
import _thread

# Thread-safe tracker for system activity.
# DFS (Dynamic Frequency Scaling) is DISABLED for Pico 2W stability.
_lock = _thread.allocate_lock()
_active_boosts = 0

def boost_cpu():
    """Tracks a high-priority task. Logic preserved but clock-scaling REMOVED."""
    global _active_boosts
    with _lock:
        _active_boosts += 1

def idle_cpu():
    """Releases a task. Logic preserved but clock-scaling REMOVED."""
    global _active_boosts
    with _lock:
        _active_boosts -= 1
        if _active_boosts < 0: _active_boosts = 0

def lock_system_frequency():
    """FORCES the Pico 2W to a stable 150MHz. Prevents WiFi/CYW43 desync."""
    try:
        machine.freq(150_000_000)
        print("CPU locked at 150MHz (WiFi Stability Mode)")
    except:
        pass
