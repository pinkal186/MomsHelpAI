"""Grocery Planner Agent - Creates shopping lists using Google ADK."""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from storage.sqlite_storage import SQLiteStorage
from utils.logger import setup_logger
from google.adk.tools import FunctionTool

logger = setup_logger(__name__)


def check_pantry_inventory(family_id: str, ingredients: List[str]) -> Dict[str, Any]:
    """Check pantry inventory against ingredient list."""
    try:
        storage = SQLiteStorage()
        pantry = storage.get_pantry(family_id)
        if not pantry:
            return {"status": "error", "error_message": "Pantry not found"}
        
        available = []
        needed = []
        for ingredient in ingredients:
            if ingredient in pantry:
                available.append(ingredient)
            else:
                needed.append(ingredient)
        
        return {"status": "success", "available": available, "needed": needed}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "error", "error_message": str(e)}


def consolidate_shopping_list(ingredients: List[str]) -> Dict[str, Any]:
    """Consolidate and merge duplicate ingredients."""
    try:
        # Simple consolidation - count occurrences
        from collections import Counter
        consolidated = Counter(ingredients)
        return {"status": "success", "consolidated": {k: str(v) for k, v in consolidated.items()}}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "error", "error_message": str(e)}


def organize_by_sections(ingredients: Dict[str, str]) -> Dict[str, Any]:
    """Organize shopping list by store sections."""
    try:
        from tools.recipe_tools import categorize_ingredient
        sections = {}
        for item, qty in ingredients.items():
            category = categorize_ingredient(item)
            if category not in sections:
                sections[category] = []
            sections[category].append({"item": item, "quantity": qty})
        return {"status": "success", "sections": sections}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "error", "error_message": str(e)}


def save_shopping_to_pantry(family_id: str, items: Dict[str, str]) -> Dict[str, Any]:
    """Save shopping items as pantry updates."""
    try:
        storage = SQLiteStorage()
        # Convert items dict to pantry update format
        updates = [{"item": item, "quantity": qty, "category": "groceries"} for item, qty in items.items()]
        success = storage.update_pantry_stock(family_id, updates)
        logger.info(f"Updated pantry with {len(items)} items")
        return {"status": "success", "items_added": len(items)}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "error", "error_message": str(e)}


class GroceryPlannerAgent(BaseAgent):
    """Grocery shopping list agent using Google ADK."""
    
    def __init__(self):
        instruction = """You create optimized grocery shopping lists from meal plans.

Input (per architecture):
{
  "meal_plan": {...},
  "current_pantry_stock": {"rice": {"quantity": "2 cups"}, ...}
}

Output (per architecture):
{
  "shopping_list": {
    "produce": [{"item": "tomatoes", "quantity": "6"}],
    "protein": [...], "dairy": [...], "grains": [...]
  },
  "total_items": 24,
  "items_already_in_stock": ["rice", "pasta"],
  "stock_update_required": [{"item": "rice", "deduct": "1 cup"}]
}

Tools: check_pantry, consolidate_shopping_list, organize_by_sections, save_shopping_to_pantry"""
        
        tools = [
            FunctionTool(check_pantry_inventory),
            FunctionTool(consolidate_shopping_list),
            FunctionTool(organize_by_sections),
            FunctionTool(save_shopping_to_pantry)
        ]
        
        super().__init__(name="GroceryPlannerAgent", instruction=instruction, tools=tools, model="gemini-2.5-flash-lite", output_key="grocery_list")
        logger.info("GroceryPlannerAgent initialized")
    
    async def create_shopping_list(self, family_id: str, grocery_list_data: Dict[str, Any], pantry_stock: Dict = None) -> Any:
        """Create shopping list from pre-extracted ingredients.
        
        Input grocery_list_data structure:
        {
          "vegetables": [{"item": "onions", "quantity": "1 kg"}],
          "grains": [{"item": "rice", "quantity": "2 kg"}],
          ...
        }
        """
        if not grocery_list_data:
            grocery_list_data = {}
        
        import json
        grocery_json = json.dumps(grocery_list_data, indent=2)
        pantry_info = json.dumps(pantry_stock, indent=2) if pantry_stock else "{}"
        
        query = f"""Create final shopping list for family {family_id}.

=== INGREDIENTS NEEDED (from meal plan) ===
{grocery_json}
=== END INGREDIENTS ===

=== CURRENT PANTRY STOCK ===
{pantry_info}
=== END PANTRY STOCK ===

Task:
1. Extract all items from ingredients list above
2. Use 'check_pantry_inventory' to check what's already in stock
3. Remove items that are in stock (or reduce quantities)
4. Use 'consolidate_shopping_list' to merge duplicates
5. Use 'organize_by_sections' to reorganize by store sections
6. Use 'save_shopping_to_pantry' to add shopping items to pantry
7. Return JSON:
{{
  "shopping_list": {{
    "produce": [{{"item": "tomatoes", "quantity": "6"}}],
    "grains": [...],
    "dairy": [...]
  }},
  "total_items": 24,
  "items_in_stock": ["rice", "oil"],
  "estimated_cost": "₹2000"
}}

Return ONLY valid JSON!"""
        
        return await self.run_debug(query)


grocery_planner_agent = GroceryPlannerAgent()
