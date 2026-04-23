# locks.py
# Centralized lock registry. Two shared locks for the entire system.
import _thread

net_lock = _thread.allocate_lock()    # Serializes all HTTPS requests (Core 0 + Core 1)
state_lock = _thread.allocate_lock()  # Protects all shared state, files, and queues
