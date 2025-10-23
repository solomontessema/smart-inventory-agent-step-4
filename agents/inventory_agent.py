import re
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import OPENAI_API_KEY, AGENT_NAME, BOSS_NAME
from tools.database_reader import read_database_tool
from tools.web_searcher import web_search_tool
from tools.email_sender import send_email_tool
from tools.log_tracker import track_log_tool

tool_definitions = [
    {"name": "Database Reader", "func": read_database_tool, "description": "Query database tables to check stock levels, availability, and thresholds."},
    {"name": "Supplier Finder", "func": web_search_tool, "description": "Search for suppliers based on product name, barcode, or category."},
    {"name": "Email Sender", "func": send_email_tool, "description": "Send an email using the format: subject || body."},
    {"name": "Log Tracker", "func": track_log_tool, "description": "Track agent actions and store execution logs for auditing and debugging."}
]

tool_registry = {tool["name"]: tool["func"] for tool in tool_definitions}
tool_descriptions = "\n".join([f'{tool["name"]}: {tool["description"]}' for tool in tool_definitions])
tool_names_list = [tool["name"] for tool in tool_definitions]
tool_names_display = ' | '.join([f'"{n}"' for n in tool_names_list])

TOOL_ALIASES = {
    "database reader": "Database Reader",
    "supplier finder": "Supplier Finder",
    "email sender": "Email Sender",
    "log tracker": "Log Tracker",
}

prompt_template = PromptTemplate(
    input_variables=["input", "agent_scratchpad", "tools", "tool_names_display", "AGENT_NAME", "BOSS_NAME"],
    template="""
You are an inventory assistant named {AGENT_NAME}. You help check stock levels and identify low inventory items. Use the products table to know the threshold of each product. Then check if the quantity of any product in the inventory table is below the threshold level. I am your boss and my name is {BOSS_NAME} and will provide you with inventory-related queries.

You have access to the following tools:
{tools}

Rules:
- You must always reason step-by-step and use tools.
- When writing SQL queries, write only the SQL query. Do not include markdown formatting, triple backticks, or commentary.
- Always include the actual results from the tools in your Observation and in the Final Answer. Do not summarize unless explicitly instructed.

Available tool names (choose EXACTLY one, verbatim):
{tool_names_display}

Strict output schema:
Thought: your reasoning
Action: one of {tool_names_display}
Action Input: the complete input on the same line as "Action Input:" with no code fences
Observation: the tool result
(Repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer to the user's original question

Example:

---
User query: What products are low in stock?

Thought: I should check thresholds from products.
Action: "Database Reader"
Action Input: SELECT barcode, name, threshold FROM products
Observation: barcode|name|threshold
Thought: I should aggregate inventory.
Action: "Database Reader"
Action Input: SELECT name, barcode, SUM(quantity) AS total_quantity FROM inventory GROUP BY name, barcode
Observation: product1 and product2 are below their thresholds.
Thought: I should log this action.
Action: "Log Tracker"
Action Input: {{"action":"Queried low inventory","details":"2 products below threshold"}}
Observation: Logged
Thought: I now know the final answer
Final Answer: The following products are low in stock: product1, product2.
---

User query: {input}

{agent_scratchpad}
"""
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)

def extract_action_and_input(text: str):
    t = text.replace("\r\n", "\n")
    action_matches = list(re.finditer(r'^\s*Action:\s*(.+)$', t, flags=re.MULTILINE))
    if not action_matches:
        return None, None
    last_action = action_matches[-1]
    action_raw = last_action.group(1).strip().strip('`"').strip()
    action_norm = action_raw.lower()
    action = TOOL_ALIASES.get(action_norm, None)
    if action is None and action_raw in tool_registry:
        action = action_raw
    post_action = t[last_action.end():]
    ai_match = re.search(r'^\s*Action Input:\s*(.*)$', post_action, flags=re.MULTILINE)
    if not ai_match:
        return action, None
    start_idx = ai_match.end()
    tail = post_action[start_idx:]
    stopper = re.search(r'^\s*(Thought:|Action:|Observation:|Final Answer:)\b', tail, flags=re.MULTILINE)
    if stopper:
        content = (ai_match.group(1) + tail[:stopper.start()]).strip()
    else:
        content = (ai_match.group(1) + tail).strip()
    content = re.sub(r'^```[a-zA-Z0-9_,-]*\s*', '', content)
    content = re.sub(r'\s*```$', '', content).strip()
    return action, content

def run_inventory_agent(user_input: str, max_turns: int = 8) -> str:
    scratchpad = ""
    for _ in range(max_turns):
        prompt = prompt_template.format(
            input=user_input,
            agent_scratchpad=scratchpad,
            tools=tool_descriptions,
            tool_names_display=tool_names_display,
            AGENT_NAME=AGENT_NAME,
            BOSS_NAME=BOSS_NAME
        )
        print("\n--- Prompt Sent to LLM ---\n")
        print(prompt)
        raw_response = llm.invoke(prompt)
        response = raw_response.content if hasattr(raw_response, "content") else str(raw_response)
        scratchpad += f"\n{response}"
        print("\n--- Agent Thought Process ---\n")
        print(scratchpad)
        if "Final Answer:" in response:
            return response.split("Final Answer:")[-1].strip()
        action, action_input = extract_action_and_input(response)
        if action and action_input and action in tool_registry:
            print(f"\nInvoking tool: {action} with input:\n{action_input}")
            try:
                result = tool_registry[action](action_input)
                print(f"Tool result: {result}")
                scratchpad += f"\nObservation: {result}"
            except Exception as e:
                print(f"Tool error: {e}")
                scratchpad += f"\nObservation: Error executing {action}: {str(e)}"
        else:
            print("Invalid action or missing input.")
            scratchpad += "\nObservation: Invalid action or missing input"
    return "Sorry, I couldn't complete the task within the allowed steps."

if __name__ == "__main__":
    q = "List products that are below threshold."
    print(run_inventory_agent(q))
