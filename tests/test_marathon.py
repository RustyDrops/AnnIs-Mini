# test_marathon.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import shim
import agent_core
import memory
import api_client

async def run_marathon():
    # Load and clean memory
    memory.init_memory()
    memory.clear_context()
    
    print("\n--- BUDGET BEFORE START ---")
    print(api_client.get_budget_status())
    
    marathon_prompt = (
        "Research the top 3 most trending AI news stories of the last 24 hours. "
        "Summarize each story for a high-level executive. "
        "Find a free news API that specifically supports AI or tech topics. "
        "Write a MicroPython script for the Pico 2W that fetches data from that API. "
        "Design a 128x64 OLED layout for a 'News Ticker' dashboard. "
        "And finally, audit the system budget to see how much this entire marathon cost."
    )
    
    print(f"\n[USER]: {marathon_prompt}\n")
    await agent_core.process_message(marathon_prompt)
    
    print("\n--- BUDGET AFTER START ---")
    print(api_client.get_budget_status())

if __name__ == "__main__":
    asyncio.run(run_marathon())
