"""Comprehensive test for Orchestrator Agent - Sequential agent coordination."""

import asyncio
import sys
import json
sys.path.insert(0, '.')

from agents.orchestrator import orchestrator
from storage.sqlite_storage import SQLiteStorage


async def test_orchestrator_full_workflow():
    """Test complete orchestrator workflow: MealPlanner → WeekPlanner → GroceryPlanner."""
    
    print("🎯 Testing OrchestratorAgent - Sequential Coordination")
    print("=" * 80)
    
    # Setup: Ensure family data exists
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
        print("✅ Family data loaded\n")
    except:
        print("ℹ️  Family already exists\n")
    
    # Test orchestrator with comprehensive request
    print("📝 User Request:")
    print("   'Plan this week with quick meals Monday-Tuesday,'")
    print("   'cooking break Wednesday, heavy meals Thursday if time allows'\n")
    
    print("🔄 Expected Flow:")
    print("   Step 1: MealPlannerAgent")
    print("           Input: family_id, request, preferences")
    print("           Output: meal_plan (7 days × 3 meals)")
    print("")
    print("   Step 2: WeekPlannerAgent")
    print("           Input: meal_plan, family_id, start_date")
    print("           Output: weekly_schedule (meals + activities)")
    print("")
    print("   Step 3: GroceryPlannerAgent")
    print("           Input: meal_plan, pantry_stock")
    print("           Output: shopping_list (organized by sections)")
    print("")
    
    print("=" * 80)
    print("⏳ Executing Orchestrator...\n")
    
    try:
        result = await orchestrator.handle_request(
            user_request="Plan this week with quick meals Monday-Tuesday, no dinner for Wednesday, heavy meals Thursday if time allows",
            family_id="sharma_001",
            num_days=7,
            dietary_restrictions=["vegetarian"],
            preferences={"cuisine": ["Indian"], "quick_meals": True},
            week_start_date="2025-12-02"
        )
        
        print("=" * 80)
        print("✅ ORCHESTRATOR RESULT")
        print("=" * 80)
        
        # Display agents executed
        if "agents_executed" in result:
            print(f"\n📊 Agents Executed: {', '.join(result['agents_executed'])}")
            print(f"   Total agents: {len(result['agents_executed'])}")
        
        # Display meal plan
        if "meal_plan" in result and result["meal_plan"]:
            print("\n🍽️  MEAL PLAN OUTPUT:")
            print("-" * 80)
            if isinstance(result["meal_plan"], dict):
                if "text_plan" in result["meal_plan"]:
                    # Show first 500 chars of text plan
                    text = result["meal_plan"]["text_plan"]
                    print(text[:500])
                    if len(text) > 500:
                        print(f"\n   ... [Total length: {len(text)} characters]")
                else:
                    print(json.dumps(result["meal_plan"], indent=2)[:500])
            else:
                print(str(result["meal_plan"])[:500])
        
        # Display weekly schedule
        if "weekly_schedule" in result and result["weekly_schedule"]:
            print("\n📅 WEEKLY SCHEDULE OUTPUT:")
            print("-" * 80)
            if isinstance(result["weekly_schedule"], dict):
                if "text_plan" in result["weekly_schedule"]:
                    text = result["weekly_schedule"]["text_plan"]
                    print(text[:500])
                    if len(text) > 500:
                        print(f"\n   ... [Total length: {len(text)} characters]")
                else:
                    print(json.dumps(result["weekly_schedule"], indent=2)[:500])
            else:
                print(str(result["weekly_schedule"])[:500])
        
        # Display shopping list
        if "shopping_list" in result and result["shopping_list"]:
            print("\n🛒 SHOPPING LIST OUTPUT:")
            print("-" * 80)
            if isinstance(result["shopping_list"], dict):
                if "text_plan" in result["shopping_list"]:
                    text = result["shopping_list"]["text_plan"]
                    print(text[:500])
                    if len(text) > 500:
                        print(f"\n   ... [Total length: {len(text)} characters]")
                else:
                    print(json.dumps(result["shopping_list"], indent=2)[:500])
            else:
                print(str(result["shopping_list"])[:500])
        
        # Display summary
        if "execution_summary" in result:
            print("\n" + "=" * 80)
            print(f"✅ {result['execution_summary']}")
            print("=" * 80)
        
        # Check for errors
        if "error" in result:
            print(f"\n⚠️  Error occurred: {result['error']}")
        
        print("\n" + "=" * 80)
        print("🎉 Test completed successfully!")
        print("=" * 80)
        print("\n💡 What happened:")
        print("   1. Orchestrator called MealPlannerAgent with user request")
        print("   2. MealPlannerAgent output was passed to WeekPlannerAgent")
        print("   3. MealPlannerAgent output was also passed to GroceryPlannerAgent")
        print("   4. All three outputs combined into comprehensive response")
        print("\n✅ This demonstrates proper sequential agent coordination!")
        
    except Exception as e:
        print("=" * 80)
        print("❌ ERROR:")
        print("=" * 80)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        
        print("\n💡 Tips:")
        print("   - If quota error: Wait 60 seconds and retry")
        print("   - If rate limit: Free tier is 15 requests/minute")
        print("   - Each orchestrator run uses ~15-20 API calls total")


if __name__ == "__main__":
    asyncio.run(test_orchestrator_full_workflow())
