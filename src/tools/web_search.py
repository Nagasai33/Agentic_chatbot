import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

load_dotenv()


tavily_search = TavilySearch(
    max_results=5,
    topic="general",
    api_key=os.getenv("TAVILY_API_KEY"),
)


@tool
def web_search(query: str) -> str:
    """
    Search the internet for current and up-to-date information.

    Use this tool when the user asks about:
    - latest information
    - current information
    - recent events
    - today's news
    - news
    - current software versions
    - current technology developments
    - information after the model's knowledge cutoff
    - companies, products, people, or events that may have changed recently

    Do NOT use this tool for simple arithmetic calculations.

    Always use this tool when the user specifically asks to search
    the web or asks for the latest/current information.
    """

    result = tavily_search.invoke({
        "query": query
    })

    return str(result)