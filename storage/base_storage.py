from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class BaseStorage(ABC):
    
    @abstractmethod
    def get_family_profile(self, family_id: str) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def save_family_profile(self, family_id: str, profile: Dict) -> bool:
        pass
    
    @abstractmethod
    def get_pantry_inventory(self, family_id: str) -> Dict:
        pass
    
    @abstractmethod
    def update_pantry_stock(self, family_id: str, updates: List[Dict]) -> bool:
        pass
    
    @abstractmethod
    def save_weekly_plan(self, family_id: str, plan_data: Dict) -> str:
        pass
    
    @abstractmethod
    def get_past_meal_plans(self, family_id: str, weeks: int = 4) -> List[str]:
        pass
