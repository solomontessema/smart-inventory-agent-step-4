import sqlite3
from datetime import datetime
from config import DB_PATH

 
def track_log_tool(input: str) -> str:
    try:
        action, details = input.split(" | ", 1)
    except ValueError:
        action, details = input, ""

    timestamp = datetime.now().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (timestamp, action, details) VALUES (?, ?, ?)",
            (timestamp, action.strip(), details.strip())
        )
        conn.commit()

    return f"✅ Logged: {action.strip()}"
