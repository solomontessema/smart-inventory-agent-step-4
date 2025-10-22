from tools.db_connector import SQLiteConnector
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from config import OPENAI_API_KEY


connector = SQLiteConnector()
schema_summary = connector.get_schema_summary()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template="""
    Given the database schema:
    {schema}

    Write only the SQLite SQL query to answer the question below.
    Do not include any explanation or commentary.

    Question:
    {question}
    """
)


sql_chain = prompt | llm | StrOutputParser()

def generate_sql(question: str):
    return sql_chain.run({"schema": schema_summary, "question": question})

def run_query(query):
    try:
        cursor = connector.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return columns, rows
    except Exception as e:
        return None, f"SQL Error: {str(e)}"


def format_results(columns, rows):
    if not rows:
        return "No results found."
    
    output = ""
    for row in rows:
        row_text = ", ".join(f"{col}: {val}" for col, val in zip(columns, row))
        output += f"- {row_text}\n"
    return output


def read_database(question):
    sql = generate_sql(question)
    columns, rows_or_error = run_query(sql)

    if isinstance(rows_or_error, str):  # error message
        return f"Error executing SQL: {rows_or_error}"
    return format_results(columns, rows_or_error)

   