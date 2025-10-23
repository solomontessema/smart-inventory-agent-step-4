
from typing import Any, Dict
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from tools.database_reader import read_database_tool         
from tools.web_searcher import web_search_tool        
from tools.email_sender import send_email_tool     
from tools.log_tracker import track_log_tool           
from config import OPENAI_API_KEY, AGENT_NAME, BOSS_NAME

# ---------------------------
# LLM
# ---------------------------
# This uses a current small model with better tool-following.
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=OPENAI_API_KEY
)

# ---------------------------
# Memory
# ---------------------------
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="input"
)

# ---------------------------
# Tools
# ---------------------------
tools = [
    Tool(
        name="Database Reader",
        func=read_database_tool,
        description="Execute a SQL query and return raw tabular results. Use for inventory & thresholds."
    ),
    Tool(
        name="Supplier Finder",
        func=web_search_tool,
        description="Search suppliers by product name, barcode, or category."
    ),
    Tool(
        name="Email Sender",
        func=send_email_tool,
        description="Send an email using: subject || body"
    ),
    Tool(
        name="Log Tracker",
        func=track_log_tool,
        description="Record actions/results for auditing & debugging."
    ),
]

# ---------------------------
# Prompt
# ---------------------------
prompt_template = PromptTemplate(
    input_variables=["input", "chat_history", "agent_scratchpad", "tools", "tool_names", "AGENT_NAME", "BOSS_NAME"],
    template="""
You are an inventory assistant named {AGENT_NAME}. The user is {BOSS_NAME}.
Task: identify products below their threshold using the database.

Data model:
- products(name, barcode, threshold)
- inventory(name, barcode, quantity)

You have tools:
{tools}

Rules:
- Prefer ONE SQL that joins products with inventory, aggregates quantity, and filters total < threshold.
- When writing SQL, write ONLY the SQL (no backticks/markdown/comments).
- Always ground your Final Answer in the actual tool Observation.
- If a tool fails, try a corrected attempt; do not conclude after an error.
- Keep the final answer concise and helpful.

When using the Email Sender tool:
- Format the body as professional HTML (use <p>, <ul>, <li>, <b>, <a> tags).
- Do not include Markdown or \n escapes.

Available tool names: {tool_names}

Format:
Thought: reasoning
Action: one of [{tool_names}]
Action Input: input for the action (SQL on one line, no fences)
Observation: (system will insert the tool result)
... (repeat Thought/Action/Action Input/Observation if needed)
Thought: I now know the final answer
Final Answer: concise result grounded in Observation

Example (for low stock):
Thought: I should run a single SQL that computes total quantities vs thresholds.
Action: Database Reader
Action Input: SELECT p.name, p.barcode, COALESCE(SUM(i.quantity),0) AS total_quantity, p.threshold
FROM products p LEFT JOIN inventory i ON i.barcode = p.barcode
GROUP BY p.name, p.barcode, p.threshold
HAVING COALESCE(SUM(i.quantity),0) < p.threshold
ORDER BY p.name;

Observation: name|barcode|total_quantity|threshold
Widget A|12345|4|10
Cable|99999|0|5

Thought: I have the products below threshold.
Final Answer: Low stock:
- Widget A (12345): total_quantity=4, threshold=10
- Cable (99999): total_quantity=0, threshold=5

Conversation history:
{chat_history}

User query: {input}

{agent_scratchpad}
"""
)

# ---------------------------
# Agent
# ---------------------------
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt_template)

inventory_agent = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=False,                
    handle_parsing_errors=False,
    max_iterations=6,              
    early_stopping_method="generate",
    return_intermediate_steps=True 
)

# ---------------------------
# Runner
# ---------------------------
def run_inventory_agent(user_input)-> Dict[str, Any]:
    result = inventory_agent.invoke({
        "input": user_input,
        "AGENT_NAME": AGENT_NAME,
        "BOSS_NAME": BOSS_NAME
    })
    return result

