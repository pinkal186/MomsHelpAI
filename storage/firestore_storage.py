from google.cloud import firestore
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from storage.base_storage import BaseStorage
from utils.logger import logger

class FirestoreStorage(BaseStorage):
    
    def __init__(self):
        self.db = firestore.Client()
        logger.info("Firestore client initialized")
    
    def get_family_profile(self, family_id: str) -> Optional[Dict]:
        doc = self.db.collection('families').document(family_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def save_family_profile(self, family_id: str, profile: Dict) -> bool:
        try:
            self.db.collection('families').document(family_id).set(profile)
            logger.info(f"Saved family profile for {family_id} to Firestore")
            return True
        except Exception as e:
            logger.error(f"Error saving family profile to Firestore: {e}")
            return False
    
    def get_pantry_inventory(self, family_id: str) -> Dict:
        doc = self.db.collection('pantry').document(family_id).get()
        if doc.exists:
            return doc.to_dict()
        return {}
    
    def update_pantry_stock(self, family_id: str, updates: List[Dict]) -> bool:
        try:
            pantry_ref = self.db.collection('pantry').document(family_id)
            current_pantry = pantry_ref.get().to_dict() if pantry_ref.get().exists else {}
            
            for update in updates:
                item = update['item']
                current_pantry[item] = {
                    'quantity': update['quantity'],
                    'category': update.get('category', 'other'),
                    'last_updated': datetime.now()
                }
            
            pantry_ref.set(current_pantry)
            logger.info(f"Updated {len(updates)} pantry items for {family_id} in Firestore")
            return True
        except Exception as e:
            logger.error(f"Error updating pantry in Firestore: {e}")
            return False
    
    def save_weekly_plan(self, family_id: str, plan_data: Dict) -> str:
        plan_id = f"{family_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            plan_data['created_at'] = datetime.now()
            plan_data['family_id'] = family_id
            
            self.db.collection('weekly_plans').document(plan_id).set(plan_data)
            logger.info(f"Saved weekly plan {plan_id} to Firestore")
            return plan_id
        except Exception as e:
            logger.error(f"Error saving weekly plan to Firestore: {e}")
            return ""
    
    def get_past_meal_plans(self, family_id: str, weeks: int = 4) -> List[str]:
        cutoff_date = datetime.now() - timedelta(weeks=weeks)
        
        plans = self.db.collection('weekly_plans') \
            .where('family_id', '==', family_id) \
            .where('created_at', '>=', cutoff_date) \
            .stream()
        
        past_meals = []
        for plan in plans:
            data = plan.to_dict()
            meal_plan = data.get('meal_plan', {})
            for day, meals in meal_plan.items():
                for meal_type, meal_data in meals.items():
                    meal_name = meal_data.get('meal_name', '')
                    if meal_name:
                        past_meals.append(meal_name)
        
        return list(set(past_meals))
