from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class GroceryItem:
    item: str
    quantity: str
    category: str = "other"
    
    def to_dict(self) -> Dict:
        return {
            'item': self.item,
            'quantity': self.quantity,
            'category': self.category
        }

@dataclass
class ShoppingList:
    items_by_category: Dict[str, List[GroceryItem]]
    total_items: int = 0
    items_in_stock: List[str] = field(default_factory=list)
    stock_updates: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        if self.total_items == 0:
            self.total_items = sum(
                len(items) for items in self.items_by_category.values()
            )
    
    def to_dict(self) -> Dict:
        return {
            'shopping_list': {
                category: [item.to_dict() for item in items]
                for category, items in self.items_by_category.items()
            },
            'total_items': self.total_items,
            'items_already_in_stock': self.items_in_stock,
            'stock_update_required': self.stock_updates
        }
