import chromadb
from chromadb.config import Settings
from typing import List, Dict
from utils.logger import logger
from utils.config import Config

class ChromaStorage:
    
    def __init__(self, persist_directory: str = Config.CHROMA_PERSIST_DIRECTORY):
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        self.collection = self.client.get_or_create_collection(
            name="family_preferences"
        )
        logger.info(f"ChromaDB initialized at {persist_directory}")
    
    def add_meal_preferences(self, family_id: str, meals: List[Dict]):
        documents = []
        metadatas = []
        ids = []
        
        for idx, meal in enumerate(meals):
            meal_name = meal.get('meal_name', '')
            if meal_name:
                documents.append(meal_name)
                metadatas.append({
                    'family_id': family_id,
                    'liked': meal.get('liked', True),
                    'meal_type': meal.get('meal_type', 'dinner')
                })
                ids.append(f"{family_id}_meal_{idx}_{meal_name.replace(' ', '_')}")
        
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} meals to ChromaDB for {family_id}")
    
    def search_similar_meals(self, query: str, family_id: str = None, n_results: int = 5) -> List[str]:
        where_clause = {'family_id': family_id} if family_id else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        
        if results and results['documents']:
            return results['documents'][0]
        return []
