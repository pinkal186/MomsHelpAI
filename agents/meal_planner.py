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
        
        # Handle the actual database structure where preferences are nested
        preferences = family.get('preferences', {})
        
        return {
            "status": "success",
            "preferences": {
                "family_name": preferences.get('name', family.get('name', 'Unknown')),
                "members_count": len(preferences.get('members', [])),
                "dietary_restrictions": family.get('dietary_restrictions', []),
                "preferred_cuisines": preferences.get('preferred_cuisines', ['Indian']),
                "allergies": preferences.get('allergies', []),
                "spice_level": preferences.get('spice_level', 'medium'),
                "members": preferences.get('members', [])
            }
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "error", "error_message": str(e)}


def save_meal_plan(family_id: str, date: str, meal_data: Dict[str, Any]) -> Dict[str, Any]:
    """Save meal plan to database."""
    try:
        storage = SQLiteStorage()
        
        # Handle both list and dict formats for meal_plan
        meal_plan_raw = meal_data.get('meal_plan', [])
        meal_plan_dict = {}
        
        if isinstance(meal_plan_raw, list):
            # Convert from list format to dict format expected by storage
            for day_plan in meal_plan_raw:
                if isinstance(day_plan, dict):
                    day = day_plan.get('day', 'Today')
                    meal_plan_dict[day] = {
                        'breakfast': day_plan.get('breakfast', {}),
                        'lunch': day_plan.get('lunch', {}), 
                        'dinner': day_plan.get('dinner', {})
                    }
        elif isinstance(meal_plan_raw, dict):
            # Already in dict format, use as is
            meal_plan_dict = meal_plan_raw
        else:
            # Handle unexpected format - save whatever we have
            logger.warning(f"Unexpected meal_plan format: {type(meal_plan_raw)}. Saving as-is: {meal_plan_raw}")
            meal_plan_dict = {"raw_data": meal_plan_raw}
        
        plan_data = {
            'week_start_date': date,
            'meal_plan': meal_plan_dict,  # Now in correct format for storage
            'shopping_list': meal_data.get('grocery_list', {}),
            'notes': meal_data.get('summary', ''),
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
        instruction = """You are a meal planning assistant. You MUST complete ALL 4 steps for every request:

MANDATORY WORKFLOW:
STEP 1: Get family preferences using 'get_family_preferences' tool
STEP 2: Search for recipes using 'SearchAgent' based on the user's request and family preferences  
STEP 3: Create a meal plan with the found recipes in the exact format below
STEP 4: Save the meal plan using 'save_meal_plan' tool

CRITICAL REQUIREMENTS:
- You MUST complete all 4 steps in sequence
- Never stop after step 1 or 2 - always continue to create and save the meal plan
- After getting search results, immediately create the JSON meal plan
- After creating the meal plan, immediately call save_meal_plan with the complete data
- The user is waiting for a complete meal plan - do not give incomplete responses

PLANNING RULES:
- Analyze the user request to determine what to plan:
  * "today's dinner" → Plan only dinner for today
  * "Monday and Tuesday meals" → Plan meals for Monday and Tuesday only
  * "this week" → Plan all meals for 7 days
  * "next 3 days breakfast" → Plan only breakfast for next 3 days
- Only fill in meals that were specifically requested
- Use empty {} for meals not requested
- Always use 4 servings for family meals
- Days should be named clearly: "Today", "Tomorrow", "Monday", "Tuesday", etc.

MEAL PLAN STRUCTURE - use exactly this format (meal_plan must be a LIST):
{
  "meal_plan": [
    {
      "day": "Monday",
      "breakfast": {
        "meal_name": "Poha",
        "prep_time_minutes": 15,
        "servings": 4,
        "ingredients": ["poha", "onion", "turmeric"],
        "recipe_steps": "1. Rinse poha. 2. Cook with onions...",
        "reference_link": "https://recipe-link.com"
      },
      "lunch": {},  // Empty if not requested
      "dinner": {}  // Empty if not requested
    }
    // Only include days that user requested
  ],
  "grocery_list": {
    "vegetables": [{"item": "onions", "quantity": "1 kg"}],
    "grains": [{"item": "poha", "quantity": "500g"}],
    "spices": [{"item": "turmeric", "quantity": "50g"}],
    "dairy": [],
    "other": []
  },
  "summary": "plan generate any spefication taken care, for user need to focus. "
}

EXAMPLES:
- Request: "today's dinner" → meal_plan has 1 day with only dinner filled, breakfast/lunch empty
- Request: "next 3 days breakfast" → meal_plan has 3 days with only breakfast filled, lunch/dinner empty
- Request: "this week" → meal_plan has 7 days with all meals filled (breakfast, lunch, dinner)

CRITICAL: Always ensure meal_plan is a LIST of day objects, never a dict. Complete all 4 steps!"""
        
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
        """Plan meals using natural language request."""
        from datetime import datetime
        
        # Explicit query to ensure all 4 steps are completed
        query = f"""Plan meals for family {family_id}.

User request: {request}

Family ID: {family_id}
Date: {datetime.now().strftime('%Y-%m-%d')}
"""
        
        # Use run_debug() to get events
        return await self.run_debug(query)


meal_planner_agent = MealPlannerAgent()
