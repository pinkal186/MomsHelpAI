"""Orchestrator Agent - Sequential coordinator using Google ADK pattern."""

from typing import Any, Optional, Dict, Callable
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
        week_start_date: str = None,
        approval_callback: Optional[Callable[[str, Dict], bool]] = None
    ) -> Dict[str, Any]:
        """Orchestrate complete weekly planning workflow.
        
        Input (per architecture):
            user_request: "Plan this week" or "Quick meals for Monday-Tuesday"
            family_id: Family identifier
            num_days: Days to plan (default 7)
            dietary_restrictions: ["vegetarian", "no_seafood"]
            preferences: {"cuisine": ["Indian"], "quick_meals": true}
            week_start_date: "2025-12-02" (optional)
            approval_callback: Optional function(agent_name, output) -> bool
                              If provided, pauses after MealPlanner for human approval.
                              Return True to continue, False to stop.
        
        Output (per architecture):
        {
            "meal_plan": {...},
            "weekly_schedule": {...},
            "shopping_list": {...},
            "agents_executed": ["MealPlanner", "WeekPlanner", "GroceryPlanner"],
            "execution_summary": "Planned 7 days with 21 meals, 5 activities, 24 grocery items"
        }
        
        With approval_callback, returns after MealPlanner if not approved:
        {
            "meal_plan": {...},
            "status": "awaiting_approval" or "rejected",
            "agents_executed": ["MealPlanner"]
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
            # STEP 1: Meal Planning (wait for completion)
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
            
            # Validate meal plan extraction - fallback to storage if needed
            if result["meal_plan"].get("status") == "no_meal_plan_extracted":
                logger.warning("MealPlanner did not save plan, trying latest from storage...")
                try:
                    latest_plan = self._get_latest_family_plan(family_id)
                    if latest_plan and latest_plan.get('meal_plan'):
                        result["meal_plan"] = latest_plan
                        logger.info("✓ Retrieved meal plan from storage as fallback")
                    else:
                        logger.warning("No fallback meal plan available")
                except Exception as e:
                    logger.error(f"Failed to retrieve fallback plan: {e}")
            else:
                meals_count = len(result['meal_plan'].get('meal_plan', []))
                logger.info(f"✓ MealPlanner completed with meal plan containing {meals_count} days")
            
            # HUMAN-IN-THE-LOOP: Check if approval is required
            if approval_callback is not None:
                logger.info("Requesting human approval for meal plan...")
                approved = approval_callback("MealPlanner", result["meal_plan"])
                
                if not approved:
                    logger.info("Meal plan rejected by human. Stopping workflow.")
                    result["status"] = "rejected"
                    result["execution_summary"] = "Meal plan generated but rejected by user"
                    return result
                
                logger.info("Meal plan approved by human. Continuing workflow...")
            
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
        """Extract meal plan JSON from agent response or retrieve from storage."""
        saved_plan = None
        plan_id = None
        
        if isinstance(response, list):
            # Look for save_meal_plan function call first (most reliable)
            for event in response:
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'function_call') and part.function_call:
                                if part.function_call.name == 'save_meal_plan':
                                    # Extract meal_data from function call args
                                    args = part.function_call.args
                                    if hasattr(args, 'meal_data') and args.meal_data:
                                        try:
                                            # Try to parse if it's a string
                                            if isinstance(args.meal_data, str):
                                                saved_plan = json.loads(args.meal_data)
                                            else:
                                                saved_plan = args.meal_data
                                            logger.info(f"Successfully extracted meal plan from save_meal_plan call")
                                            break
                                        except (json.JSONDecodeError, AttributeError) as e:
                                            logger.warning(f"Failed to parse meal_data: {e}")
                                            continue
                            
                            # Look for save response with plan_id
                            elif hasattr(part, 'function_response') and part.function_response:
                                func_resp = part.function_response.response
                                if isinstance(func_resp, dict) and func_resp.get('plan_id'):
                                    plan_id = func_resp.get('plan_id')
                                    logger.info(f"Found saved plan ID: {plan_id}")
            
            # If we have meal_data from function call, return it
            if saved_plan:
                return saved_plan
            
            # If we have plan_id, retrieve from storage
            if plan_id:
                try:
                    stored_plan = self.storage.get_weekly_plan_by_id(plan_id)
                    if stored_plan:
                        logger.info(f"Retrieved meal plan from storage: {plan_id}")
                        return {
                            "meal_plan": stored_plan.get('meal_plan', []),
                            "grocery_list": stored_plan.get('shopping_list', {}),
                            "summary": stored_plan.get('notes', 'Meal plan from storage')
                        }
                except Exception as e:
                    logger.warning(f"Failed to retrieve plan from storage: {e}")
            
            # Look in agent text responses as fallback
            for event in response:
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                text = part.text.strip()
                                # Look for JSON patterns
                                if '{"meal_plan"' in text or '"meal_plan":' in text:
                                    # Try to extract JSON
                                    import re
                                    # Find JSON-like structures
                                    json_pattern = r'\{[^}]*"meal_plan"[^}]*\[[^\]]*\][^}]*\}'
                                    matches = re.findall(json_pattern, text, re.DOTALL)
                                    
                                    for match in matches:
                                        try:
                                            parsed = json.loads(match)
                                            if isinstance(parsed, dict) and 'meal_plan' in parsed:
                                                logger.info(f"Extracted meal plan from agent text")
                                                return parsed
                                        except json.JSONDecodeError:
                                            continue
            
            # Fallback - create minimal structure
            logger.warning(f"No meal plan extracted from {len(response)} events")
            return {
                "events_count": len(response),
                "status": "no_meal_plan_extracted", 
                "meal_plan": [],
                "grocery_list": {},
                "summary": "No valid meal plan found in agent response"
            }
        
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
            logger.warning("No meal plan data provided to WeekPlanner")
            return {"meal_plan": [], "summary": "No meal plan available"}
        
        # Check if extraction failed
        if meal_plan_dict.get("status") == "no_meal_plan_extracted":
            logger.warning("Meal plan extraction failed, providing empty plan to WeekPlanner")
            return {"meal_plan": [], "summary": "Meal plan extraction failed"}
        
        # If it's already structured JSON with meal_plan key
        if isinstance(meal_plan_dict, dict) and "meal_plan" in meal_plan_dict:
            meals = meal_plan_dict.get("meal_plan", [])
            
            # Handle both list and dict formats for meal_plan
            if isinstance(meals, dict):
                # Convert dict format from storage to list format for WeekPlanner
                meal_list = []
                for day_name, day_meals in meals.items():
                    if isinstance(day_meals, dict):
                        meal_list.append({
                            "day": day_name,
                            "breakfast": day_meals.get("breakfast", {}),
                            "lunch": day_meals.get("lunch", {}),
                            "dinner": day_meals.get("dinner", {})
                        })
                meals = meal_list
                logger.info(f"Converted dict format to list format for WeekPlanner")
            
            logger.info(f"Prepared {len(meals)} days of meal data for WeekPlanner")
            return {
                "meal_plan": meals,
                "summary": meal_plan_dict.get("summary", "Meal plan from MealPlanner")
            }
        
        # Fallback
        logger.warning(f"Unexpected meal plan format: {type(meal_plan_dict)}")
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
            logger.warning("No meal plan data provided to GroceryPlanner")
            return {}
        
        # Check if extraction failed
        if meal_plan_dict.get("status") == "no_meal_plan_extracted":
            logger.warning("Meal plan extraction failed, no grocery list available")
            return {}
        
        if isinstance(meal_plan_dict, dict) and "grocery_list" in meal_plan_dict:
            grocery_list = meal_plan_dict["grocery_list"]
            if grocery_list:
                total_items = sum(len(items) for items in grocery_list.values() if isinstance(items, list))
                logger.info(f"Extracted grocery list with {total_items} items for GroceryPlanner")
            else:
                logger.warning("Grocery list is empty")
            return grocery_list
        
        logger.warning("No grocery_list found in meal plan data")
        return {}
    
    def _extract_schedule(self, response) -> Dict:
        """Extract schedule from agent response."""
        return self._extract_meal_plan(response)  # Same pattern
    
    def _extract_shopping_list(self, response) -> Dict:
        """Extract shopping list from agent response."""
        return self._extract_meal_plan(response)  # Same pattern
    
    def _get_pantry_stock(self, family_id: str) -> Dict:
        """Get current pantry stock from storage with defaults."""
        try:
            pantry = self.storage.get_pantry(family_id)
            if pantry:
                return pantry
            
            # Provide basic pantry stock for new families
            default_pantry = {
                'grains': [{'item': 'rice', 'quantity': '2 kg', 'expiry_date': '2024-12-31'}],
                'spices': [{'item': 'salt', 'quantity': '500g', 'expiry_date': '2025-12-31'}],
                'oils': [{'item': 'cooking oil', 'quantity': '1L', 'expiry_date': '2025-06-30'}]
            }
            
            # Save default pantry for the family
            self.storage.update_pantry_inventory(family_id, default_pantry)
            return default_pantry
        except Exception as e:
            logger.error(f"Error getting pantry stock: {e}")
            return {}
    
    def _get_latest_family_plan(self, family_id: str) -> Dict:
        """Get the most recent meal plan for a family from storage."""
        try:
            conn = self.storage._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT meal_plan, shopping_list, week_start_date 
                FROM weekly_plans 
                WHERE family_id = ? 
                ORDER BY week_start_date DESC 
                LIMIT 1
            ''', (family_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                import json
                return {
                    'meal_plan': json.loads(row[0]) if row[0] else {},
                    'grocery_list': json.loads(row[1]) if row[1] else {},
                    'summary': f"Latest meal plan from {row[2]}"
                }
            return {}
        except Exception as e:
            logger.error(f"Error getting latest plan: {e}")
            return {}
    

    
    def _generate_summary(self, result: Dict) -> str:
        """Generate execution summary."""
        agents = ", ".join(result["agents_executed"])
        return f"Successfully executed {len(result['agents_executed'])} agents: {agents}"


# Create singleton instance
orchestrator = OrchestratorAgent()
orchestrator_agent = orchestrator  # Alias for consistency
