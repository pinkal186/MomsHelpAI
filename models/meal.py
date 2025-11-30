from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Meal:
    meal_name: str
    recipe: str
    servings: int
    prep_time: str
    ingredients: List[Dict[str, str]] = field(default_factory=list)
    reference_link: str = ""
    refined_by_subagent: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'meal_name': self.meal_name,
            'recipe': self.recipe,
            'servings': self.servings,
            'prep_time': self.prep_time,
            'ingredients': self.ingredients,
            'reference_link': self.reference_link,
            'refined_by_subagent': self.refined_by_subagent
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Meal':
        return Meal(
            meal_name=data['meal_name'],
            recipe=data['recipe'],
            servings=data['servings'],
            prep_time=data['prep_time'],
            ingredients=data.get('ingredients', []),
            reference_link=data.get('reference_link', ''),
            refined_by_subagent=data.get('refined_by_subagent', False)
        )

@dataclass
class DayMeals:
    breakfast: Meal
    lunch: Meal
    dinner: Meal
    
    def to_dict(self) -> Dict:
        return {
            'breakfast': self.breakfast.to_dict(),
            'lunch': self.lunch.to_dict(),
            'dinner': self.dinner.to_dict()
        }

@dataclass
class MealPlan:
    meals: Dict[str, DayMeals]
    total_recipes: int = 0
    recipes_refined: int = 0
    
    def __post_init__(self):
        if self.total_recipes == 0:
            self.total_recipes = len(self.meals) * 3
    
    def to_dict(self) -> Dict:
        return {
            day: meals.to_dict() 
            for day, meals in self.meals.items()
        }
