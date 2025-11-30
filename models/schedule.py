from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class DaySchedule:
    date: str
    meals: Dict[str, str]
    activities: List[str] = field(default_factory=list)
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'date': self.date,
            'meals': self.meals,
            'activities': self.activities,
            'notes': self.notes
        }

@dataclass
class WeeklySchedule:
    schedule: Dict[str, DaySchedule]
    weekly_summary: Dict[str, any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'schedule': {
                day: sched.to_dict() 
                for day, sched in self.schedule.items()
            },
            'weekly_summary': self.weekly_summary
        }
