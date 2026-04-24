import ujson
import utime
import telegram_bot

def tool_ask_human(question: str) -> str:
    """
    Generates #Q<id>, saves to queue, sends to Telegram. AI does NOT block.
    """
    timestamp = utime.time()
    # Simple ID generation based on timestamp to avoid collisions
    ticket_id = f"#Q{timestamp % 10000}"
    filename = ticket_id.replace("#Q", "")
    filepath = f"data/human_queue/{filename}.json"
    
    payload = {
        "id": ticket_id,
        "question": question,
        "timestamp": timestamp
    }
    
    with open(filepath, 'w') as f:
        ujson.dump(payload, f)
        
    msg = f"[Action Required: {ticket_id}] {question}"
    telegram_bot.send_telegram_msg(msg)
    
    return f"Question added to queue as {ticket_id}. Please move on to other tasks."
