# test_mega_chain.py
import asyncio
import shim
import agent_core
import memory
import api_client
import os

async def run_test():
    # Reset
    if os.path.exists('context.json'): os.remove('context.json')
    if os.path.exists('stats.json'): os.remove('stats.json')
    
    print("--- STARTING MEGA CHAIN TEST ---")
    memory.init_memory()
    
    # 1. Ask for budget
    print("USER: ~budget")
    await agent_core.process_message("~budget")
    
    # 2. The Mega Prompt
    test_prompt = (
        "Research the current weather in Tokyo, design a 128x64 OLED UI for it, "
        "write the MicroPython code to run it on a Pico 2W, audit the system health, "
        "and finally write a funny headline for the result."
    )
    print(f"\nUSER: {test_prompt}\n")
    await agent_core.process_message(test_prompt)
    
    # 3. Final Budget check
    print("\n--- FINAL BUDGET CHECK ---")
    print(api_client.get_budget_status())
    print("--- TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(run_test())
