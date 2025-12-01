"""Test MealPlanner with specific input."""

import asyncio
import sys
sys.path.insert(0, '.')

from agents.meal_planner import meal_planner_agent
from storage.sqlite_storage import SQLiteStorage


def check_saved_meal_plan(family_id="sharma_001"):
    """Check what was saved to database."""
    try:
        storage = SQLiteStorage()
        conn = storage._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT plan_id, meal_plan, created_at 
            FROM weekly_plans 
            WHERE family_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (family_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            plan_id, meal_plan_json, created_at = row
            print(f"\nSaved Plan ID: {plan_id}")
            print(f"Created: {created_at}")
            
            if meal_plan_json:
                import json
                meal_plan = json.loads(meal_plan_json)
                print(f"\nStored Meal Plan:")
                
                meals_found = 0
                for day, meals in meal_plan.items():
                    if isinstance(meals, dict):
                        for meal_type, meal_data in meals.items():
                            if meal_data and meal_data.get('meal_name'):
                                meals_found += 1
                                name = meal_data['meal_name']
                                time = f" ({meal_data['prep_time_minutes']}m)" if meal_data.get('prep_time_minutes') else ""
                                print(f"  {day} {meal_type}: {name}{time}")
                
                if meals_found == 0:
                    print("  No meals found in stored data")
                else:
                    print(f"\nTotal meals stored: {meals_found}")
                    return True
            else:
                print("No meal plan data saved")
                return False
        else:
            print("No meal plan found in database")
            return False
    except Exception as e:
        print(f"Database error: {e}")
        return False


async def test_meal_planner():
    """Test meal planner with the specified request."""
    
    print("Testing MealPlanner Agent")
    print("=" * 70)
    
    # Ensure family data exists
    storage = SQLiteStorage()
    sharma_family = {
        'id': 'sharma_001',
        'name': 'Sharma Family',
        'members': [
            {'name': 'Rajesh', 'age': 38, 'role': 'father'},
            {'name': 'Priya', 'age': 35, 'role': 'mother'},
            {'name': 'Aarav', 'age': 10, 'role': 'son'},
            {'name': 'Ananya', 'age': 7, 'role': 'daughter'}
        ],
        'dietary_restrictions': ['vegetarian'],
        'preferred_cuisines': ['North Indian', 'South Indian', 'Gujarati'],
        'allergies': [],
        'spice_level': 'medium'
    }
    
    try:
        storage.create_family(sharma_family)
        print("Sharma family data loaded")
    except:
        print("Sharma family already exists")
    
    # Test the meal planner
    print("\nRequest: Easy meals for Monday and Tuesday")
    print("Calling MealPlanner Agent...")
    
    try:
        response = await meal_planner_agent.plan_meals(
            family_id="sharma_001",
            request="Plan easy and quick meals for Monday and Tuesday - breakfast, lunch and dinner"
        )
        
        print(f"\nAgent completed with {len(response)} events")
        
        # Check what was saved to database
        if check_saved_meal_plan():
            print("\n✅ SUCCESS: Meal plan generated and saved correctly!")
        else:
            print("\n❌ ISSUE: No proper meal plan was saved")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        if "quota" in str(e).lower():
            print("Rate limit exceeded - wait and try again")


if __name__ == "__main__":
    asyncio.run(test_meal_planner())
