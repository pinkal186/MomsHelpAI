import json
from typing import Dict, List
from utils.validators import parse_quantity

def extract_ingredients_from_recipe(recipe_text: str) -> List[Dict]:
    """Extract ingredients from recipe text - simple parser"""
    ingredients = []
    
    common_ingredients = {
        'rice': 'grains', 'wheat': 'grains', 'roti': 'grains',
        'dal': 'protein', 'chicken': 'protein', 'paneer': 'protein', 'egg': 'protein',
        'tomato': 'vegetables', 'onion': 'vegetables', 'potato': 'vegetables',
        'milk': 'dairy', 'curd': 'dairy', 'ghee': 'dairy',
        'oil': 'spices', 'masala': 'spices', 'turmeric': 'spices'
    }
    
    for ingredient, category in common_ingredients.items():
        if ingredient in recipe_text.lower():
            ingredients.append({
                'item': ingredient,
                'quantity': '200g',
                'category': category
            })
    
    return ingredients

def categorize_ingredient(ingredient_name: str) -> str:
    """Categorize ingredient into food groups"""
    categories_map = {
        'vegetables': ['tomato', 'onion', 'potato', 'carrot', 'peas', 'beans', 'spinach', 'cauliflower'],
        'grains': ['rice', 'wheat', 'flour', 'atta', 'roti', 'bread'],
        'protein': ['dal', 'chicken', 'fish', 'egg', 'paneer', 'tofu', 'rajma', 'chole'],
        'dairy': ['milk', 'curd', 'yogurt', 'cheese', 'ghee', 'butter'],
        'spices': ['masala', 'turmeric', 'cumin', 'coriander', 'chilli', 'garam'],
        'fruits': ['apple', 'banana', 'mango', 'orange', 'grapes']
    }
    
    ingredient_lower = ingredient_name.lower()
    for category, keywords in categories_map.items():
        if any(keyword in ingredient_lower for keyword in keywords):
            return category
    
    return 'other'
