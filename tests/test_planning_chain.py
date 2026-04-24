# test_planning_chain.py
import asyncio
import shim
import agent_core
import memory
import api_client

async def run_test():
    print("--- STARTING PLANNING CHAIN TEST ---")
    memory.init_memory()
    
    # Prompt that forces a multi-step plan
    test_prompt = "I want to build a weather-aware lamp. Research the current sky conditions in Tokyo and then write a MicroPython script that sets a NeoPixel LED to Blue if it's raining or Yellow if it's sunny."
    print(f"USER: {test_prompt}\n")
    
    await agent_core.process_message(test_prompt)
    
    print("\n--- CHECKING BUDGET ---")
    print(api_client.get_budget_status())
    print("--- TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(run_test())
