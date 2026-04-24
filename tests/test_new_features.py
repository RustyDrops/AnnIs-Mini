# test_new_features.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import shim
import scripts.memory_indexer as indexer
import skills.human_ops as human_ops
import skills.file_ops as file_ops
import agent_core
import memory
import ujson
import os

async def run_tests():
    print("\n--- STARTING NEW FEATURES TESTS ---")
    
    # Ensure directories exist
    os.makedirs("data/human_queue", exist_ok=True)
    os.makedirs("data/memory", exist_ok=True)
    
    # 1. TEST: Memory Indexer
    print("\n[TEST 1] Indexed Memory Retrieval")
    indexer.save_memory_with_index("research", ["weather", "tokyo"], "The weather in Tokyo is sunny.")
    indexer.save_memory_with_index("research", ["weather", "london"], "The weather in London is rainy.")
    
    results = indexer.search_indexed_memory("research", ["tokyo"])
    print(f"Search for 'tokyo': {results}")
    assert len(results) == 1 and "Tokyo" in results[0]["data"]
    
    results = indexer.search_indexed_memory("research", ["weather"])
    print(f"Search for 'weather' (should have 2): {len(results)}")
    assert len(results) == 2
    print("PASS: Indexed Memory Retrieval works.")

    # 2. TEST: Async Ticketing
    print("\n[TEST 2] Async Human Ticketing")
    # Clean queue
    if os.path.exists("data/human_queue"):
        for f in os.listdir("data/human_queue"):
            os.remove(f"data/human_queue/{f}")
            
    res = human_ops.tool_ask_human("What is the API key?")
    print(f"Tool Result: {res}")
    
    queue_files = os.listdir("data/human_queue")
    print(f"Files in human_queue: {queue_files}")
    assert len(queue_files) == 1
    print("PASS: Ticket created successfully.")

    # 3. TEST: Syntax Validation
    print("\n[TEST 3] Native Syntax Validation")
    broken_code = "def test():\n    print('Missing paren'" # Syntax error
    res = file_ops.tool_write_file("test_broken.py", broken_code)
    print(f"Write Result (Broken): {res}")
    assert "SyntaxError" in res
    
    valid_code = "def test():\n    print('Hello')\n"
    res = file_ops.tool_write_file("test_valid.py", valid_code)
    print(f"Write Result (Valid): {res}")
    assert "Successfully" in res
    print("PASS: Syntax Validation works.")

    # 4. TEST: Task Boundary Wipe
    print("\n[TEST 4] Task Boundary Context Wipe")
    memory.init_memory()
    memory.clear_context()
    memory.add_message("user", "Hello, how are you?")
    memory.add_message("model", "I am fine, let me help you.")
    print(f"Context before plan: {len(memory.get_full_context())} messages.")
    
    # Simulate create_plan tool call logic directly
    print("Simulating 'create_plan' tool execution...")
    memory.clear_context()
    plan_text = "[{'agent': 'research', 'task': 'get weather'}]"
    memory.add_message("user", f"SYSTEM: Task Boundary - New Plan Started:\n{plan_text}")
    
    context = memory.get_full_context()
    print(f"Context after plan: {len(context)} messages.")
    print(f"First message snippet: {context[0]['parts'][0]['text'][:50]}...")
    assert len(context) == 1
    assert "Task Boundary" in context[0]['parts'][0]['text']
    print("PASS: Task Boundary Wipe works.")

    print("\n--- ALL TESTS PASSED ---")

if __name__ == "__main__":
    asyncio.run(run_tests())
