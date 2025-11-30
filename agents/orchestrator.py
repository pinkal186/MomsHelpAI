"""Orchestrator Agent - Sequential coordinator using Google ADK pattern."""

from typing import Any, Optional, Dict
from datetime import datetime
from agents.meal_planner import meal_planner_agent
from agents.week_planner import week_planner_agent
from agents.grocery_planner import grocery_planner_agent
from storage.sqlite_storage import SQLiteStorage
from utils.logger import setup_logger
import json

logger = setup_logger(__name__)


class OrchestratorAgent:
    """Sequential orchestrator - chains agents with proper input/output flow.
    
    Architecture Flow (per TECHNICAL_ARCHITECTURE.md):
    1. MealPlanner(family_id, request, preferences) → meal_plan
    2. WeekPlanner(meal_plan, family_id, start_date) → weekly_schedule
    3. GroceryPlanner(meal_plan, pantry_stock) → shopping_list
    
    Returns comprehensive response with all outputs.
    """
    
    def __init__(self):
        self.storage = SQLiteStorage()
        logger.info("OrchestratorAgent initialized (sequential pattern)")
    
    async def handle_request(
        self,
        user_request: str,
        family_id: str,
        num_days: int = 7,
        dietary_restrictions: list = None,
        preferences: dict = None,
        week_start_date: str = None
    ) -> Dict[str, Any]:
        """Orchestrate complete weekly planning workflow.
        
        Input (per architecture):
            user_request: "Plan this week" or "Quick meals for Monday-Tuesday"
            family_id: Family identifier
            num_days: Days to plan (default 7)
            dietary_restrictions: ["vegetarian", "no_seafood"]
            preferences: {"cuisine": ["Indian"], "quick_meals": true}
            week_start_date: "2025-12-02" (optional)
        
        Output (per architecture):
        {
            "meal_plan": {...},
            "weekly_schedule": {...},
            "shopping_list": {...},
            "agents_executed": ["MealPlanner", "WeekPlanner", "GroceryPlanner"],
            "execution_summary": "Planned 7 days with 21 meals, 5 activities, 24 grocery items"
        }
        """
        logger.info(f"Orchestrating request: {user_request[:80]}...")
        
        if not week_start_date:
            week_start_date = datetime.now().strftime("%Y-%m-%d")
        
        result = {
            "agents_executed": [],
            "meal_plan": None,
            "weekly_schedule": None,
            "shopping_list": None,
            "execution_summary": ""
        }
        
        try:
            # STEP 1: Meal Planning
            logger.info("Step 1: Calling MealPlannerAgent...")
            meal_response = await meal_planner_agent.plan_meals(
                family_id=family_id,
                request=user_request,
                num_days=num_days,
                dietary_restrictions=dietary_restrictions,
                preferences=preferences
            )
            result["agents_executed"].append("MealPlanner")
            result["meal_plan"] = self._extract_meal_plan(meal_response)
            logger.info(f"✓ MealPlanner completed")
            
            # STEP 2: Week Planning (uses meal_plan output)
            logger.info("Step 2: Calling WeekPlannerAgent...")
            # Extract meal_plan array + summary for WeekPlanner
            meal_plan_for_week = self._prepare_meal_plan_for_agents(result["meal_plan"])
            week_response = await week_planner_agent.plan_week(
                family_id=family_id,
                start_date=week_start_date,
                meal_plan_data=meal_plan_for_week
            )
            result["agents_executed"].append("WeekPlanner")
            result["weekly_schedule"] = self._extract_schedule(week_response)
            logger.info(f"✓ WeekPlanner completed")
            
            # STEP 3: Grocery Planning (uses grocery_list from meal_plan)
            logger.info("Step 3: Calling GroceryPlannerAgent...")
            # Extract pre-generated grocery_list from MealPlanner
            grocery_list_data = self._extract_grocery_list_from_meal_plan(result["meal_plan"])
            pantry_stock = self._get_pantry_stock(family_id)
            grocery_response = await grocery_planner_agent.create_shopping_list(
                family_id=family_id,
                grocery_list_data=grocery_list_data,
                pantry_stock=pantry_stock
            )
            result["agents_executed"].append("GroceryPlanner")
            result["shopping_list"] = self._extract_shopping_list(grocery_response)
            logger.info(f"✓ GroceryPlanner completed")
            
            # Generate summary
            result["execution_summary"] = self._generate_summary(result)
            logger.info(f"✓ Orchestration complete: {result['execution_summary']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Orchestration error: {str(e)}")
            result["error"] = str(e)
            return result
    
    def _extract_meal_plan(self, response) -> Dict:
        """Extract meal plan JSON from agent response."""
        if isinstance(response, list):
            # Extract from events
            for event in reversed(response):
                if hasattr(event, 'content') and event.content:
                    if hasattr(event, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                # Try to parse as JSON
                                text = part.text.strip()
                                # Remove markdown code blocks if present
                                if text.startswith('```json'):
                                    text = text[7:]
                                if text.startswith('```'):
                                    text = text[3:]
                                if text.endswith('```'):
                                    text = text[:-3]
                                text = text.strip()
                                
                                try:
                                    return json.loads(text)
                                except json.JSONDecodeError:
                                    # Fallback to text
                                    return {"text_plan": part.text}
            return {"events_count": len(response)}
        return {"raw_response": str(response)[:500]}
    
    def _prepare_meal_plan_for_agents(self, meal_plan_dict: Dict) -> Dict:
        """Extract meal_plan array and summary for WeekPlanner.
        
        From MealPlanner output:
        {
          "meal_plan": [...],
          "grocery_list": {...},
          "summary": "..."
        }
        
        Returns for WeekPlanner:
        {
          "meal_plan": [...],
          "summary": "..."
        }
        """
        if not meal_plan_dict:
            return {"meal_plan": [], "summary": "No meal plan"}
        
        # If it's already structured JSON with meal_plan key
        if isinstance(meal_plan_dict, dict) and "meal_plan" in meal_plan_dict:
            return {
                "meal_plan": meal_plan_dict.get("meal_plan", []),
                "summary": meal_plan_dict.get("summary", "")
            }
        
        # Fallback
        return {"meal_plan": [], "summary": str(meal_plan_dict)[:200]}
    
    def _extract_grocery_list_from_meal_plan(self, meal_plan_dict: Dict) -> Dict:
        """Extract grocery_list from MealPlanner output.
        
        From MealPlanner output:
        {
          "meal_plan": [...],
          "grocery_list": {
            "vegetables": [{"item": "...", "quantity": "..."}],
            ...
          },
          "summary": "..."
        }
        
        Returns grocery_list dict for GroceryPlanner.
        """
        if not meal_plan_dict:
            return {}
        
        if isinstance(meal_plan_dict, dict) and "grocery_list" in meal_plan_dict:
            return meal_plan_dict["grocery_list"]
        
        return {}
    
    def _extract_schedule(self, response) -> Dict:
        """Extract schedule from agent response."""
        return self._extract_meal_plan(response)  # Same pattern
    
    def _extract_shopping_list(self, response) -> Dict:
        """Extract shopping list from agent response."""
        return self._extract_meal_plan(response)  # Same pattern
    
    def _get_pantry_stock(self, family_id: str) -> Dict:
        """Get current pantry stock from storage."""
        try:
            pantry = self.storage.get_pantry(family_id)
            return pantry if pantry else {}
        except:
            return {}
    
    def _generate_summary(self, result: Dict) -> str:
        """Generate execution summary."""
        agents = ", ".join(result["agents_executed"])
        return f"Successfully executed {len(result['agents_executed'])} agents: {agents}"


# Create singleton instance
orchestrator = OrchestratorAgent()
orchestrator_agent = orchestrator  # Alias for consistency
