"""Test MealPlannerAgent with actual agent calls."""

import pytest
import asyncio
from agents.meal_planner import meal_planner_agent


class TestMealPlannerAgent:
    """Test MealPlannerAgent with real agent execution."""
    
    @pytest.mark.asyncio
    async def test_plan_simple_dinner(self):
        """Test planning a single dinner meal."""
        result = await meal_planner_agent.plan_meals(
            family_id="test_family_001",
            request="Plan dinner for tonight with vegetarian Indian meal",
            num_days=1
        )
        
        print("\n=== Test: Simple Dinner ===")
        print(f"Result: {result}")
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_plan_weekly_meals(self):
        """Test planning full week of meals."""
        result = await meal_planner_agent.plan_meals(
            family_id="test_family_002",
            request="Plan this week's meals with variety of Indian cuisine",
            num_days=7,
            dietary_restrictions=["vegetarian"],
            preferences={"cuisine": ["Indian", "Italian"]}
        )
        
        print("\n=== Test: Weekly Meal Plan ===")
        print(f"Result: {result}")
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_plan_with_restrictions(self):
        """Test planning with dietary restrictions."""
        result = await meal_planner_agent.plan_meals(
            family_id="test_family_003",
            request="Plan 3 days of meals for family with no onion, no garlic restrictions",
            num_days=3,
            dietary_restrictions=["no_onion", "no_garlic", "vegetarian"]
        )
        
        print("\n=== Test: With Dietary Restrictions ===")
        print(f"Result: {result}")
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_plan_special_occasion(self):
        """Test planning for special occasion."""
        result = await meal_planner_agent.plan_meals(
            family_id="test_family_004",
            request="Plan festive Diwali dinner for 15 people with traditional sweets",
            num_days=1,
            preferences={"occasion": "Diwali", "guests": 15}
        )
        
        print("\n=== Test: Special Occasion (Diwali) ===")
        print(f"Result: {result}")
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
