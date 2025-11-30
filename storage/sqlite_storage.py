import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from storage.base_storage import BaseStorage
from utils.logger import logger
from utils.config import Config

class SQLiteStorage(BaseStorage):
    
    def __init__(self, db_path: str = Config.SQLITE_DB_PATH):
        self.db_path = db_path
        self._initialize_database()
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def _initialize_database(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS families (
                family_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                member_count INTEGER,
                dietary_restrictions TEXT,
                preferences TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pantry (
                family_id TEXT,
                item TEXT,
                quantity TEXT,
                category TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (family_id, item),
                FOREIGN KEY (family_id) REFERENCES families(family_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_plans (
                plan_id TEXT PRIMARY KEY,
                family_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                week_start_date DATE,
                meal_plan TEXT,
                schedule TEXT,
                shopping_list TEXT,
                approved BOOLEAN DEFAULT 0,
                FOREIGN KEY (family_id) REFERENCES families(family_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meal_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id TEXT,
                meal_name TEXT,
                served_date DATE,
                liked BOOLEAN DEFAULT 1,
                FOREIGN KEY (family_id) REFERENCES families(family_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                schedule_id TEXT PRIMARY KEY,
                family_id TEXT,
                date DATE,
                time TEXT,
                activity TEXT,
                category TEXT,
                participants TEXT,
                duration_minutes INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (family_id) REFERENCES families(family_id)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pantry_family ON pantry(family_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plans_family ON weekly_plans(family_id, created_at DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_meals_family_date ON meal_history(family_id, served_date DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedules_family_date ON schedules(family_id, date)')
        
        conn.commit()
        conn.close()
        logger.info(f"SQLite database initialized at {self.db_path}")
    
    def get_family_profile(self, family_id: str) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM families WHERE family_id = ?', (family_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'family_id': row[0],
                'created_at': row[1],
                'member_count': row[2],
                'dietary_restrictions': json.loads(row[3]) if row[3] else [],
                'preferences': json.loads(row[4]) if row[4] else {}
            }
        return None
    
    def get_family(self, family_id: str) -> Optional[Dict]:
        """Alias for get_family_profile - returns complete family data."""
        return self.get_family_profile(family_id)
    
    def create_family(self, family_data: Dict) -> str:
        """Create a new family profile."""
        family_id = family_data.get('id', family_data.get('family_id'))
        
        profile = {
            'member_count': len(family_data.get('members', [])),
            'dietary_restrictions': family_data.get('dietary_restrictions', []),
            'preferences': {
                'name': family_data.get('name'),
                'members': family_data.get('members', []),
                'preferred_cuisines': family_data.get('preferred_cuisines', []),
                'allergies': family_data.get('allergies', []),
                'spice_level': family_data.get('spice_level', 'medium')
            }
        }
        
        success = self.save_family_profile(family_id, profile)
        return family_id if success else None
    
    def save_family_profile(self, family_id: str, profile: Dict) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO families 
                (family_id, member_count, dietary_restrictions, preferences)
                VALUES (?, ?, ?, ?)
            ''', (
                family_id,
                profile.get('member_count', 0),
                json.dumps(profile.get('dietary_restrictions', [])),
                json.dumps(profile.get('preferences', {}))
            ))
            conn.commit()
            logger.info(f"Saved family profile for {family_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving family profile: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_pantry_inventory(self, family_id: str) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT item, quantity, category FROM pantry WHERE family_id = ?', (family_id,))
        rows = cursor.fetchall()
        conn.close()
        
        inventory = {}
        for row in rows:
            inventory[row[0]] = {
                'quantity': row[1],
                'category': row[2]
            }
        return inventory
    
    def update_pantry_stock(self, family_id: str, updates: List[Dict]) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('BEGIN TRANSACTION')
            
            for update in updates:
                item = update['item']
                quantity = update['quantity']
                category = update.get('category', 'other')
                
                cursor.execute('''
                    INSERT OR REPLACE INTO pantry 
                    (family_id, item, quantity, category, last_updated)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (family_id, item, quantity, category))
            
            conn.commit()
            logger.info(f"Updated {len(updates)} pantry items for {family_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating pantry: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def save_weekly_plan(self, family_id: str, plan_data: Dict) -> str:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        plan_id = f"{family_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            cursor.execute('BEGIN TRANSACTION')
            
            cursor.execute('''
                INSERT INTO weekly_plans 
                (plan_id, family_id, week_start_date, meal_plan, schedule, shopping_list, approved)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                plan_id,
                family_id,
                plan_data.get('week_start_date'),
                json.dumps(plan_data.get('meal_plan', {})),
                json.dumps(plan_data.get('schedule', {})),
                json.dumps(plan_data.get('shopping_list', {})),
                plan_data.get('approved', True)
            ))
            
            for day, meals in plan_data.get('meal_plan', {}).items():
                for meal_type, meal_data in meals.items():
                    cursor.execute('''
                        INSERT INTO meal_history (family_id, meal_name, served_date)
                        VALUES (?, ?, ?)
                    ''', (family_id, meal_data.get('meal_name', ''), day))
            
            conn.commit()
            logger.info(f"Saved weekly plan {plan_id}")
            return plan_id
        except Exception as e:
            logger.error(f"Error saving weekly plan: {e}")
            conn.rollback()
            return ""
        finally:
            conn.close()
    
    def get_past_meal_plans(self, family_id: str, weeks: int = 4) -> List[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(weeks=weeks)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT DISTINCT meal_name FROM meal_history 
            WHERE family_id = ? AND served_date >= ?
            ORDER BY served_date DESC
        ''', (family_id, cutoff_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows if row[0]]
    
    def get_pantry(self, family_id: str) -> Dict:
        """Alias for get_pantry_inventory - returns pantry stock."""
        return self.get_pantry_inventory(family_id)
    
    def create_schedule(self, schedule_item: Dict) -> str:
        """Create a scheduled activity item.
        
        Args:
            schedule_item: {
                'family_id': str,
                'date': str,
                'time': str,
                'activity': str,
                'category': str,
                'participants': List[str],
                'duration_minutes': int
            }
        
        Returns:
            schedule_id: Unique identifier
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            schedule_id = f"schedule_{schedule_item['family_id']}_{schedule_item['date']}_{schedule_item['time']}"
            
            cursor.execute('''
                INSERT OR REPLACE INTO schedules 
                (schedule_id, family_id, date, time, activity, category, participants, duration_minutes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                schedule_id,
                schedule_item['family_id'],
                schedule_item['date'],
                schedule_item['time'],
                schedule_item['activity'],
                schedule_item['category'],
                ','.join(schedule_item.get('participants', [])),
                schedule_item.get('duration_minutes', 60),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            return schedule_id
        except Exception as e:
            logger.error(f"Error creating schedule: {str(e)}")
            conn.rollback()
            return ""
        finally:
            conn.close()
    

