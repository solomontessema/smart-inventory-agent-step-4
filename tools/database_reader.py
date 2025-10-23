from typing import List, Tuple, Any
from tools.db_connector import SQLiteConnector

connector = SQLiteConnector()


def _exec_sql(sql: str) -> Tuple[List[str], List[Tuple[Any, ...]]]:
    cur = connector.conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description] if cur.description else []
    return cols, rows

def _format_table(cols: List[str], rows: List[Tuple[Any, ...]]) -> str:
    if not cols:
        return "No result columns."
    header = "|".join(cols)
    if not rows:
        return header  # header only when no matches
    lines = [header]
    for r in rows:
        lines.append("|".join("" if v is None else str(v) for v in r))
    return "\n".join(lines)

def read_database_tool(sql: str) -> str:

    if not isinstance(sql, str) or not sql.strip():
        return "Error executing SQL: empty query."

    try:
        cols, rows = _exec_sql(sql)
        return _format_table(cols, rows)
    except Exception as e:
        return f"Error executing SQL: {e}"
