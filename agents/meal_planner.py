"""Meal Planner Agent - Plans meals using Google ADK with google_search + RecipeRefiner sub-agent."""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from agents.search_agent import search_agent
from storage.sqlite_storage import SQLiteStorage
from utils.logger import setup_logger
from google.adk.tools import AgentTool

logger = setup_logger(__name__)


def get_family_preferences(family_id: str) -> Dict[str, Any]:
    """Get family dietary preferences and restrictions from database."""
    try:
        storage = SQLiteStorage()
        family = storage.get_family(family_id)
        if not family:
            return {"status": "error", "error_message": f"Family {family_id} not found"}
        
        return {
            "status": "success",
            "preferences": {
                "family_name": family.get('name', 'Unknown'),
                "members_count": len(family.get('members', [])),
                "dietary_restrictions": family.get('dietary_restrictions', []),
                "preferred_cuisines": family.get('preferred_cuisines', ['Indian']),
                "allergies": family.get('allergies', []),
                "members": family.get('members', [])
            }
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "error", "error_message": str(e)}


def save_meal_plan(family_id: str, date: str, meal_data: Dict[str, Any]) -> Dict[str, Any]:
    """Save meal plan to database."""
    try:
        storage = SQLiteStorage()
        plan_data = {
            'week_start_date': date,
            'meal_plan': meal_data.get('recipes', {}),
            'notes': meal_data.get('notes', ''),
            'approved': True
        }
        plan_id = storage.save_weekly_plan(family_id, plan_data)
        logger.info(f"Saved meal {plan_id}")
        return {"status": "success", "plan_id": plan_id}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "error", "error_message": str(e)}


class MealPlannerAgent(BaseAgent):
    """Meal planning agent using google_search + RecipeRefiner sub-agent (ADK pattern)."""
    
    def __init__(self):
        instruction = """You plan Indian family meals using SearchAgent for web recipes.

You MUST ALWAYS follow these steps:
1) Get the family's preferences using the 'get_family_preferences' tool.
2) Search for suitable recipes using the 'SearchAgent' that match the family's requirements.
3) Create a detailed meal plan with the recipes, adjusting servings for 4 people.
4) Save the final meal plan using the 'save_meal_plan' tool.

CRITICAL: Return ONLY valid JSON in this EXACT format:
{
  "meal_plan": [
    {
      "day": "Monday",
      "breakfast": {
        "meal_name": "Poha",
        "prep_time_minutes": 15,
        "servings": 4,
        "ingredients": ["poha", "onion", "peanuts", "turmeric"],
        "recipe_steps": "1. Rinse poha...",
        "reference_link": "https://..."
      },
      "lunch": {...},
      "dinner": {...}
    },
    ... (7 days total)
  ],
  "grocery_list": {
    "vegetables": [{"item": "onions", "quantity": "1 kg"}],
    "grains": [{"item": "rice", "quantity": "2 kg"}],
    "spices": [{"item": "turmeric", "quantity": "50g"}],
    "dairy": [...],
    "other": [...]
  },
  "summary": "7-day vegetarian meal plan with quick breakfasts, simple lunches, heavy dinners"
}

Return ONLY the JSON - no extra text before or after!"""
        
        tools = [
            AgentTool(agent=search_agent.get_agent()),
            get_family_preferences,
            save_meal_plan
        ]
        
        super().__init__(
            name="MealPlannerAgent",
            instruction=instruction,
            tools=tools,
            model="gemini-2.5-flash-lite",
            output_key="meal_plan"
        )
        logger.info("MealPlannerAgent initialized")
    
    async def plan_meals(self, family_id: str, request: str, num_days: int = 7, dietary_restrictions: list = None, preferences: dict = None) -> Any:
        """Plan meals using natural language request (handles daily, weekly, special occasions).
        
        Args per architecture input format:
            family_id: Family identifier
            request: Natural language ("Plan this week", "Plan tomorrow", "Plan Diwali party for 20")
            num_days: Number of days to plan (default: 7)
            dietary_restrictions: List like ["no_seafood", "vegetarian_option"]
            preferences: Dict like {"cuisine": ["Italian"], "kid_friendly": true}
        """
        restrictions_str = ", ".join(dietary_restrictions) if dietary_restrictions else "none"
        prefs_str = str(preferences) if preferences else "Indian cuisine"
        
        query = f"""Plan meals for family {family_id}.

User request: {request}
Days: {num_days}
Dietary restrictions: {restrictions_str}
Preferences: {prefs_str}

1. Use get_family_preferences tool
2. Use SearchAgent to find recipes
3. Create meal plan with the recipes found
4. Save using save_meal_plan tool

Return complete meal plan with recipes."""
        
        # Use run_debug() to get events, caller will extract final text
        return await self.run_debug(query)


meal_planner_agent = MealPlannerAgent()
