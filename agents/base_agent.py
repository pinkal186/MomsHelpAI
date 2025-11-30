"""BaseAgent - Wrapper for Google ADK Agent following Kaggle patterns."""

from typing import List, Optional, Any
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from utils.config import Config
from utils.logger import setup_logger
import os

logger = setup_logger(__name__)


class BaseAgent:
    """Base class wrapping google.adk.agents.Agent with common configuration."""
    
    def __init__(self, name: str, instruction: str, tools: Optional[List] = None, model: str = "gemini-2.5-flash-lite", output_key: Optional[str] = None, retry_config: Optional[types.HttpRetryOptions] = None, description: str = ""):
        os.environ["GOOGLE_API_KEY"] = Config.GOOGLE_API_KEY
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
        
        self.name = name
        self.model = model
        self.output_key = output_key
        self.tools = tools or []
        self.description = description or f"{name} agent"  # ADD description attribute
        
        if retry_config is None:
            retry_config = types.HttpRetryOptions(
                attempts=5, exp_base=7, initial_delay=1,
                http_status_codes=[429, 500, 503, 504]
            )
        
        self.agent = Agent(name=name, model=model, instruction=instruction, tools=self.tools, output_key=output_key, description=self.description)
        self.runner = InMemoryRunner(agent=self.agent)
        logger.info(f"{name} initialized")
    
    async def run(self, user_message: str, user_id: str = "default_user", session_id: str = "debug_session") -> Any:
        """Run agent using run_async pattern from Kaggle ADK examples."""
        try:
            logger.info(f"{self.name}: {user_message[:80]}...")
            
            query_content = types.Content(role="user", parts=[types.Part(text=user_message)])
            
            result = None
            async for event in self.runner.run_async(user_id=user_id, session_id=session_id, new_message=query_content):
                if event.is_final_response() and event.content and event.content.parts:
                    result = event.content.parts[0].text
            
            logger.info(f"{self.name} completed")
            return result
        except Exception as e:
            logger.error(f"{self.name} error: {str(e)}")
            raise
    
    async def run_debug(self, user_message: str) -> Any:
        """Run agent with debug output using run_debug from Kaggle examples."""
        try:
            response = await self.runner.run_debug(user_message)
            return response
        except Exception as e:
            logger.error(f"{self.name} debug error: {str(e)}")
            raise
    
    def get_agent(self) -> Agent:
        return self.agent
    
    def get_runner(self) -> InMemoryRunner:
        return self.runner
