import ujson
try:
    import uos as os
except ImportError:
    import os

def reindex_memory(category="research"):
    """
    Scans the JSONL file and rebuilds the inverted index based on tags.
    """
    jsonl_path = f"data/memory/{category}.jsonl"
    index_path = f"data/memory/{category}_index.json"
    
    index = {}
    
    try:
        with open(jsonl_path, 'r') as f:
            while True:
                # Get the byte offset BEFORE reading the line
                offset = f.tell()
                line = f.readline()
                if not line:
                    break
                
                try:
                    entry = ujson.loads(line)
                    tags = entry.get("tags", [])
                    for tag in tags:
                        if tag not in index:
                            index[tag] = []
                        index[tag].append(offset)
                except ValueError:
                    # Skip invalid JSON lines
                    pass
    except OSError:
        pass
        
    with open(index_path, 'w') as f:
        ujson.dump(index, f)
        
    return index

def save_memory_with_index(category: str, tags: list, data: str):
    """
    Appends a new memory to the JSONL and updates the index file.
    """
    jsonl_path = f"data/memory/{category}.jsonl"
    index_path = f"data/memory/{category}_index.json"
    
    entry = {"tags": tags, "data": data}
    line = ujson.dumps(entry) + "\n"
    
    try:
        offset = os.stat(jsonl_path)[6]
    except OSError:
        offset = 0
        
    # Append to JSONL
    with open(jsonl_path, 'a') as f:
        f.write(line)
        
    # Update the index file
    try:
        with open(index_path, 'r') as f:
            index = ujson.load(f)
    except (OSError, ValueError):
        index = {}
        
    for tag in tags:
        if tag not in index:
            index[tag] = []
        index[tag].append(offset)
        
    with open(index_path, 'w') as f:
        ujson.dump(index, f)
        
    return True

def search_indexed_memory(category: str, tags: list, max_results: int = 5):
    """
    Reads the index, finds byte offsets for the given tags,
    and returns the matching memories using f.seek().
    """
    index_path = f"data/memory/{category}_index.json"
    jsonl_path = f"data/memory/{category}.jsonl"
    
    try:
        with open(index_path, 'r') as f:
            index = ujson.load(f)
    except (OSError, ValueError):
        return []
        
    # Collect all offsets for the given tags
    offsets = set()
    for tag in tags:
        if tag in index:
            for offset in index[tag]:
                offsets.add(offset)
                
    # Sort offsets (latest first, which means highest offset first)
    sorted_offsets = sorted(list(offsets), reverse=True)[:max_results]
    
    results = []
    if not sorted_offsets:
        return results
        
    try:
        with open(jsonl_path, 'r') as f:
            for offset in sorted_offsets:
                f.seek(offset)
                line = f.readline()
                if line:
                    try:
                        results.append(ujson.loads(line))
                    except ValueError:
                        pass
    except OSError:
        pass
        
    return results
