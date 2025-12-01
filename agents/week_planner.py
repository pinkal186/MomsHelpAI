"""Week Planner Agent - Schedules weekly activities using Google ADK."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from storage.sqlite_storage import SQLiteStorage
from utils.logger import setup_logger
from google.adk.tools import FunctionTool
import json

logger = setup_logger(__name__)


def get_activity_suggestions(family_id: str) -> Dict[str, Any]:
    """Get activity suggestions from family's specific activities in sample_family_data.json."""
    try:
        with open('data/sample_family_data.json', 'r', encoding='utf-8') as f:
            family_data = json.load(f)
        
        # Find the family by ID
        target_family = None
        for family_key, family_info in family_data.items():
            if family_info.get('family_id') == family_id:
                target_family = family_info
                break
        
        if not target_family:
            return {"status": "error", "error_message": f"Family with ID {family_id} not found"}
        
        # Get kids activities from the family data
        kids_activities = target_family.get('kids_activities', {})
        
        if not kids_activities:
            return {"status": "error", "error_message": "No kids activities found for this family"}
        
        # Convert to the expected format
        all_activities = []
        for child_name, activities in kids_activities.items():
            for activity in activities:
                all_activities.append({
                    "id": f"{family_id}_{child_name}_{activity['name']}",
                    "name": activity['name'],
                    "category": activity['category'],
                    "participant": child_name,
                    "schedule": activity['schedule'],
                    "duration_minutes": activity.get('duration_minutes', 60),
                    "location": activity.get('location', 'Local Area')
                })
        
        logger.info(f"Found {len(all_activities)} activities for family {family_id}")
        return {"status": "success", "activities": all_activities}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "error", "error_message": str(e)}


def save_schedule_item(family_id: str, date: str, time: str, activity: str, category: str, participants: List[str], duration_minutes: int = 60) -> Dict[str, Any]:
    """Save scheduled activity to database."""
    try:
        storage = SQLiteStorage()
        schedule_item = {
            'family_id': family_id, 'date': date, 'time': time,
            'activity': activity, 'category': category,
            'participants': participants, 'duration_minutes': duration_minutes
        }
        schedule_id = storage.create_schedule(schedule_item)
        logger.info(f"Saved schedule {schedule_id}")
        return {"status": "success", "schedule_id": schedule_id}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "error", "error_message": str(e)}


class WeekPlannerAgent(BaseAgent):
    """Weekly activity scheduling agent using Google ADK."""
    
    def __init__(self):
        instruction = """You plan weekly family schedules using activity database.

Input (per architecture):
{
  "week_start_date": "2025-12-02",
  "meal_plan": {"Monday": {"breakfast": {...}, "lunch": {...}, "dinner": {...}}, ...},
  "kids_activities_db": [{"activity": "Soccer", "days": ["Monday"], "time": "16:00"}]
}

Output (per architecture):
{
  "weekly_schedule": {
    "Monday": {"date": "2025-12-02", "meals": {...}, "activities": ["Soccer 16:00"], "notes": "..."},
    ...
  },
  "weekly_summary": {"total_meals": 21, "total_activities": 5, "busy_days": [...]}
}

Tools: get_activity_suggestions, save_schedule_item"""
        
        tools = [
            FunctionTool(get_activity_suggestions),
            FunctionTool(save_schedule_item)
        ]
        
        super().__init__(
            name="WeekPlannerAgent",
            instruction=instruction,
            tools=tools,
            model="gemini-2.5-flash-lite",
            output_key="weekly_schedule"
        )
        logger.info("WeekPlannerAgent initialized")
    
    async def plan_week(self, family_id: str, start_date: str, meal_plan_data: Dict = None) -> Any:
        """Plan weekly schedule with meals and activities.
        
        Input meal_plan_data structure:
        {
          "meal_plan": [{"day": "Monday", "breakfast": {"meal_name": "...", "prep_time_minutes": 15, ...}, ...}],
          "summary": "..."
        }
        """
        if not meal_plan_data:
            meal_plan_data = {"meal_plan": [], "summary": "No meal plan"}
        
        import json
        meal_plan_json = json.dumps(meal_plan_data, indent=2)
        
        query = f"""Create weekly schedule for family {family_id} starting {start_date}.

=== STRUCTURED MEAL PLAN DATA ===
{meal_plan_json}
=== END DATA ===

Task:
1. Use 'get_activity_suggestions' to get femily activities based on meal times and free slots
2. Create daily time-based schedule for 7 days:
   - Extract meal times and prep_time_minutes from the data above
   - Schedule: Breakfast (08:00), Lunch (13:00), Dinner (19:00)
   - Add cooking time slots BEFORE meals based on prep_time_minutes
   - Add activities from get_activity_suggestions
3. Use 'save_schedule_item' to save each activity
4. Return JSON:
{{
  "weekly_schedule": {{
    "Monday": {{
      "date": "{start_date}",
      "timeline": [
        {{"time": "07:45", "activity": "Cook Breakfast", "duration_min": 15}},
        {{"time": "08:00", "activity": "Breakfast - Poha", "duration_min": 30}},
        ...
      ]
    }},
    ...
  }},
  "weekly_summary": {{"total_meals": 21, "total_activities": 5}}
  "agent_suggation":{ "your suggation by seing all data, what woud be good or not, what is better way to handle with mininal text,and practicle advice"}
}}

Return ONLY valid JSON!"""
        
        return await self.run_debug(query)


week_planner_agent = WeekPlannerAgent()
