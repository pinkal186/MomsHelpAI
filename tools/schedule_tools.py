from datetime import datetime, timedelta
from typing import Dict, List
from utils.config import Config

def merge_meal_and_activity_schedules(meals_schedule: Dict, activities_schedule: Dict) -> Dict:
    """Merge meal and activity schedules into unified weekly schedule"""
    merged = {}
    
    all_days = set(list(meals_schedule.keys()) + list(activities_schedule.keys()))
    
    for day in all_days:
        day_schedule = {}
        
        if day in meals_schedule:
            day_schedule.update(meals_schedule[day])
        
        if day in activities_schedule:
            for time, activity in activities_schedule[day].items():
                if time in day_schedule:
                    new_time = shift_time(time, 30)
                    day_schedule[new_time] = day_schedule[time]
                day_schedule[time] = activity
        
        merged[day] = dict(sorted(day_schedule.items()))
    
    return merged

def shift_time(time_str: str, minutes: int) -> str:
    """Shift time by given minutes"""
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
        new_time = time_obj + timedelta(minutes=minutes)
        return new_time.strftime("%H:%M")
    except:
        return time_str

def format_schedule_for_display(schedule: Dict) -> str:
    """Format schedule into readable text"""
    output = []
    
    for day, events in schedule.items():
        output.append(f"\n{day}:")
        for time, event in events.items():
            output.append(f"  {time} - {event}")
    
    return '\n'.join(output)

def create_meal_schedule_from_plan(meal_plan: Dict) -> Dict:
    """Convert meal plan to time-based schedule"""
    schedule = {}
    
    for day, meals in meal_plan.items():
        day_schedule = {}
        
        for meal_type, meal_data in meals.items():
            time = Config.MEAL_TIMES.get(meal_type, '12:00')
            meal_name = meal_data.get('meal_name', meal_type)
            day_schedule[time] = f"{meal_type.title()} - {meal_name}"
        
        schedule[day] = day_schedule
    
    return schedule
