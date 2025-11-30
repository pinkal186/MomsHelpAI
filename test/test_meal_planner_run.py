"""Test MealPlanner with specific input."""

import asyncio
import sys
sys.path.insert(0, '.')

from agents.meal_planner import meal_planner_agent
from storage.sqlite_storage import SQLiteStorage


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
        print("Sharma family data loaded\n")
    except:
        print("Sharma family already exists\n")
    
    # Test the meal planner
    print("📝 Request: Suggest easy and fast recepi for monday and tuesday,")
    print("           keep break on wednesday, thursday if not activity and")
    print("           have time then heavy meal.\n")
    print("Calling MealPlanner Agent...\n")
    
    try:
        response = await meal_planner_agent.plan_meals(
            family_id="sharma_001",
            request="Suggest easy and fast recepi for monday and tuesday, keep break on wednesday, thursday if not activity and have time then heavy meal.",
            num_days=7
        )
        
        print("=" * 70)
        print("AGENT RESPONSE:")
        print("=" * 70)
        
        # Extract the final text response from events
        if isinstance(response, list):
            # Find the last event with text content
            for event in reversed(response):
                if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            print(part.text)
                            break
                    else:
                        continue
                    break
            else:
                print("No text response found in events")
                print(f"\nLast event: {response[-1] if response else 'No events'}")
        elif hasattr(response, 'text'):
            print(response.text)
        else:
            print(response)
        
        print("\n" + "=" * 70)
        print("Test completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print("=" * 70)
        print("ERROR:")
        print("=" * 70)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_meal_planner())
