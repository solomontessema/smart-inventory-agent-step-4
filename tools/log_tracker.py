# Tracks agent actions and stores execution logs 
import sqlite3
from datetime import datetime
from config import DB_PATH

 
def track_log(action: str, details: str = "") -> str:
 
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    timestamp = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO logs (timestamp, action, details) VALUES (?, ?, ?)",
        (timestamp, action, details)
    )

    conn.commit()
    conn.close()

    return f"Logged action: {action}"


def log_wrapper(input: str) -> str:
    # Expect input like "Queried inventory | Checked products below threshold"
    try:
        action, details = input.split(" | ", 1)
    except ValueError:
        action, details = input, ""
    return track_log(action.strip(), details.strip())