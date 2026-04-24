# test_interaction.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import shim
import agent_core
import memory
import telegram_bot

async def run_interaction():
    memory.init_memory()
    memory.clear_context()
    
    # Casual Chat
    print("\n[USER]: Hello AnnIs!")
    await agent_core.process_message("Hello AnnIs!")
    
    # Trigger Plan
    print("\n[USER]: Research a free API for weather and write a script.")
    await agent_core.process_message("Research a free API for weather and write a script.")
    
if __name__ == "__main__":
    asyncio.run(run_interaction())
