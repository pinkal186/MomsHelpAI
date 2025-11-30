"""Recipe Refiner Sub-Agent - Refines recipes for family needs (ADK sub-agent pattern)."""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RecipeRefinerAgent(BaseAgent):
    """Sub-agent for recipe refinement (used as tool by MealPlannerAgent)."""
    
    def __init__(self):
        instruction = """You refine recipe suggestions for family meal planning.

When given recipe names or recipe information, create detailed meal plans with:
- Adjusted servings for 4 people
- Vegetarian substitutions if needed
- Simplified preparation steps for quick cooking
- Complete meal structure (breakfast/lunch/dinner format)

Return the refined recipes in a structured format suitable for family meal planning."""
        
        tools = []  # No additional tools - this agent refines using LLM knowledge
        
        super().__init__(
            name="RecipeRefinerAgent",
            instruction=instruction,
            tools=tools,
            model="gemini-2.5-flash-lite",
            output_key="refined_recipes"
        )
        logger.info("RecipeRefinerAgent initialized")


recipe_refiner_agent = RecipeRefinerAgent()
