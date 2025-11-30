"""Search Agent - Dedicated agent for Google Search (ADK pattern)."""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from utils.logger import setup_logger
from google.adk.tools import google_search

logger = setup_logger(__name__)


class SearchAgent(BaseAgent):
    """Dedicated search agent using google_search tool only.
    
    This agent is isolated because google_search cannot be mixed with other tool types
    in gemini-2.5-flash-lite. Other agents use this via AgentTool.
    """
    
    def __init__(self):
        # Generic instruction for flexibility
        instruction = "Use the google_search tool to find information on the given topic. Return the raw search results."
        
        tools = [google_search]  # Only google_search - no mixing!
        
        super().__init__(
            name="SearchAgent",
            instruction=instruction,
            tools=tools,
            model="gemini-2.5-flash-lite",
            output_key="search_results",
            description="Searches for information using Google search"
        )
        logger.info("SearchAgent initialized with google_search tool")


# Create singleton instance
search_agent = SearchAgent()
