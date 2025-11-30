from collections import defaultdict
from typing import Dict, List
from utils.validators import parse_quantity, format_quantity
from tools.recipe_tools import categorize_ingredient

def aggregate_ingredients(meal_plan: Dict) -> Dict[str, Dict]:
    """Aggregate ingredients across all meals"""
    aggregated = defaultdict(float)
    categories = {}
    
    for day, meals in meal_plan.items():
        for meal_type, meal_data in meals.items():
            ingredients = meal_data.get('ingredients', [])
            
            for ing in ingredients:
                if isinstance(ing, dict):
                    item = ing.get('item', '')
                    quantity = ing.get('quantity', '0')
                    category = ing.get('category', categorize_ingredient(item))
                else:
                    continue
                
                if item:
                    aggregated[item] += parse_quantity(quantity)
                    categories[item] = category
    
    result = {}
    for item, qty in aggregated.items():
        result[item] = {
            'quantity': format_quantity(qty, 'g'),
            'category': categories.get(item, 'other')
        }
    
    return result

def create_shopping_list(aggregated_ingredients: Dict, pantry_inventory: Dict) -> Dict:
    """Create shopping list by removing items already in stock"""
    shopping_items = defaultdict(list)
    items_in_stock = []
    stock_updates = []
    
    for item, data in aggregated_ingredients.items():
        required_qty = data['quantity']
        category = data['category']
        
        pantry_item = pantry_inventory.get(item, {})
        if isinstance(pantry_item, dict):
            current_qty = pantry_item.get('quantity', '0')
        else:
            current_qty = str(pantry_item)
        
        current_value = parse_quantity(current_qty)
        required_value = parse_quantity(required_qty)
        
        if current_value >= required_value:
            items_in_stock.append(item)
            stock_updates.append({
                'item': item,
                'deduct': required_qty
            })
        else:
            shopping_items[category].append({
                'item': item,
                'quantity': required_qty
            })
    
    return {
        'items_by_category': dict(shopping_items),
        'items_in_stock': items_in_stock,
        'stock_updates': stock_updates,
        'total_items': sum(len(items) for items in shopping_items.values())
    }
