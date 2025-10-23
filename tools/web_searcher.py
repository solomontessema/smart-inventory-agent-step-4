# Tool to search the web 
import os
from langchain_tavily import TavilySearch
from config import TAVILY_API_KEY

# Initialize Tavily search tool
search_tool = TavilySearch(
    api_key=TAVILY_API_KEY,
    max_results=3,
    include_answer=True
)

def web_search_tool(query: str) -> str:

    if not query:
        return "No query provided."

    try:
        results = search_tool.invoke({"query": query})

        if not results or not results.get("results"):
            return f"No results found for '{query}'."

        output = f"Search results for **{query}**:\n"
        for result in results["results"]:
            title = result.get("title", "No title")
            url = result.get("url", "")
            snippet = result.get("content", "")
            output += f"- \[{title}\]({url})\n  {snippet}\n\n"

        return output.strip()

    except Exception as e:
        return f"Error during search: {str(e)}"