# test_full_chain.py
import asyncio
import shim
import agent_core
import memory
import api_client

async def run_test():
    print("--- STARTING FULL CHAIN TEST ---")
    memory.init_memory()
    
    # Complex prompt requiring Research then Code
    test_prompt = "Research the current weather in London and write a MicroPython script for a Pico 2W to display that temperature on an I2C OLED (SSD1306)."
    print(f"USER: {test_prompt}\n")
    
    await agent_core.process_message(test_prompt)
    
    print("\n--- CHECKING BUDGET ---")
    print(api_client.get_budget_status())
    print("--- TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(run_test())
