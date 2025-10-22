
from langchain_community.chat_models import ChatOpenAI
# agents/inventory_agent.py

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import OPENAI_API_KEY, AGENT_NAME, BOSS_NAME

# Tool functions
from tools.database_reader import read_database
from tools.web_search_tool import web_search_tool
from tools.email_sender import send_email_tool
from tools.log_tracker import log_wrapper

# Step 1: Define tools with metadata
tool_definitions = [
    {
        "name": "Database Reader",
        "func": read_database,
        "description": "Query database tables to check stock levels, availability, and thresholds."
    },
    {
        "name": "Supplier Finder",
        "func": web_search_tool,
        "description": "Search for suppliers based on product name, barcode, or category."
    },
    {
        "name": "Email Sender",
        "func": send_email_tool,
        "description": "Send an email using the format: subject || body."
    },
    {
        "name": "Log Tracker",
        "func": log_wrapper,
        "description": "Track agent actions and store execution logs for auditing and debugging."
    }
]

# Step 2: Build registry and metadata strings
tool_registry = {tool["name"]: tool["func"] for tool in tool_definitions}
tool_descriptions = "\n".join([f"{tool['name']}: {tool['description']}" for tool in tool_definitions])
tool_names = ", ".join([tool["name"] for tool in tool_definitions])

# Step 3: Prompt template
prompt_template = PromptTemplate(
    input_variables=["input", "agent_scratchpad", "tools", "tool_names", "AGENT_NAME", "BOSS_NAME"],
    template="""
You are an inventory assistant named {AGENT_NAME}. Your boss is {BOSS_NAME}.
You help check stock levels, identify low inventory items, and communicate updates.

You have access to the following tools:
{tools}

Available tool names: {tool_names}

Use this format:
Thought: ...
Action: ...
Action Input: ...
Observation: ...
(Repeat as needed)
Thought: I now know the final answer.
Final Answer: ...

User query: {input}

{agent_scratchpad}
"""
)

# Step 4: LLM and parser
llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
parser = StrOutputParser()

# Step 5: Agent loop with tool execution
def run_inventory_agent(user_input: str) -> str:
    scratchpad = ""

    while True:
        prompt = prompt_template.format(
            input=user_input,
            agent_scratchpad=scratchpad,
            tools=tool_descriptions,
            tool_names=tool_names,
            AGENT_NAME=AGENT_NAME,
            BOSS_NAME=BOSS_NAME
        )

        raw_response = llm.invoke(prompt)
        response = raw_response.content if hasattr(raw_response, "content") else str(raw_response)
        scratchpad += f"\n{response}"

        if "Final Answer:" in response:
            return response.split("Final Answer:")[-1].strip()

        # Parse Action and Action Input
        action = None
        action_input = None
        for line in response.splitlines():
            if line.strip().startswith("Action:"):
                action = line.split("Action:")[1].strip()
            elif line.strip().startswith("Action Input:"):
                action_input = line.split("Action Input:")[1].strip()

        if action and action_input and action in tool_registry:
            try:
                result = tool_registry[action](action_input)
                scratchpad += f"\nObservation: {result}"
            except Exception as e:
                scratchpad += f"\nObservation: ❌ Error executing {action}: {str(e)}"
        else:
            scratchpad += "\nObservation: ❌ Invalid action or missing input"

