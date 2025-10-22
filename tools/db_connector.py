# DB Connector Class 
import sqlite3
from config import DB_PATH

class SQLiteConnector:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def list_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in self.cursor.fetchall()]

    def describe_table(self, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        return self.cursor.fetchall()

    def get_schema_summary(self):
        summary = []
        for table in self.list_tables():
            cols = self.describe_table(table)
            formatted = f"Table: {table} Columns: {[col[1] for col in cols]}"
            summary.append(formatted)
        return "\n".join(summary)