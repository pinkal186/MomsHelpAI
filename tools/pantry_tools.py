from typing import Dict, Optional
from utils.validators import parse_quantity
from utils.logger import logger

def check_pantry(pantry_inventory: Dict, ingredient: str, required_qty: str) -> Dict:
    """Check if ingredient available in pantry with sufficient quantity"""
    current_stock = pantry_inventory.get(ingredient, {})
    current_qty = current_stock.get('quantity', '0') if isinstance(current_stock, dict) else current_stock
    
    current_value = parse_quantity(str(current_qty))
    required_value = parse_quantity(required_qty)
    
    available = current_value >= required_value if current_value > 0 else False
    
    return {
        'available': available,
        'current_stock': current_qty,
        'required': required_qty,
        'action': 'skip' if available else 'buy'
    }

def get_pantry_status(pantry_inventory: Dict) -> Dict:
    """Get pantry status summary"""
    total_items = len(pantry_inventory)
    categories = {}
    
    for item, data in pantry_inventory.items():
        if isinstance(data, dict):
            category = data.get('category', 'other')
        else:
            category = 'other'
        
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    return {
        'total_items': total_items,
        'by_category': categories
    }
