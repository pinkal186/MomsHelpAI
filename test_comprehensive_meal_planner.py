#!/usr/bin/env python3
"""Comprehensive test for MealPlanner Agent - Check output format and DB storage."""

import asyncio
import sys
import json
sys.path.insert(0, '.')

from agents.meal_planner import meal_planner_agent
from storage.sqlite_storage import SQLiteStorage


def check_database_storage(family_id="sharma_001"):
    """Check what was actually saved to database."""
    print("\n" + "="*60)
    print("DATABASE STORAGE CHECK:")
    print("="*60)
    
    try:
        storage = SQLiteStorage()
        conn = storage._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT plan_id, meal_plan, shopping_list, created_at 
            FROM weekly_plans 
            WHERE family_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (family_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            plan_id, meal_plan_json, shopping_list_json, created_at = row
            print(f"✓ Found Plan ID: {plan_id}")
            print(f"✓ Created: {created_at}")
            
            if meal_plan_json and meal_plan_json.strip():
                try:
                    meal_plan = json.loads(meal_plan_json)
                    print(f"✓ Meal Plan Data Type: {type(meal_plan)}")
                    print(f"✓ Meal Plan Keys: {list(meal_plan.keys()) if isinstance(meal_plan, dict) else 'Not a dict'}")
                    
                    if isinstance(meal_plan, dict):
                        meals_found = 0
                        for day, meals in meal_plan.items():
                            if isinstance(meals, dict):
                                for meal_type, meal_data in meals.items():
                                    if meal_data and isinstance(meal_data, dict) and meal_data.get('meal_name'):
                                        meals_found += 1
                                        print(f"  ✓ {day} {meal_type}: {meal_data['meal_name']}")
                        
                        if meals_found == 0:
                            print("  ✗ NO ACTUAL MEALS FOUND IN DATA")
                            print(f"  Raw data: {meal_plan}")
                        else:
                            print(f"  ✓ Total meals found: {meals_found}")
                    else:
                        print(f"  ✗ Meal plan is not a dictionary: {meal_plan}")
                        
                except json.JSONDecodeError as e:
                    print(f"  ✗ JSON decode error: {e}")
                    print(f"  Raw data: {meal_plan_json[:200]}...")
            else:
                print("  ✗ No meal plan data saved (empty or null)")
            
            if shopping_list_json and shopping_list_json.strip():
                try:
                    shopping_list = json.loads(shopping_list_json)
                    print(f"✓ Shopping List: {type(shopping_list)}")
                except:
                    print("✗ Shopping list parse error")
            else:
                print("✗ No shopping list saved")
                
        else:
            print("✗ NO MEAL PLAN FOUND IN DATABASE")
            
            # Check if any plans exist for any family
            conn = storage._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM weekly_plans')
            count = cursor.fetchone()[0]
            conn.close()
            print(f"  Total plans in DB: {count}")
            
    except Exception as e:
        print(f"✗ Database error: {e}")
        import traceback
        traceback.print_exc()


async def test_simple_request():
    """Test with a simple, clear request."""
    print("="*60)
    print("TEST 1: Simple Dinner Request")
    print("="*60)
    
    try:
        response = await meal_planner_agent.plan_meals(
            family_id="sharma_001",
            request="Plan dinner for today - something quick and vegetarian"
        )
        
        print(f"Response type: {type(response)}")
        print(f"Response length: {len(response) if isinstance(response, list) else 'Not a list'}")
        
        # Check final text response
        final_text = None
        if isinstance(response, list):
            for event in reversed(response):
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                final_text = part.text.strip()
                                break
                        if final_text:
                            break
        
        print(f"Final response: {final_text[:300] if final_text else 'None'}...")
        
        # Check if it looks like JSON
        if final_text and final_text.startswith('{'):
            try:
                json_data = json.loads(final_text)
                print("✓ Valid JSON response")
                print(f"  Keys: {list(json_data.keys())}")
                if 'meal_plan' in json_data:
                    print(f"  Meal plan type: {type(json_data['meal_plan'])}")
            except:
                print("✗ Invalid JSON in response")
        else:
            print("✗ Response is not JSON format")
            
        # Check database
        check_database_storage()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_week_request():
    """Test with a full week request."""
    print("\n" + "="*60)
    print("TEST 2: Full Week Request")
    print("="*60)
    
    try:
        response = await meal_planner_agent.plan_meals(
            family_id="sharma_001",
            request="Plan meals for this week - all meals for 7 days, vegetarian, Indian cuisine"
        )
        
        print(f"Response type: {type(response)}")
        
        # Check final response
        final_text = None
        if isinstance(response, list):
            for event in reversed(response):
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                final_text = part.text.strip()
                                break
                        if final_text:
                            break
        
        print(f"Final response length: {len(final_text) if final_text else 0}")
        
        if final_text and final_text.startswith('{'):
            try:
                json_data = json.loads(final_text)
                print("✓ Valid JSON response")
                if 'meal_plan' in json_data:
                    meal_plan = json_data['meal_plan']
                    if isinstance(meal_plan, list):
                        print(f"  Meal plan days: {len(meal_plan)}")
                        for day_plan in meal_plan:
                            if isinstance(day_plan, dict):
                                day = day_plan.get('day', 'Unknown')
                                meals = [k for k in ['breakfast', 'lunch', 'dinner'] if day_plan.get(k)]
                                print(f"    {day}: {meals}")
                    else:
                        print(f"  Meal plan type: {type(meal_plan)}")
            except Exception as e:
                print(f"✗ JSON parse error: {e}")
        
        # Check database
        check_database_storage()
        
    except Exception as e:
        print(f"✗ Error: {e}")


async def main():
    """Run comprehensive tests."""
    print("COMPREHENSIVE MEAL PLANNER TEST")
    print("="*60)
    
    # Setup family data
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
        print("✓ Family data setup complete")
    except:
        print("✓ Family already exists")
    
    # Run tests
    await test_simple_request()
    
    print("\n" + "="*60)
    print("Waiting 10 seconds before next test to avoid rate limits...")
    await asyncio.sleep(10)
    
    await test_week_request()
    
    print("\n" + "="*60)
    print("TEST SUMMARY:")
    print("="*60)
    print("1. Check if agent returns proper JSON meal plans")
    print("2. Check if meal plans are saved correctly to database")
    print("3. Verify data format matches expected structure")


if __name__ == "__main__":
    asyncio.run(main())