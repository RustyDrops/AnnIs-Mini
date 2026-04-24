# test_research.py
import asyncio
import shim
import agent_core
import memory

async def run_test():
    print("--- STARTING RESEARCH TEST ---")
    memory.init_memory()
    
    test_prompt = "Who won the most recent Super Bowl and what was the score?"
    print(f"USER: {test_prompt}")
    
    await agent_core.process_message(test_prompt)
    print("--- TEST COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(run_test())
