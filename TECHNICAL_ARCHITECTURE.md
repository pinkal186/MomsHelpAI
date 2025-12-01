# MomsHelperAI - Technical Architecture Document

## 📋 Executive Summary

**Project Name:** MomsHelperAI - Intelligent Weekly Family Planner  
**Track:** Concierge Agents (Kaggle 5-Day AI Agents Capstone)  
**Framework:** Google ADK (Agent Development Kit) - ONLY  
**LLM:** Gemini 2.0 Flash  

---

## 🎯 1. Problem & Solution

### Problem
Busy mothers spend **14+ hours per week** on meal planning, grocery shopping, and weekly family coordination - leading to stress, food waste, and less family time.

### Solution  
**MomsHelperAI**: A multi-agent system built with **Google ADK** that automates weekly family planning through intelligent agent orchestration.

**Impact**: Reduce planning time from 14 hours to 4 hours per week (71% reduction)

---

## 🏗️ 2. Architecture Overview - Google ADK Multi-Agent System

### 2.1 Agent Hierarchy (Sequential Orchestration Pattern)

**Built exclusively with Google Agent Development Kit (ADK)**

**Orchestration Pattern**: Python-based Sequential Coordinator
- **NOT** LLM-as-Manager (no agent decides which agent to call)
- **NOT** Agent-as-Tool pattern (no sub-agents)
- **IS** Sequential execution: Orchestrator → MealPlanner → WeekPlanner → GroceryPlanner

```
USER REQUEST
     ↓
┌────────────────────────────────────────┐
│   ORCHESTRATOR (Python Coordinator)    │
│   - Sequential agent execution         │
│   - Powered by: Python logic           │
│   - Pattern: Sequential chaining       │
└──────────┬─────────────────────────────┘
           │
    ┌──────┴──────┬──────────────┐
    ↓             ↓              ↓
┌─────────┐  ┌─────────┐  ┌──────────────┐
│  MEAL   │  │  WEEK   │  │   GROCERY    │
│ PLANNER │  │ PLANNER │  │   PLANNER    │
│ AGENT   │  │ AGENT   │  │   AGENT      │
│ (JSON)  │  │         │  │              │
└─────────┘  └─────────┘  └──────────────┘
     │             │              │
     ↓             ↓              ↓
  (google_search) (schedules)  (pantry)
```

### 2.2 Agent Execution Flow & Data Dependencies

**Sequential Execution Order**:

```
1. USER REQUEST → Orchestrator.handle_request()
   ↓
2. Orchestrator → MealPlannerAgent.plan_meals()
   ├─ Calls: google_search tool
   ├─ Calls: check_pantry_inventory tool
   ├─ DB Read: storage.get_pantry(family_id)
   ├─ DB Write: storage.save_weekly_plan(meal_plan)
   └─ Returns: JSON {meal_plan: [...], grocery_list: {...}, summary: "..."}
   ↓
3. Orchestrator → WeekPlannerAgent.plan_week()
   ├─ Input: meal_plan_data (extracted from step 2)
   ├─ Calls: create_schedule tool
   ├─ DB Read: storage.get_family(family_id)
   ├─ DB Write: storage.create_schedule(schedule_item)
   └─ Returns: weekly_schedule JSON
   ↓
4. Orchestrator → GroceryPlannerAgent.create_shopping_list()
   ├─ Input: grocery_list_data (extracted from step 2) + pantry_stock
   ├─ Calls: check_pantry_inventory tool
   ├─ Calls: save_shopping_to_pantry tool
   ├─ DB Read: storage.get_pantry(family_id)
   ├─ DB Write: storage.update_pantry_stock(family_id, items)
   └─ Returns: shopping_list JSON
   ↓
5. Orchestrator → Combines all outputs
   └─ Returns: {meal_plan, weekly_schedule, shopping_list, execution_summary}
```

**Key Data Flow Rules**:
- ✅ MealPlanner outputs structured JSON with embedded `grocery_list`
- ✅ Orchestrator extracts `meal_plan` array for WeekPlanner
- ✅ Orchestrator extracts `grocery_list` for GroceryPlanner
- ✅ Each agent is independent (no agent calls another agent)
- ✅ Orchestrator manages all inter-agent communication

### 2.3 ADK Patterns Used (Kaggle Capstone Requirements)

| Pattern | Where Used | ADK Implementation |
|---------|------------|-------------------|
| **1. Sequential Agents** | Orchestrator → Meal → Week → Grocery | Python-based sequential chaining |
| **2. Tools Integration** | All agents use custom tools | `FunctionTool` wrapper pattern |
| **3. Structured Output** | MealPlanner outputs JSON format | JSON instruction + parsing |
| **4. LLM-powered Agent** | All 3 agents use Gemini 2.5 Flash Lite | `Agent` with `generate_content_stream` |
| **5. Database Integration** | SQLite for persistence | Direct storage method calls |

### 2.4 Agent → Method → Database Interaction Map

**Complete mapping of which agent calls which methods and accesses which database tables:**

| Agent | Tool Methods Used | Storage Methods Called | Database Tables Accessed | When Called |
|-------|------------------|----------------------|------------------------|-------------|
| **Orchestrator** | None (Python coordinator) | `get_pantry(family_id)` | `pantry` (read) | Before GroceryPlanner |
| | | `get_family(family_id)` | `families` (read) | Optional: get family data |
| **MealPlanner** | `google_search(query)` | `get_pantry_inventory(family_id)` | `pantry` (read) | Check available ingredients |
| | `check_pantry_inventory(family_id, ingredients)` | `save_weekly_plan(meal_plan)` | `weekly_plans` (write) | Save meal plan |
| | `save_meal_plan(family_id, plan)` | `get_past_meal_plans(family_id, weeks)` | `meal_history` (read) | Avoid repetition |
| | | | `weekly_plans` (write) | Store complete plan |
| **WeekPlanner** | `create_schedule(schedule_item)` | `get_family(family_id)` | `families` (read) | Get family info |
| | | `create_schedule(schedule_data)` | `schedules` (write) | Save schedule items |
| **GroceryPlanner** | `check_pantry_inventory(family_id, ingredients)` | `get_pantry(family_id)` | `pantry` (read) | Check stock |
| | `consolidate_shopping_list(ingredients)` | `update_pantry_stock(family_id, updates)` | `pantry` (write) | Add purchased items |
| | `organize_by_sections(ingredients)` | | | |
| | `save_shopping_to_pantry(family_id, items)` | | | |

**Database Schema (SQLite)**:

```sql
-- Table: families
CREATE TABLE families (
    family_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    member_count INTEGER,
    dietary_restrictions TEXT,  -- JSON array
    preferences TEXT             -- JSON object
);

-- Table: pantry
CREATE TABLE pantry (
    family_id TEXT,
    item TEXT,
    quantity TEXT,
    category TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (family_id, item),
    FOREIGN KEY (family_id) REFERENCES families(family_id)
);

-- Table: weekly_plans
CREATE TABLE weekly_plans (
    plan_id TEXT PRIMARY KEY,
    family_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    week_start_date DATE,
    meal_plan TEXT,      -- JSON
    schedule TEXT,       -- JSON
    shopping_list TEXT,  -- JSON
    approved BOOLEAN DEFAULT 0,
    FOREIGN KEY (family_id) REFERENCES families(family_id)
);

-- Table: meal_history
CREATE TABLE meal_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id TEXT,
    meal_name TEXT,
    served_date DATE,
    liked BOOLEAN DEFAULT 1,
    FOREIGN KEY (family_id) REFERENCES families(family_id)
);

-- Table: schedules
CREATE TABLE schedules (
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
);
```

**Data Flow Example**:

```python
# Step 1: Orchestrator calls MealPlanner
meal_response = await meal_planner_agent.plan_meals(
    family_id="sharma_001",
    request="Quick meals",
    num_days=7,
    dietary_restrictions=["vegetarian"],
    preferences={"cuisine": ["Indian"]}
)
# MealPlanner internally:
#   - Calls google_search("recipes")
#   - Calls storage.get_pantry_inventory("sharma_001") → reads pantry table
#   - Calls storage.save_weekly_plan({meal_plan: ...}) → writes weekly_plans table
#   - Returns JSON: {meal_plan: [...], grocery_list: {...}, summary: "..."}

# Step 2: Orchestrator extracts data and calls WeekPlanner
meal_plan_for_week = orchestrator._prepare_meal_plan_for_agents(meal_plan)
week_response = await week_planner_agent.plan_week(
    family_id="sharma_001",
    start_date="2025-12-02",
    meal_plan_data=meal_plan_for_week  # {meal_plan: [...], summary: "..."}
)
# WeekPlanner internally:
#   - Calls storage.get_family("sharma_001") → reads families table
#   - Calls storage.create_schedule({date, time, activity}) → writes schedules table
#   - Returns weekly_schedule JSON

# Step 3: Orchestrator extracts grocery data and calls GroceryPlanner
grocery_list_data = orchestrator._extract_grocery_list_from_meal_plan(meal_plan)
pantry_stock = storage.get_pantry("sharma_001")  # reads pantry table
grocery_response = await grocery_planner_agent.create_shopping_list(
    family_id="sharma_001",
    grocery_list_data=grocery_list_data,  # {vegetables: [...], grains: [...]}
    pantry_stock=pantry_stock
)
# GroceryPlanner internally:
#   - Calls check_pantry_inventory("sharma_001", [ingredients]) → reads pantry table
#   - Calls storage.update_pantry_stock("sharma_001", updates) → writes pantry table
#   - Returns shopping_list JSON
```

---

## 🤖 3. Agent Specifications

### 3.1 Orchestrator (Python Coordinator)

**Role**: Sequentially executes specialist agents and chains data between them  
**Framework**: Python class (NOT an LLM agent)  
**LLM**: None (uses Python logic for orchestration)  
**Pattern**: Sequential execution with explicit data passing  

**Input Format**:
```json
{
  "user_request": "Plan this week for my family",
  "family_id": "sharma_001",
  "num_days": 7,
  "dietary_restrictions": ["vegetarian"],
  "preferences": {"cuisine": ["Indian"], "quick_meals": true},
  "week_start_date": "2025-12-02"
}
```

**Output Format**:
```json
{
  "meal_plan": {"meal_plan": [...], "grocery_list": {...}, "summary": "..."},
  "weekly_schedule": {...},
  "shopping_list": {...},
  "agents_executed": ["MealPlanner", "WeekPlanner", "GroceryPlanner"],
  "execution_summary": "Successfully executed 3 agents: MealPlanner, WeekPlanner, GroceryPlanner"
}
```

**Human-in-the-Loop (HITL)**: After generating the complete plan, Orchestrator asks for user approval before finalizing.

**ADK Implementation**:
```python
from google import genai
from google.genai import types

orchestrator = genai.Agent(
    model="gemini-2.0-flash",
    system_instruction="""You are a family planning coordinator. 
    After generating the complete weekly plan, ALWAYS present it to the user and ask: 
    'Do you approve this plan? (yes/no/modify)'
    Wait for user response before finalizing.""",
    tools=[meal_planner_tool, week_planner_tool, grocery_planner_tool]
)

# HITL Workflow
def run_with_human_approval(user_request, session_id):
    # Generate complete plan
    response = orchestrator.send_message(user_request, session_id=session_id)
    
    print(response.text)  # Shows plan summary
    
    # HUMAN-IN-THE-LOOP: Simple approval
    user_input = input("\nApprove? (yes/no/modify): ").lower()
    
    if user_input == "yes":
        return response  # Plan approved
    elif user_input == "modify":
        modifications = input("What to change? ")
        # Send modifications back to orchestrator
        final_response = orchestrator.send_message(
            f"Modify the plan: {modifications}", 
            session_id=session_id
        )
        return final_response
    else:
        return "Plan rejected. Please start over."
```

---

### 3.2 Meal Planner Agent

**Role**: Generate weekly meal plans using Google Search with structured JSON output  
**Framework**: Google ADK `Agent` class  
**LLM**: Gemini 2.5 Flash Lite  
**Pattern**: Tool usage with structured JSON response  

**Tools (FunctionTool wrappers)**:
1. `google_search` - Built-in ADK tool for recipe search
2. `check_pantry_inventory(family_id, ingredients)` - Custom tool to check stock
3. `save_meal_plan(family_id, plan)` - Saves meal plan to database

**Storage Methods Called**:
- `storage.get_pantry_inventory(family_id)` → Reads `pantry` table
- `storage.get_past_meal_plans(family_id, weeks)` → Reads `meal_history` table
- `storage.save_weekly_plan(plan_data)` → Writes `weekly_plans` table

**Database Tables Used**:
- `pantry` (READ) - Check available ingredients
- `meal_history` (READ) - Avoid repeating recent meals
- `weekly_plans` (WRITE) - Save generated meal plan

**Input Format**:
```json
{
  "num_days": 7,
  "dietary_restrictions": ["no_seafood", "vegetarian_option"],
  "family_size": 4,
  "pantry_items": ["chicken", "rice", "pasta"],
  "preferences": {
    "cuisine": ["Italian", "Mexican"],
    "kid_friendly": true
  }
}
```

**Output Format (Structured JSON)**:
```json
{
  "meal_plan": [
    {
      "day": "Monday",
      "breakfast": {
        "meal_name": "Poha",
        "prep_time_minutes": 15,
        "servings": 4,
        "ingredients": ["poha", "onion", "peanuts", "turmeric"],
        "recipe_steps": "1. Rinse poha. 2. Heat oil, add mustard seeds...",
        "reference_link": "https://example.com/poha-recipe"
      },
      "lunch": {
        "meal_name": "Dal Tadka",
        "prep_time_minutes": 30,
        "servings": 4,
        "ingredients": ["toor dal", "onion", "tomato", "cumin"],
        "recipe_steps": "1. Pressure cook dal. 2. Prepare tadka...",
        "reference_link": "https://example.com/dal-tadka"
      },
      "dinner": {
        "meal_name": "Paneer Butter Masala",
        "prep_time_minutes": 40,
        "servings": 4,
        "ingredients": ["paneer", "tomato", "cream", "garam masala"],
        "recipe_steps": "1. Prepare tomato gravy. 2. Add paneer cubes...",
        "reference_link": "https://example.com/paneer-recipe"
      }
    }
    // ... 6 more days
  ],
  "grocery_list": {
    "vegetables": [{"item": "onions", "quantity": "1 kg"}],
    "grains": [{"item": "rice", "quantity": "2 kg"}],
    "spices": [{"item": "turmeric", "quantity": "50g"}],
    "dairy": [{"item": "paneer", "quantity": "500g"}]
  },
  "summary": "7-day vegetarian meal plan"
}
```

**ADK Implementation**:
```python
from google.genai import Agent
from google.adk.tools import FunctionTool

# Main Meal Planner Agent with structured JSON output
meal_planner = Agent(
    model="gemini-2.5-flash-lite",
    instruction="""Generate meal plans and return ONLY valid JSON in this format:
    {
      "meal_plan": [{"day": "Monday", "breakfast": {...}, "lunch": {...}, "dinner": {...}}],
      "grocery_list": {"vegetables": [...], "grains": [...], "spices": [...]},
      "summary": "..."
    }
    Return ONLY the JSON - no extra text!""",
    tools=[
        'google_search',
        FunctionTool(check_pantry_inventory),
        FunctionTool(save_meal_plan)
    ]
)
```

**Key Design Change**: Removed Recipe Refiner sub-agent. All recipe adjustments now done directly by Meal Planner with structured JSON output.

**Future Enhancements** (Not part of Phase 1 implementation):
- ✉️ **Email Integration**: Send meal plans via email (Gmail API)
- 📅 **Calendar Integration**: Add meals to Google Calendar events
- 📖 **Calendar Reading**: Read existing calendar to avoid conflicts with weekly planning

---

### 3.3 Week Planner Agent

**Role**: Create comprehensive weekly schedule (meals + kids activities + events)  
**Framework**: Google ADK `Agent` class  
**LLM**: Gemini 2.5 Flash Lite  
**Pattern**: Sequential processing with meal plan input

**Tools (FunctionTool wrappers)**:
1. `create_schedule(schedule_item)` - Saves scheduled activities

**Storage Methods Called**:
- `storage.get_family(family_id)` → Reads `families` table
- `storage.create_schedule(schedule_data)` → Writes `schedules` table

**Database Tables Used**:
- `families` (READ) - Get family member info for activities
- `schedules` (WRITE) - Save scheduled activities  

**Input Format** (from Orchestrator extraction):
```json
{
  "family_id": "sharma_001",
  "start_date": "2025-12-02",
  "meal_plan_data": {
    "meal_plan": [
      {
        "day": "Monday",
        "breakfast": {"meal_name": "Poha", "prep_time_minutes": 15},
        "lunch": {"meal_name": "Dal Tadka", "prep_time_minutes": 30},
        "dinner": {"meal_name": "Paneer Masala", "prep_time_minutes": 40}
      }
      // ... rest of week
    ],
    "summary": "7-day vegetarian meal plan with Indian cuisine"
  }
}
```

**Output Format**:
```json
{
  "weekly_schedule": {
    "Monday": {
      "date": "2025-12-02",
      "meals": {
        "breakfast": "Pancakes (15 min)",
        "lunch": "Sandwiches (10 min)",
        "dinner": "Chicken Tacos (30 min)"
      },
      "activities": ["Soccer practice 16:00"],
      "notes": "Prepare soccer gear. Start dinner early before practice."
    },
    "Tuesday": {
      "date": "2025-12-03",
      "meals": {
        "breakfast": "Oatmeal (10 min)",
        "lunch": "Pasta Salad (20 min)",
        "dinner": "Stir Fry (25 min)"
      },
      "activities": ["Piano lesson 17:00"],
      "notes": "Dinner before piano lesson."
    }
    // ... rest of week
  },
  "weekly_summary": {
    "total_meals": 21,
    "total_activities": 5,
    "busy_days": ["Monday", "Tuesday", "Wednesday", "Friday"],
    "free_days": ["Thursday", "Saturday", "Sunday"]
  }
}
```

**ADK Parallel Pattern**:
```python
from google.genai.types import ParallelRunner

# Process meals and activities in parallel
week_planner = genai.Agent(
    model="gemini-2.0-flash",
    tools=[
        process_meals_tool,
        process_activities_tool,
        merge_schedule_tool
    ]
)

# Use ParallelRunner for concurrent processing
parallel_runner = ParallelRunner([
    lambda: process_meals(meal_plan),
    lambda: process_activities(activities_db)
])
results = parallel_runner.run()
```

---

### 3.4 Grocery Planner Agent

**Role**: Generate shopping list from pre-extracted ingredients by checking pantry stock  
**Framework**: Google ADK `Agent` class  
**LLM**: Gemini 2.5 Flash Lite

**Tools (FunctionTool wrappers)**:
1. `check_pantry_inventory(family_id, ingredients)` - Checks what's in stock
2. `consolidate_shopping_list(ingredients)` - Merges duplicate items
3. `organize_by_sections(ingredients)` - Groups by store sections
4. `save_shopping_to_pantry(family_id, items)` - Updates pantry after shopping

**Storage Methods Called**:
- `storage.get_pantry(family_id)` → Reads `pantry` table
- `storage.update_pantry_stock(family_id, updates)` → Writes `pantry` table

**Database Tables Used**:
- `pantry` (READ) - Check current stock levels
- `pantry` (WRITE) - Update stock after shopping  

**Input Format** (from Orchestrator extraction):
```json
{
  "family_id": "sharma_001",
  "grocery_list_data": {
    "vegetables": [{"item": "onions", "quantity": "1 kg"}],
    "grains": [{"item": "rice", "quantity": "2 kg"}],
    "spices": [{"item": "turmeric", "quantity": "50g"}],
    "dairy": [{"item": "paneer", "quantity": "500g"}]
  },
  "pantry_stock": {
    "rice": {"quantity": "2 cups", "category": "grains"},
    "turmeric": {"quantity": "100g", "category": "spices"}
  }
}
```

**Output Format**:
```json
{
  "shopping_list": {
    "produce": [
      {"item": "tomatoes", "quantity": "6"},
      {"item": "onions", "quantity": "3"},
      {"item": "bell peppers", "quantity": "2"}
    ],
    "protein": [
      {"item": "chicken breast", "quantity": "2 lbs"},
      {"item": "eggs", "quantity": "1 dozen"}
    ],
    "dairy": [
      {"item": "milk", "quantity": "1 gallon"},
      {"item": "parmesan cheese", "quantity": "8 oz"}
    ],
    "grains": [
      {"item": "tortillas", "quantity": "1 pack"}
    ]
  },
  "total_items": 24,
  "items_already_in_stock": ["rice", "pasta", "olive_oil"],
  "stock_update_required": [
    {"item": "rice", "deduct": "1 cup"},
    {"item": "pasta", "deduct": "400g"}
  ]
}
```

**Stock Management Workflow**:

1. **Receive Pre-extracted List**: Orchestrator passes `grocery_list` from MealPlanner JSON output
2. **Check Pantry Stock**: Agent uses `check_pantry_inventory` tool to see what's available
3. **Generate Shopping List**: Only adds items NOT in stock or insufficient quantity
4. **Save to Pantry**: Uses `save_shopping_to_pantry` to update pantry inventory after shopping
5. **No Separate Table**: Grocery lists are managed through pantry table updates

**Future Enhancements** (Not part of Phase 1):
- 💰 **Expense Tracking**: Track spending, generate monthly reports
- 📱 **Auto Stock Update**: Scan receipts to auto-update pantry inventory
- 🔔 **Low Stock Alerts**: Notify when staples (rice, oil) running low

---

## 🔄 4. Data Flow & Orchestration

### 4.1 Complete Data Flow Diagram

**End-to-End Data Journey** (What data, when, where, how):

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: USER INPUT                                                  │
├─────────────────────────────────────────────────────────────────────┤
│ Data: {                                                             │
│   "request": "Plan my week",                                       │
│   "family_id": "fam_123",                                          │
│   "week_start_date": "2024-12-02"                                  │
│ }                                                                   │
│ Where Used: Orchestrator Agent receives this                       │
│ When: Initial API call or chat interaction                         │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: ORCHESTRATOR AGENT (Data Gathering Phase)                  │
├─────────────────────────────────────────────────────────────────────┤
│ Data Read:                                                          │
│   → ChromaDB: get_family_profile(family_id)                        │
│   → Firestore: get_pantry_inventory(family_id)                     │
│   → Firestore: get_past_meal_plans(family_id, limit=4 weeks)      │
│                                                                     │
│ Data Retrieved:                                                     │
│   • family_profile = {members, allergies, preferences}             │
│   • pantry_stock = {rice: "2 cups", pasta: "500g", ...}            │
│   • past_meals = ["Tacos", "Pasta", "Stir-fry"] (avoid repeats)   │
│                                                                     │
│ Where Used: Passed as context to downstream agents                 │
│ When: Before calling Meal Planner                                  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: MEAL PLANNER AGENT (Recipe Generation)                     │
├─────────────────────────────────────────────────────────────────────┤
│ Input Data:                                                         │
│   • family_profile (from Step 2)                                   │
│   • past_meals (to avoid repetition)                               │
│   • user_preferences = "quick meals on weekdays"                   │
│                                                                     │
│ Processing:                                                         │
│   1. google_search("quick recipes")             │
│   2. Filter results by: dietary restrictions, past meals           │
│   3. Select 7 breakfasts, 7 lunches, 7 dinners                     │
│   4. For each meal: extract ingredients, prep time, recipe steps   │
│   5. Generate structured JSON with meal_plan + grocery_list        │
│                                                                     │
│ Output Data (meal_plan.json):                                      │
│   {                                                                 │
│     "Monday": {                                                     │
│       "breakfast": {"meal_name": "Pancakes", "prep_time": "15"},  │
│       "lunch": {"meal_name": "Sandwiches", "prep_time": "10"},   │
│       "dinner": {"meal_name": "Chicken Tacos", "prep_time": "30"} │
│     },                                                              │
│     ... (all 7 days)                                                │
│   }                                                                 │
│                                                                     │
│ Where Used: Passed to Week Planner + Grocery Planner               │
│ When: After all 21 meals generated and refined                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: WEEK PLANNER AGENT (Parallel Scheduling)                   │
├─────────────────────────────────────────────────────────────────────┤
│ Input Data:                                                         │
│   • meal_plan.json (from Step 3)                                   │
│   • family_profile.members (kids ages: 8, 5)                       │
│                                                                     │
│ Data Read:                                                          │
│   → JSON File: activities_database.json (soccer, art class, etc.) │
│                                                                     │
│ Parallel Processing (using ParallelRunner):                        │
│   ┌──────────────────────┐   ┌─────────────────────────┐          │
│   │ Thread 1: Meals      │   │ Thread 2: Activities    │          │
│   │ ─────────────────    │   │ ──────────────────────  │          │
│   │ • Parse meal_plan    │   │ • Filter activities by  │          │
│   │ • Add prep times     │   │   kids' ages (5-8)      │          │
│   │ • Schedule timing    │   │ • Check availability    │          │
│   │ • Mark cooking slots │   │ • Schedule Mon/Wed/Fri  │          │
│   └──────────────────────┘   └─────────────────────────┘          │
│             ↓                            ↓                         │
│          Merged via merge_schedule() utility function              │
│                                                                     │
│ Output Data (weekly_schedule.json):                                │
│   {                                                                 │
│     "Monday": {                                                     │
│       "08:00": "Breakfast - Pancakes",                             │
│       "12:00": "Lunch - Sandwiches",                               │
│       "16:00": "Activity - Soccer Practice",                       │
│       "18:00": "Dinner - Chicken Tacos"                            │
│     },                                                              │
│     ... (all 7 days with time slots)                               │
│   }                                                                 │
│                                                                     │
│ Where Used: Shown to user in final plan                           │
│ When: After parallel processing completes                          │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: GROCERY PLANNER AGENT (Shopping List Generation)           │
├─────────────────────────────────────────────────────────────────────┤
│ Input Data:                                                         │
│   • meal_plan.json (from Step 3) - needs ingredients               │
│   • pantry_stock (from Step 2) - what's already available          │
│                                                                     │
│ Processing:                                                         │
│   1. Extract all ingredients from 21 meals                         │
│   2. Aggregate quantities (e.g., 5 meals need chicken = 3 lbs)     │
│   3. Call check_pantry(ingredient) for each item                   │
│   4. IF pantry_stock[item] >= required → skip from shopping        │
│   5. IF pantry_stock[item] < required → add to list                │
│   6. Group by category (produce, dairy, meat, grains)              │
│                                                                     │
│ Data Read:                                                          │
│   → pantry_stock via check_pantry() utility function               │
│                                                                     │
│ Output Data (shopping_list.json):                                  │
│   {                                                                 │
│     "shopping_list": {                                              │
│       "produce": [{"item": "tomatoes", "quantity": "6"}],         │
│       "meat": [{"item": "chicken breast", "quantity": "2 lbs"}],  │
│       "dairy": [{"item": "milk", "quantity": "1 gallon"}]         │
│     },                                                              │
│     "total_items": 24,                                              │
│     "items_already_in_stock": ["rice", "pasta", "olive_oil"],     │
│     "stock_update_required": [                                      │
│       {"item": "rice", "deduct": "1 cup"},                        │
│       {"item": "pasta", "deduct": "400g"}                         │
│     ]                                                               │
│   }                                                                 │
│                                                                     │
│ Where Used: Shown to user + stored for pantry updates              │
│ When: After all ingredients aggregated and checked                 │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: ORCHESTRATOR SYNTHESIS (Combines All Results)              │
├─────────────────────────────────────────────────────────────────────┤
│ Input Data:                                                         │
│   • meal_plan.json (21 meals)                                      │
│   • weekly_schedule.json (time-slotted calendar)                   │
│   • shopping_list.json (24 items, grouped by category)             │
│                                                                     │
│ Processing:                                                         │
│   • Synthesize into human-readable summary                         │
│   • Format for presentation                                        │
│   • Add approval prompt                                            │
│                                                                     │
│ Output to User:                                                     │
│   "📅 Your Weekly Plan:                                             │
│    🍽️ Meals: Pancakes Mon, Tacos Tue, Pasta Wed...                 │
│    ⚽ Activities: Soccer Mon/Wed 4pm, Art Class Fri 3pm            │
│    🛒 Shopping: 24 items (Tomatoes, Chicken, Milk...)              │
│                                                                     │
│    Do you approve this plan? (yes/no/modify)"                      │
│                                                                     │
│ Where Stored: ADK Session (session_id) for HITL workflow           │
│ When: After all 3 agents complete                                  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 7: HUMAN-IN-THE-LOOP APPROVAL                                 │
├─────────────────────────────────────────────────────────────────────┤
│ User Input:                                                         │
│   • "yes" → Proceed to save                                        │
│   • "no" → Discard and restart                                     │
│   • "modify: change Tuesday dinner" → Re-run Meal Planner          │
│                                                                     │
│ IF APPROVED ("yes"):                                                │
│   Data Write Operations:                                            │
│   ✓ Firestore.save("weekly_plans", weekly_schedule.json)          │
│   ✓ Firestore.save("shopping_lists", shopping_list.json)          │
│   ✓ ChromaDB.add(meal_plan.json) → for future recommendations     │
│   ✓ Firestore.update("pantry_stock", deduct rice/pasta)           │
│                                                                     │
│ IF MODIFY:                                                          │
│   • Parse modification request                                     │
│   • Re-run specific agent (Meal/Week/Grocery)                      │
│   • Maintain session context via ADK session_id                    │
│   • Loop back to Step 6 for new synthesis                          │
│                                                                     │
│ Where Stored: Firestore + ChromaDB (long-term memory)              │
│ When: Only after user confirms "yes"                               │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Sequential Workflow (Primary Pattern)

**ADK Implementation**: `SequentialRunner` or manual chaining

```
USER: "Plan my week"
  ↓
[Orchestrator Agent]
  ↓ (Sequential calls)
  ↓
[1. Meal Planner Agent]
  ├── Calls: google_search (recipes)
  ├── Calls: recipe_refiner_agent (SUB-AGENT)
  └── Returns: meal_plan.json
  ↓
[2. Week Planner Agent]
  ├── Input: meal_plan.json
  ├── Parallel: process_meals() + process_activities()
  └── Returns: weekly_schedule.json
  ↓
[3. Grocery Planner Agent]
  ├── Input: meal_plan.json + pantry_inventory
  └── Returns: shopping_list.json
  ↓
[Orchestrator] → Synthesizes → Presents to USER
  ↓
🔔 HUMAN-IN-THE-LOOP: "Approve? (yes/no/modify)"
  ↓
  ├─→ YES → Save & finalize
  ├─→ MODIFY → Re-run with changes
  └─→ NO → Reject & restart
```

**ADK Code Pattern (with Human-in-the-Loop)**:
```python
from google import genai

session_id = "user_123"

# Step 1: Generate complete plan
orchestrator_response = orchestrator.send_message(
    "Plan this week for my family of 4",
    session_id=session_id
)

print(orchestrator_response.text)
# Output: "Here's your weekly plan:
#          Meals: Pancakes Mon, Tacos Tue...
#          Activities: Soccer Mon, Art Fri...
#          Shopping: 24 items
#          Do you approve? (yes/no/modify)"

# HUMAN-IN-THE-LOOP: User approval
user_approval = input("Your response: ").lower()

if user_approval == "yes":
    final_plan = orchestrator_response
    print("✅ Plan approved and saved!")
    
elif user_approval == "modify":
    changes = input("What to change? ")
    # Re-run with modifications
    final_plan = orchestrator.send_message(
        f"Modify: {changes}",
        session_id=session_id
    )
    print("✅ Plan updated!")

---

### 4.4 Data Transformation Pipeline

**How Data Changes Between Agents**:

```
┌──────────────────────────────────────────────────────────────────┐
│ Stage 1: User Input → Orchestrator                              │
├──────────────────────────────────────────────────────────────────┤
│ Input Format:                                                    │
│   Natural language: "Plan meals for my family this week"        │
│                                                                  │
│ Transformation:                                                  │
│   • Extract family_id from session/auth                         │
│   • Parse date range ("this week" → 2024-12-02 to 2024-12-08)  │
│   • Fetch family context from ChromaDB                          │
│                                                                  │
│ Output Format:                                                   │
│   {                                                              │
│     "family_id": "fam_123",                                     │
│     "week_start": "2024-12-02",                                 │
│     "family_profile": {members, allergies, preferences},        │
│     "pantry_stock": {rice: "2 cups", pasta: "500g"}            │
│   }                                                              │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 2: Orchestrator → Meal Planner                            │
├──────────────────────────────────────────────────────────────────┤
│ Input Format (from Stage 1):                                     │
│   {family_profile, pantry_stock, week_start}                    │
│                                                                  │
│ Transformation by Meal Planner:                                  │
│   • Query google_search for recipes                             │
│   • Filter by dietary restrictions                              │
│   • Select 21 meals (7 days × 3 meals)                          │
│   • For each meal: extract ingredients, prep time, steps        │
│   • Generate structured JSON with meal_plan + grocery_list      │
│                                                                  │
│ Output Format (meal_plan.json with embedded grocery_list):       │
│   {                                                              │
│     "Monday": {                                                  │
│       "breakfast": {"meal_name": "Pancakes", "prep_time": 15}, │
│       "lunch": {"meal_name": "Sandwiches", "prep_time": 10},   │
│       "dinner": {"meal_name": "Tacos", "prep_time": 30}        │
│     },                                                           │
│     ... (Tuesday-Sunday)                                         │
│   }                                                              │
│   ✓ Simple format: Only meal_name + prep_time                  │
│   ✓ No ingredients (those stored separately)                    │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 3: Meal Plan → Week Planner                               │
├──────────────────────────────────────────────────────────────────┤
│ Input Format (meal_plan.json from Stage 2):                     │
│   {Monday: {breakfast, lunch, dinner}, ...}                     │
│                                                                  │
│ Transformation by Week Planner:                                  │
│   • Parse meal_plan into time slots                             │
│   • Breakfast → 08:00, Lunch → 12:00, Dinner → 18:00           │
│   • Add prep time buffers (30 min dinner needs start at 17:30) │
│   • Fetch activities_database for kids' schedules               │
│   • Parallel merge: meals + activities                          │
│   • Resolve conflicts (if activity at 6pm, move dinner to 7pm) │
│                                                                  │
│ Output Format (weekly_schedule.json):                            │
│   {                                                              │
│     "Monday": {                                                  │
│       "08:00": "Breakfast - Pancakes",                          │
│       "12:00": "Lunch - Sandwiches",                            │
│       "16:00": "Activity - Soccer Practice",                    │
│       "18:00": "Dinner - Tacos"                                 │
│     },                                                           │
│     ... (complete 7-day schedule)                               │
│   }                                                              │
│   ✓ Time-slotted format for calendar view                       │
│   ✓ Includes meals + activities merged                          │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 4: Meal Plan → Grocery Planner                            │
├──────────────────────────────────────────────────────────────────┤
│ Input Format:                                                    │
│   • meal_plan.json (from Stage 2)                               │
│   • pantry_stock (from Stage 1)                                 │
│                                                                  │
│ Transformation by Grocery Planner:                               │
│   • For each meal_name, lookup full recipe with ingredients     │
│   • Aggregate all ingredients across 21 meals                   │
│   • Example: "Tacos" appears 2x → 2 lbs chicken total          │
│   • Check pantry: IF pantry_stock["rice"] >= 1 cup → skip      │
│   • Group by category: produce, meat, dairy, grains             │
│   • Calculate stock deductions                                  │
│                                                                  │
│ Output Format (shopping_list.json):                              │
│   {                                                              │
│     "shopping_list": {                                           │
│       "produce": [{"item": "tomatoes", "quantity": "6"}],      │
│       "meat": [{"item": "chicken", "quantity": "2 lbs"}]       │
│     },                                                           │
│     "total_items": 24,                                           │
│     "items_already_in_stock": ["rice", "pasta"],                │
│     "stock_update_required": [                                   │
│       {"item": "rice", "deduct": "1 cup"}                      │
│     ]                                                            │
│   }                                                              │
│   ✓ Categorized shopping list                                   │
│   ✓ Shows what to buy + what to deduct from pantry             │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 5: All Outputs → Orchestrator Synthesis                   │
├──────────────────────────────────────────────────────────────────┤
│ Input Format:                                                    │
│   • meal_plan.json (21 meals)                                   │
│   • weekly_schedule.json (time-slotted calendar)                │
│   • shopping_list.json (categorized items)                      │
│                                                                  │
│ Transformation by Orchestrator:                                  │
│   • Convert JSON to human-readable narrative                    │
│   • Summarize key points                                        │
│   • Add approval prompt                                         │
│                                                                  │
│ Output Format (to User):                                         │
│   Natural language text:                                        │
│   "📅 Your Weekly Plan is ready!                                 │
│                                                                  │
│    🍽️ MEALS (21 total):                                         │
│    Mon: Pancakes, Sandwiches, Tacos                             │
│    Tue: Oatmeal, Salad, Pasta...                                │
│                                                                  │
│    ⚽ ACTIVITIES:                                                │
│    Soccer Practice - Mon/Wed 4pm                                │
│    Art Class - Fri 3pm                                          │
│                                                                  │
│    🛒 SHOPPING LIST (24 items):                                  │
│    Produce: Tomatoes (6), Lettuce (1 head)...                   │
│    Meat: Chicken breast (2 lbs)...                              │
│                                                                  │
│    Already in pantry: Rice, Pasta, Olive oil                    │
│                                                                  │
│    Do you approve this plan? (yes/no/modify)"                   │
│                                                                  │
│   ✓ User-friendly narrative (not JSON)                          │
│   ✓ Includes HITL prompt                                        │
└──────────────────────────────────────────────────────────────────┘
```
    
else:
    print("❌ Plan rejected. Starting over...")
```

### 4.2 Parallel Execution (Week Planner Internal)

**ADK Implementation**: `ParallelRunner`

```python
from google.genai.types import ParallelRunner

# Inside Week Planner Agent
def plan_week_parallel(meal_plan, activities_db):
    # Execute in parallel
    runners = [
        lambda: organize_meals(meal_plan),
        lambda: schedule_activities(activities_db),
        lambda: identify_conflicts()
    ]
    
    parallel = ParallelRunner(runners)
    results = parallel.run()  # All execute simultaneously
    
    # Merge results
    return merge_into_weekly_schedule(results)
```

---

### 4.5 Utility Functions & Helper Tools

**All Custom Functions Required for MomsHelperAI**:

#### 4.5.1 Data Access Functions

```python
# ──────────────────────────────────────────────────────────────
# FUNCTION: get_family_profile
# WHERE USED: Orchestrator Agent (Step 2 in data flow)
# WHEN CALLED: At start of every planning request
# DATA SOURCE: ChromaDB or Firestore
# ──────────────────────────────────────────────────────────────
def get_family_profile(family_id: str) -> dict:
    """
    Retrieves family profile with members, allergies, preferences.
    
    Args:
        family_id: Unique family identifier (e.g., "fam_123")
    
    Returns:
        {
            "family_id": "fam_123",
            "members": [
                {"name": "Emma", "age": 8, "allergies": [], "preferences": ["pasta"]},
                {"name": "Liam", "age": 5, "allergies": ["peanuts"], "preferences": ["chicken"]}
            ],
            "dietary_restrictions": ["no_seafood"],
            "family_size": 4
        }
    
    Data Usage:
        • Passed to Meal Planner for recipe filtering
        • Used by Recipe Refiner for portion adjustment
        • Used by Week Planner for activity selection (kids' ages)
    """
    # Implementation: Query ChromaDB or Firestore
    from google.cloud import firestore
    db = firestore.Client()
    doc = db.collection('families').document(family_id).get()
    return doc.to_dict()


# ──────────────────────────────────────────────────────────────
# FUNCTION: get_pantry_inventory
# WHERE USED: Orchestrator (Step 2), Grocery Planner (Step 5)
# WHEN CALLED: Before meal planning, before shopping list generation
# DATA SOURCE: Firestore (structured data)
# ──────────────────────────────────────────────────────────────
def get_pantry_inventory(family_id: str) -> dict:
    """
    Gets current pantry stock for a family.
    
    Args:
        family_id: Unique family identifier
    
    Returns:
        {
            "rice": "2 cups",
            "pasta": "500g",
            "olive_oil": "1 bottle",
            "tomato_sauce": "2 cans",
            "last_updated": "2024-12-01T10:30:00Z"
        }
    
    Data Usage:
        • Grocery Planner checks stock before adding items to shopping list
        • If pantry has enough, item skipped from shopping
        • After shopping, this data updated via update_pantry_stock()
    """
    from google.cloud import firestore
    db = firestore.Client()
    doc = db.collection('pantry').document(family_id).get()
    return doc.to_dict() if doc.exists else {}


# ──────────────────────────────────────────────────────────────
# FUNCTION: get_past_meal_plans
# WHERE USED: Meal Planner Agent (Step 3)
# WHEN CALLED: Before generating new meal plan (to avoid repeats)
# DATA SOURCE: Firestore or ChromaDB vector search
# ──────────────────────────────────────────────────────────────
def get_past_meal_plans(family_id: str, weeks: int = 4) -> list:
    """
    Retrieves past meal plans to avoid repetition.
    
    Args:
        family_id: Unique family identifier
        weeks: How many weeks back to check (default 4)
    
    Returns:
        [
            "Chicken Tacos",
            "Spaghetti Bolognese",
            "Grilled Salmon",
            "Vegetable Stir-fry"
        ]
    
    Data Usage:
        • Meal Planner filters out these meals from new suggestions
        • Ensures variety week-to-week
        • Example: If "Tacos" in past 4 weeks → suggest "Burritos" instead
    """
    from google.cloud import firestore
    from datetime import datetime, timedelta
    
    db = firestore.Client()
    cutoff_date = datetime.now() - timedelta(weeks=weeks)
    
    plans = db.collection('weekly_plans') \
              .where('family_id', '==', family_id) \
              .where('created_at', '>=', cutoff_date) \
              .stream()
    
    past_meals = []
    for plan in plans:
        data = plan.to_dict()
        for day in data.get('meals', {}).values():
            for meal in day.values():
                past_meals.append(meal.get('meal_name'))
    
    return list(set(past_meals))  # Remove duplicates


# ──────────────────────────────────────────────────────────────
# FUNCTION: get_activities_database
# WHERE USED: Week Planner Agent (Step 4)
# WHEN CALLED: When scheduling kids' activities
# DATA SOURCE: JSON file or Firestore
# ──────────────────────────────────────────────────────────────
def get_activities_database(kids_ages: list) -> list:
    """
    Fetches available activities filtered by kids' ages.
    
    Args:
        kids_ages: List of children's ages [8, 5]
    
    Returns:
        [
            {
                "id": "act_001",
                "name": "Soccer Practice",
                "age_range": [6, 12],
                "schedule": {"days": ["Monday", "Wednesday"], "time": "16:00"},
                "duration_minutes": 60
            },
            {
                "id": "act_002",
                "name": "Art Class",
                "age_range": [5, 10],
                "schedule": {"days": ["Friday"], "time": "15:00"},
                "duration_minutes": 90
            }
        ]
    
    Data Usage:
        • Week Planner schedules these activities in weekly_schedule.json
        • Filters by age: only show activities where kid's age in age_range
        • Example: 5-year-old qualifies for Art Class [5-10] but not Teen Coding [13-17]
    """
    import json
    
    with open('data/activities_database.json', 'r') as f:
        all_activities = json.load(f)['activities']
    
    # Filter activities where at least one kid's age fits
    filtered = []
    for activity in all_activities:
        age_min, age_max = activity['age_range']
        if any(age_min <= age <= age_max for age in kids_ages):
            filtered.append(activity)
    
    return filtered


#### 4.5.2 Data Processing Functions

```python
# ──────────────────────────────────────────────────────────────
# FUNCTION: check_pantry
# WHERE USED: Grocery Planner Agent (Step 5)
# WHEN CALLED: For each ingredient before adding to shopping list
# DATA SOURCE: Calls get_pantry_inventory() internally
# ──────────────────────────────────────────────────────────────
def check_pantry(family_id: str, ingredient: str, required_qty: str) -> dict:
    """
    Checks if ingredient available in pantry with sufficient quantity.
    
    Args:
        family_id: Unique family identifier
        ingredient: Item name (e.g., "rice")
        required_qty: Needed amount (e.g., "2 cups")
    
    Returns:
        {
            "available": True/False,
            "current_stock": "3 cups",
            "required": "2 cups",
            "action": "skip" or "buy"
        }
    
    Data Usage:
        • IF available=True → Grocery Planner skips item from shopping list
        • IF available=False → Add to shopping_list.json
        • Stores "current_stock" for display to user
    
    Example:
        check_pantry("fam_123", "rice", "2 cups")
        → {"available": True, "current_stock": "3 cups", "action": "skip"}
        Result: Rice NOT added to shopping list
    """
    pantry = get_pantry_inventory(family_id)
    current = pantry.get(ingredient, "0")
    
    # Simple comparison (production version needs unit conversion)
    available = current != "0" and current >= required_qty
    
    return {
        "available": available,
        "current_stock": current,
        "required": required_qty,
        "action": "skip" if available else "buy"
    }


# ──────────────────────────────────────────────────────────────
# FUNCTION: merge_schedule
# WHERE USED: Week Planner Agent (Step 4)
# WHEN CALLED: After parallel processing meals + activities
# DATA SOURCE: In-memory data from ParallelRunner threads
# ──────────────────────────────────────────────────────────────
def merge_schedule(meals_schedule: dict, activities_schedule: dict) -> dict:
    """
    Merges meal schedule and activities schedule into unified calendar.
    
    Args:
        meals_schedule: {
            "Monday": {
                "08:00": "Breakfast - Pancakes",
                "12:00": "Lunch - Sandwiches",
                "18:00": "Dinner - Tacos"
            }
        }
        activities_schedule: {
            "Monday": {
                "16:00": "Soccer Practice"
            }
        }
    
    Returns:
        {
            "Monday": {
                "08:00": "Breakfast - Pancakes",
                "12:00": "Lunch - Sandwiches",
                "16:00": "Activity - Soccer Practice",
                "18:00": "Dinner - Tacos"
            }
        }
    
    Data Usage:
        • Combines outputs from parallel threads
        • Handles conflicts (if activity and dinner same time → shift dinner)
        • Sorts by time for chronological view
        • Returns weekly_schedule.json
    """
    merged = {}
    
    # Merge all days
    all_days = set(list(meals_schedule.keys()) + list(activities_schedule.keys()))
    
    for day in all_days:
        merged[day] = {}
        
        # Add meals
        if day in meals_schedule:
            merged[day].update(meals_schedule[day])
        
        # Add activities
        if day in activities_schedule:
            for time, activity in activities_schedule[day].items():
                if time in merged[day]:
                    # Conflict detected - shift meal by 30 min
                    new_time = shift_time(time, 30)
                    merged[day][new_time] = merged[day][time]
                merged[day][time] = activity
        
        # Sort by time
        merged[day] = dict(sorted(merged[day].items()))
    
    return merged


def shift_time(time_str: str, minutes: int) -> str:
    """Helper to shift time slots (e.g., '18:00' + 30 min = '18:30')"""
    from datetime import datetime, timedelta
    time_obj = datetime.strptime(time_str, "%H:%M")
    new_time = time_obj + timedelta(minutes=minutes)
    return new_time.strftime("%H:%M")


# ──────────────────────────────────────────────────────────────
# FUNCTION: aggregate_ingredients
# WHERE USED: Grocery Planner Agent (Step 5)
# WHEN CALLED: After extracting ingredients from all 21 meals
# DATA SOURCE: In-memory meal_plan.json with full recipes
# ──────────────────────────────────────────────────────────────
def aggregate_ingredients(meal_plan: dict) -> dict:
    """
    Aggregates ingredients across all meals (e.g., 3 meals need chicken → total 3 lbs).
    
    Args:
        meal_plan: Full meal plan with ingredients for each meal
    
    Returns:
        {
            "chicken breast": "3 lbs",
            "tomatoes": "8",
            "rice": "2 cups",
            "olive oil": "1/4 cup"
        }
    
    Data Usage:
        • Grocery Planner uses this to generate shopping_list.json
        • Before adding to list, calls check_pantry() for each item
        • Groups by category (produce, meat, dairy, grains)
    
    Example:
        Monday Dinner: Tacos → chicken: 1 lb, tomatoes: 3
        Thursday Dinner: Grilled Chicken → chicken: 1 lb, tomatoes: 2
        Result: {"chicken breast": "2 lbs", "tomatoes": "5"}
    """
    from collections import defaultdict
    
    aggregated = defaultdict(float)
    
    for day, meals in meal_plan.items():
        for meal_type, meal_data in meals.items():
            for ingredient, quantity in meal_data.get('ingredients', {}).items():
                # Simple aggregation (production needs unit conversion)
                aggregated[ingredient] += parse_quantity(quantity)
    
    # Convert back to strings
    return {item: format_quantity(qty) for item, qty in aggregated.items()}


def parse_quantity(qty_str: str) -> float:
    """Convert '2 lbs' → 2.0"""
    import re
    match = re.search(r'([\d.]+)', qty_str)
    return float(match.group(1)) if match else 0.0


def format_quantity(qty: float) -> str:
    """Convert 2.0 → '2 lbs'"""
    return f"{qty:.1f} lbs" if qty > 1 else f"{qty:.2f} lbs"


#### 4.5.3 Data Storage Functions

```python
# ──────────────────────────────────────────────────────────────
# FUNCTION: save_weekly_plan
# WHERE USED: Orchestrator Agent (Step 7 - after HITL approval)
# WHEN CALLED: Only when user says "yes" to approve plan
# DATA TARGET: Firestore (structured data) + ChromaDB (vector memory)
# ──────────────────────────────────────────────────────────────
def save_weekly_plan(family_id: str, meal_plan: dict, weekly_schedule: dict, shopping_list: dict):
    """
    Saves approved plan to Firestore and ChromaDB for future reference.
    
    Args:
        family_id: Unique family identifier
        meal_plan: meal_plan.json from Meal Planner
        weekly_schedule: weekly_schedule.json from Week Planner
        shopping_list: shopping_list.json from Grocery Planner
    
    Data Written:
        • Firestore: /weekly_plans/{plan_id} → complete plan
        • ChromaDB: Meal names vectorized for future recommendations
        • Firestore: /shopping_lists/{plan_id} → for user reference
    
    When Used:
        • After HITL approval ("yes")
        • NOT called if user says "no" or "modify"
    """
    from google.cloud import firestore
    from datetime import datetime
    
    db = firestore.Client()
    
    # Save to Firestore
    plan_id = f"{family_id}_{datetime.now().strftime('%Y%m%d')}"
    db.collection('weekly_plans').document(plan_id).set({
        'family_id': family_id,
        'created_at': datetime.now(),
        'meals': meal_plan,
        'schedule': weekly_schedule,
        'shopping_list': shopping_list
    })
    
    # Save to ChromaDB for long-term memory
    from chromadb import Client
    chroma_client = Client()
    collection = chroma_client.get_or_create_collection("family_preferences")
    
    # Store meal names as vectors
    for day, meals in meal_plan.items():
        for meal_type, meal_data in meals.items():
            collection.add(
                documents=[meal_data['meal_name']],
                metadatas=[{"family_id": family_id, "liked": True}],
                ids=[f"{family_id}_{day}_{meal_type}"]
            )


# ──────────────────────────────────────────────────────────────
# FUNCTION: update_pantry_stock
# WHERE USED: Orchestrator Agent (Step 7 - after HITL approval)
# WHEN CALLED: After user approves plan, to deduct used ingredients
# DATA TARGET: Firestore /pantry/{family_id}
# ──────────────────────────────────────────────────────────────
def update_pantry_stock(family_id: str, stock_updates: list):
    """
    Updates pantry inventory by deducting used ingredients.
    
    Args:
        family_id: Unique family identifier
        stock_updates: [
            {"item": "rice", "deduct": "1 cup"},
            {"item": "pasta", "deduct": "400g"}
        ]
    
    Data Updated:
        • Firestore /pantry/{family_id}
        • Example: rice: "3 cups" → "2 cups" after deducting 1 cup
    
    When Used:
        • Only after HITL approval
        • Ensures pantry reflects actual consumption
        • Next week's plan will see updated stock
    """
    from google.cloud import firestore
    
    db = firestore.Client()
    pantry_ref = db.collection('pantry').document(family_id)
    
    current_pantry = pantry_ref.get().to_dict()
    
    for update in stock_updates:
        item = update['item']
        deduct = parse_quantity(update['deduct'])
        current = parse_quantity(current_pantry.get(item, "0"))
        
        new_qty = max(0, current - deduct)  # Prevent negative stock
        current_pantry[item] = format_quantity(new_qty)
    
    pantry_ref.set(current_pantry)
```

#### 4.5.4 ADK Tool Wrapper Functions

```python
# ──────────────────────────────────────────────────────────────
# FUNCTION: create_recipe_refiner_tool
# WHERE USED: Meal Planner Agent (Step 3)
# WHEN CALLED: Wraps Recipe Refiner Sub-Agent as ADK tool
# DATA FLOW: recipe → sub-agent → refined_recipe
# ──────────────────────────────────────────────────────────────
def create_recipe_refiner_tool():
    """
    Wraps Recipe Refiner Sub-Agent as FunctionDeclaration for ADK.
    
    Returns:
        ADK Tool that Meal Planner can call
    
    Usage in Meal Planner:
        meal_planner = genai.Agent(
            model="gemini-2.0-flash",
            tools=[google_search, recipe_refiner_tool]  # ← This tool
        )
    
    Data Usage:
        • Input: {raw_recipe, family_size, allergies}
        • Processing: Sub-agent adjusts portions, substitutes allergens
        • Output: {refined_recipe with exact quantities}
    """
    from google.genai.types import FunctionDeclaration
    
    return FunctionDeclaration(
        name="refine_recipe",
        description="Adjusts recipe portions and substitutes ingredients for allergies",
        parameters={
            "type": "object",
            "properties": {
                "recipe_name": {"type": "string"},
                "family_size": {"type": "integer"},
                "allergies": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["recipe_name", "family_size"]
        }
    )


# ──────────────────────────────────────────────────────────────
# FUNCTION: create_check_pantry_tool
# WHERE USED: Grocery Planner Agent (Step 5)
# WHEN CALLED: ADK tool for checking pantry stock
# DATA FLOW: Wraps check_pantry() as ADK tool
# ──────────────────────────────────────────────────────────────
def create_check_pantry_tool():
    """
    Wraps check_pantry() function as ADK FunctionDeclaration.
    
    Returns:
        ADK Tool for Grocery Planner agent
    
    Usage in Grocery Planner:
        grocery_planner = genai.Agent(
            model="gemini-2.0-flash",
            tools=[check_pantry_tool]  # ← This tool
        )
    """
    from google.genai.types import FunctionDeclaration
    
    return FunctionDeclaration(
        name="check_pantry",
        description="Checks if ingredient available in family's pantry",
        parameters={
            "type": "object",
            "properties": {
                "ingredient": {"type": "string"},
                "required_qty": {"type": "string"}
            },
            "required": ["ingredient", "required_qty"]
        }
    )
```

---

## 💾 5. Data Management & Storage

### 5.1 Storage Strategy: **SQLite (Local) → Firestore (Production)**

**Chosen Approach**: Use **SQLite** for development/demo, easy upgrade to **Firestore** for production

| Component | Technology | Purpose | Why This Choice |
|-----------|-----------|---------|-----------------|
| **Agent Framework** | **Google ADK (ONLY)** | Agent orchestration, LLM calls | Required for Kaggle |
| **Vector Store** | ChromaDB (local) | Store family preferences, semantic search | Works offline, production-ready |
| **Structured Data (MVP)** | **SQLite** | Pantry, plans, profiles | Single file, SQL queries, zero setup |
| **Structured Data (Prod)** | Firestore | Cloud sync, multi-user | Upgrade path from SQLite |
| **Static Data** | JSON files | Activities database | Version-controlled, rarely changes |

---

### 5.2 Why JSON Files Are NOT Production-Ready

**JSON files work for demos but fail in production:**

| Problem | Why It Breaks | Production Impact |
|---------|---------------|-------------------|
| **❌ No Concurrency Control** | 2 users update pantry → last write wins, data lost | Family members can't use app simultaneously |
| **❌ No Transactions** | App crashes mid-save → corrupted partial data | Weekly plan saved but pantry not updated = inconsistent state |
| **❌ No Indexing** | Must read entire file to find 1 record | Slow for 1000+ weekly plans (linear O(n) search) |
| **❌ No Relationships** | Can't link pantry items to recipes efficiently | Manual joins in Python code = slow & error-prone |
| **❌ No Validation** | Bad data written directly to file | `{"rice": "abc"}` crashes app on next read |
| **❌ File Locking Issues** | OS locks file during write → other processes blocked | Multi-agent parallel execution fails |
| **❌ No Backups** | File corrupted = all data lost | No automatic recovery |
| **❌ No Access Control** | Anyone can edit files | Security risk for multi-user app |

**Example Failure Scenario:**
```python
# User 1: Updating pantry
pantry = json.load(open('pantry.json'))  # rice: 2 cups
pantry['rice'] = '1 cup'

# User 2: Updating pantry (simultaneously)
pantry = json.load(open('pantry.json'))  # rice: 2 cups (stale read!)
pantry['pasta'] = '500g'

# User 1 saves
json.dump(pantry, open('pantry.json', 'w'))  # {rice: 1 cup}

# User 2 saves (overwrites User 1's change!)
json.dump(pantry, open('pantry.json', 'w'))  # {rice: 2 cups, pasta: 500g}

# RESULT: User 1's rice update LOST!
```

---

### 5.3 Recommended Solution: **SQLite (Production-Ready + Zero Setup)**

**Why SQLite is BETTER than JSON AND production-ready:**

| Feature | JSON Files | SQLite | Firestore |
|---------|-----------|--------|-----------|
| **Zero Setup** | ✅ Yes | ✅ Yes (built into Python) | ❌ Requires GCP account |
| **Offline** | ✅ Yes | ✅ Yes | ❌ Needs internet |
| **Concurrency** | ❌ No | ✅ Yes (ACID transactions) | ✅ Yes |
| **Queries** | ❌ Manual loops | ✅ SQL (fast) | ✅ Yes |
| **Relationships** | ❌ Manual | ✅ Foreign keys | ✅ Yes |
| **Backups** | ❌ Manual | ✅ Copy `.db` file | ✅ Auto |
| **Scalability** | ❌ 100s of records | ✅ 1M+ records | ✅ Unlimited |
| **Multi-user** | ❌ No | ⚠️ Single server | ✅ Yes |
| **Production Ready** | ❌ **NO** | ✅ **YES** (for single-instance apps) | ✅ **YES** (for cloud) |
| **Kaggle Demo** | ✅ Easy | ✅ Easy | ❌ Complex setup |

**SQLite is production-ready for:**
- ✅ Single-server apps (Cloud Run with 1 instance)
- ✅ Desktop/mobile apps (family uses 1 device)
- ✅ Apps with <100K concurrent users
- ✅ Read-heavy workloads (99% reads, 1% writes)

**Upgrade to Firestore when:**
- You need multi-region deployment
- You have >100 concurrent users
- You need real-time sync across devices
- You want Google to handle backups/scaling

---

### 5.4 Data Architecture (SQLite MVP → Firestore Production)

**Phase 1: SQLite (Kaggle Demo + Production for 1000s of users)**

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR APPLICATION                         │
│                 (Python + Google ADK)                       │
└──────┬──────────────────┬──────────────────┬───────────────┘
       │                  │                  │
       ↓                  ↓                  ↓
┌─────────────┐  ┌─────────────────┐  ┌──────────────┐
│  JSON FILES │  │  SQLITE DATABASE│  │  CHROMADB    │
│  (Static)   │  │  (Dynamic Data) │  │  (Vectors)   │
├─────────────┤  ├─────────────────┤  ├──────────────┤
│ Location:   │  │ Location:       │  │ Location:    │
│ ./data/     │  │ ./data/         │  │ ./chroma.db  │
│             │  │ momshelper.db   │  │              │
├─────────────┤  ├─────────────────┤  ├──────────────┤
│ Contains:   │  │ Contains:       │  │ Contains:    │
│ • activities│  │ • pantry_stock  │  │ • meal vectors│
│   database  │  │ • weekly_plans  │  │ • preferences│
│             │  │ • family_profiles│  │ • history    │
│             │  │ • shopping_lists│  │              │
└─────────────┘  └─────────────────┘  └──────────────┘
     ↑                    ↑                    ↑
  READ ONLY          READ + WRITE           READ + WRITE
  (Rarely changes)   (User data)           (ML features)
```

**Single File Database:** `./data/momshelper.db` (20-50 KB, scales to 100s MB)

**Why This Works for Production:**
- ✅ **ACID Transactions**: Pantry + plan saved together (or both fail)
- ✅ **Fast Queries**: `SELECT * FROM pantry WHERE family_id = ?` (instant)
- ✅ **Concurrent Reads**: Multiple agents read simultaneously
- ✅ **Write Safety**: SQLite locks during writes (no data corruption)
- ✅ **Portable**: Copy `.db` file = instant backup
- ✅ **Cloud-Ready**: Deploy to Cloud Run with persistent disk

---

### 5.5 SQLite Schema (Production-Ready)

```sql
-- Family profiles table
CREATE TABLE families (
    family_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    member_count INTEGER,
    dietary_restrictions TEXT,  -- JSON array
    preferences TEXT             -- JSON object
);

-- Pantry inventory table
CREATE TABLE pantry (
    family_id TEXT,
    item TEXT,
    quantity TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (family_id, item),
    FOREIGN KEY (family_id) REFERENCES families(family_id)
);
CREATE INDEX idx_pantry_family ON pantry(family_id);

-- Weekly plans table
CREATE TABLE weekly_plans (
    plan_id TEXT PRIMARY KEY,
    family_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    week_start_date DATE,
    meal_plan TEXT,        -- JSON
    schedule TEXT,         -- JSON
    shopping_list TEXT,    -- JSON
    approved BOOLEAN DEFAULT 0,
    FOREIGN KEY (family_id) REFERENCES families(family_id)
);
CREATE INDEX idx_plans_family ON weekly_plans(family_id, created_at DESC);

-- Meal history (for avoiding repeats)
CREATE TABLE meal_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id TEXT,
    meal_name TEXT,
    served_date DATE,
    liked BOOLEAN,
    FOREIGN KEY (family_id) REFERENCES families(family_id)
);
CREATE INDEX idx_meals_family_date ON meal_history(family_id, served_date DESC);
```

**Benefits:**
- ✅ **Foreign Keys**: Data integrity enforced
- ✅ **Indexes**: Fast lookups (O(log n) instead of O(n))
- ✅ **Timestamps**: Track when data changes
- ✅ **JSON Columns**: Flexible for nested data (meal_plan, schedule)

---

### 5.6 Data Flow (SQLite Implementation)

```
User Request → ADK Agent
       ↓
   1. Read from SQLite:
      - Family profile
      - Pantry inventory
      - Past 4 weeks meal history
       ↓
   2. Query ChromaDB (semantic search):
      - Find similar liked meals
       ↓
   3. Agent generates plan
       ↓
   4. HUMAN-IN-THE-LOOP: Approve?
       ↓
   5. IF YES → SQLite Transaction:
      BEGIN TRANSACTION;
        INSERT INTO weekly_plans (...);
        UPDATE pantry SET quantity = ...;
        INSERT INTO meal_history (...);
      COMMIT;  -- All or nothing!
       ↓
   6. Store vectors in ChromaDB
       ↓
   Returns formatted response
```

**Transaction Example (Prevents Data Loss):**
```python
import sqlite3
from datetime import datetime

def save_approved_plan(family_id, meal_plan, shopping_list, stock_updates):
    """Save plan with ACID guarantees"""
    conn = sqlite3.connect('./data/momshelper.db')
    cursor = conn.cursor()
    
    try:
        # Start transaction
        cursor.execute('BEGIN TRANSACTION')
        
        # 1. Save weekly plan
        plan_id = f"{family_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        cursor.execute('''
            INSERT INTO weekly_plans (plan_id, family_id, meal_plan, shopping_list, approved)
            VALUES (?, ?, ?, ?, 1)
        ''', (plan_id, family_id, json.dumps(meal_plan), json.dumps(shopping_list)))
        
        # 2. Update pantry stock
        for update in stock_updates:
            cursor.execute('''
                UPDATE pantry 
                SET quantity = ?, last_updated = CURRENT_TIMESTAMP
                WHERE family_id = ? AND item = ?
            ''', (update['new_qty'], family_id, update['item']))
        
        # 3. Log meal history
        for day, meals in meal_plan.items():
            for meal_type, meal_data in meals.items():
                cursor.execute('''
                    INSERT INTO meal_history (family_id, meal_name, served_date)
                    VALUES (?, ?, ?)
                ''', (family_id, meal_data['meal_name'], day))
        
        # Commit all changes atomically
        conn.commit()
        print("✅ All data saved successfully!")
        
    except Exception as e:
        # Rollback if anything fails
        conn.rollback()
        print(f"❌ Error: {e}. All changes rolled back.")
        raise
    
    finally:
        conn.close()
```

**If app crashes after step 2:** ✅ SQLite rolls back ALL changes (nothing saved)  
**With JSON files:** ❌ Plan saved, pantry NOT updated (inconsistent state!)

---

### 5.7 Upgrade Path: SQLite → Firestore

**When you outgrow SQLite (100K+ users):**

```python
# Change 1 line in your code:
# from storage.sqlite_storage import DataStorage
from storage.firestore_storage import DataStorage  # Same API!

# Rest of code unchanged! 🎉
storage = DataStorage()
storage.save_weekly_plan(family_id, meal_plan, ...)
```

**Both implement same interface:**
```python
class DataStorage:
    def get_family_profile(self, family_id: str) -> dict: ...
    def get_pantry_inventory(self, family_id: str) -> dict: ...
    def save_weekly_plan(self, family_id, meal_plan, schedule, shopping_list): ...
    def update_pantry_stock(self, family_id, stock_updates): ...
```

**Migration script:**
```python
# One-time migration
sqlite_storage = SQLiteStorage('./data/momshelper.db')
firestore_storage = FirestoreStorage()

# Copy all data
for family in sqlite_storage.get_all_families():
    firestore_storage.save_family_profile(family)
    firestore_storage.save_pantry(family['family_id'], ...)
```

---

### 5.8 ChromaDB (Vector Store) - Production Ready

**ChromaDB Setup (Local → Cloud):**

```python
# Development: Local file
from chromadb import Client
chroma_client = Client()  # Creates ./chroma.db

# Production: ChromaDB Cloud (or self-hosted)
from chromadb import HttpClient
chroma_client = HttpClient(
    host="chromadb.example.com",
    port=8000
)

# API is identical!
collection = chroma_client.get_or_create_collection("family_preferences")
collection.add(documents=["Chicken Tacos"], metadatas=[{"liked": True}], ids=["meal_1"])
```

**ChromaDB is production-ready** (used by companies like Shopify, Replit)

---

### 5.9 Final Recommendation (Best of Both Worlds)

**For Kaggle Submission + Production:**

```
Phase 1 (Kaggle Demo):
✅ SQLite (./data/momshelper.db)
✅ ChromaDB (./chroma.db)  
✅ JSON files (activities_database.json)
✅ Zero cloud dependencies
✅ Works offline
✅ Production-ready for 1000s of users

Phase 2 (Scale to 100K+ users):
✅ Firestore (replace SQLite with 1 line change)
✅ ChromaDB Cloud (same API)
✅ JSON files (unchanged)
```

**Summary Table:**

| Requirement | JSON Files | SQLite | Firestore |
|-------------|-----------|--------|-----------|
| **Kaggle Demo** | ✅ Simple | ✅ Simple | ❌ Complex |
| **Production (1K users)** | ❌ **NO** | ✅ **YES** | ✅ YES |
| **Production (100K+ users)** | ❌ **NO** | ⚠️ Single server limit | ✅ **YES** |
| **ACID Transactions** | ❌ | ✅ | ✅ |
| **Setup Complexity** | ✅ None | ✅ None | ❌ GCP account |
| **Offline** | ✅ | ✅ | ❌ |
| **Cost** | Free | Free | $0.06 per 100K reads |

**Winner: SQLite for Kaggle + Initial Production, Firestore for massive scale** 🏆

### 5.2 Session & Memory (ADK Built-in)

**ADK Session Service**:
```python
from google.genai import InMemorySessionService

session_service = InMemorySessionService()

# Session stores conversation context
response = meal_planner.send_message(
    "Plan meals for this week",
    session_id="user_123",
    session_service=session_service
)

# Memory persists across sessions (family data)
# Use ChromaDB for long-term storage
```

### 5.3 Database Schema

**Mock Data (Kids Activities)**:
```json
{
  "activities_database": [
    {
      "id": "act_001",
      "name": "Soccer Practice",
      "category": "sports",
      "age_range": [6, 12],
      "schedule": {"days": ["Monday", "Wednesday"], "time": "16:00"},
      "duration_minutes": 60
    },
    {
      "id": "act_002",
      "name": "Art Class",
      "category": "creative",
      "age_range": [5, 10],
      "schedule": {"days": ["Friday"], "time": "15:00"},
      "duration_minutes": 90
    }
  ]
}
```

**Family Profile** (stored in ChromaDB/Firestore):
```json
{
  "family_id": "fam_123",
  "members": [
    {"name": "Emma", "age": 8, "allergies": [], "preferences": ["pasta", "pizza"]},
    {"name": "Liam", "age": 5, "allergies": ["peanuts"], "preferences": ["chicken", "rice"]}
  ],
  "dietary_restrictions": ["no_seafood", "vegetarian_option"],
  "preferred_stores": ["Whole Foods"],
  "budget_weekly": 150.00
}
```

---

## ☁️ 6. Deployment to Cloud (Google Cloud Platform)

## ☁️ 6. Deployment to Cloud (Google Cloud Platform)

### 6.1 Option 1: Vertex AI Agent Engine (Recommended)

**Best for**: Production deployment with ADK agents

**Steps**:
```bash
# 1. Install Google Cloud SDK
gcloud init

# 2. Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable run.googleapis.com

# 3. Deploy ADK agent to Vertex AI
# Create agent configuration
cat > agent_config.yaml <<EOF
agents:
  - name: momshelper-orchestrator
    model: gemini-2.0-flash
    tools:
      - meal_planner
      - week_planner
      - grocery_planner
EOF

# 4. Deploy using ADK CLI
adk deploy agent_config.yaml \
  --project=YOUR_PROJECT_ID \
  --region=us-central1

# 5. Get endpoint URL
gcloud ai-platform agents list
```

**Deployment Architecture**:
```
User Request (HTTPS)
  ↓
Vertex AI Agent Engine
  ├── Orchestrator Agent
  ├── Meal Planner Agent
  ├── Recipe Refiner Sub-Agent
  ├── Week Planner Agent
  └── Grocery Planner Agent
  ↓
Gemini 2.0 Flash API
  ↓
Response to User
```

---

### 6.2 Option 2: Cloud Run (Containerized Deployment)

**Best for**: Custom control, lower cost

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY agents/ ./agents/
COPY tools/ ./tools/
COPY data/ ./data/
COPY main.py .

# Set environment variables
ENV PORT=8080
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

# Run application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app
```

**Deploy to Cloud Run**:
```bash
# 1. Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/momshelper-ai

# 2. Deploy to Cloud Run
gcloud run deploy momshelper-ai \
  --image gcr.io/YOUR_PROJECT_ID/momshelper-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key

# 3. Get service URL
gcloud run services describe momshelper-ai --region us-central1
```

**API Endpoint**:
```
POST https://momshelper-ai-xxx.run.app/api/plan-week
Content-Type: application/json

{
  "user_id": "user_123",
  "request": "Plan my week"
}
```

---

### 6.3 Environment Variables & Secrets

**Required Configuration**:
```bash
# .env file (DO NOT commit to Git)
GEMINI_API_KEY=your_gemini_api_key_here
PROJECT_ID=your_gcp_project_id
REGION=us-central1

# For Firestore
FIRESTORE_DATABASE=(default)

# For ChromaDB (if using vector store)
CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db
```

**Use Google Secret Manager**:
```bash
# Store API key securely
echo -n "your_gemini_api_key" | \
  gcloud secrets create gemini-api-key --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"
```

---

### 6.4 Cost Estimation (Monthly)

| Service | Usage | Estimated Cost |
|---------|-------|----------------|
| Vertex AI Agent Engine | 10K requests/month | $15-30 |
| Gemini 2.0 Flash API | 10K requests (avg 1K tokens each) | $20-40 |
| Cloud Run | 50 hrs/month (scales to zero) | $5-10 |
| Firestore | 10K reads, 5K writes | $1-3 |
| **Total** | | **$41-83/month** |

---

## 📊 7. Capstone Requirements Checklist

### Features to Include (Kaggle Capstone)

| Requirement | Implementation | Status |
|------------|---------------|--------|
| **Multi-agent system** | 4 agents: Orchestrator + 3 specialists + 1 sub-agent | ✅ |
| **LLM-powered agents** | All use Gemini 2.0 Flash via ADK | ✅ |
| **Sequential agents** | Orchestrator → Meal → Week → Grocery (chained) | ✅ |
| **Parallel agents** | Week Planner (meals + activities in parallel) | ✅ |
| **Agent-as-tool (Sub-agent)** | Recipe Refiner sub-agent under Meal Planner | ✅ |
| **Custom tools** | `check_pantry`, `refine_recipe`, `merge_schedule` | ✅ |
| **Built-in tools** | `google_search` for recipe lookup | ✅ |
| **Sessions** | ADK InMemorySessionService | ✅ |
| **Human-in-the-Loop** | User approval after plan generation (yes/no/modify) | ✅ |
| **Long-term memory** | ChromaDB for family preferences (optional) | ⚠️ |
| **Observability** | ADK logging + custom metrics | ✅ |

**Total: 3+ key concepts ✅**  
- Multi-agent system ✅  
- Tools (custom + built-in) ✅  
- Sessions & Memory ✅  
- **Human-in-the-Loop** ✅  

---

## 🎯 8. Demo Scenarios & Expected Output

### Scenario 1: Complete Week Planning

**User Input**:
```
"Plan this week for my family. We have 2 kids (ages 8 and 5). 
No peanuts (allergy). Budget $150."
```

**Agent Flow**:
```
Orchestrator Agent
  ↓ (sequential)
Meal Planner Agent
  ├── google_search("kid-friendly recipes no peanuts")
  ├── recipe_refiner_agent.refine(recipe, family_size=4)
  └── Returns: 7-day meal plan
  ↓
Week Planner Agent (parallel)
  ├── Process meals (from meal plan)
  ├── Add activities (from mock DB: soccer, art class)
  └── Returns: weekly schedule
  ↓
Grocery Planner Agent
  ├── Extract ingredients from meal plan
  ├── Check current pantry stock
  ├── Remove items already in stock
  └── Returns: shopping list (24 items)
  ↓
Orchestrator synthesizes all → User
```

**Expected Output**:
```json
{
  "weekly_plan": {
    "meals": {
      "Monday": {
        "breakfast": "Pancakes (4 servings, refined by sub-agent)",
        "dinner": "Chicken Tacos (no peanuts, kid-friendly)"
      }
      // ... rest of week
    },
    "activities": {
      "Monday": ["Soccer practice 4pm"],
      "Friday": ["Art class 3pm"]
    },
    "shopping_list": {
      "total_items": 24,
      "organized_by_category": true
    }
  },
  "agents_executed": [
    "orchestrator",
    "meal_planner",
    "recipe_refiner_subagent",
    "week_planner",
    "grocery_planner"
  ],
  "execution_time": "14.2 seconds"
}
```

---

### Scenario 2: Meal Planning Only

**User Input**:
```
"Plan dinners for this week. We're vegetarian and have pasta in the pantry."
```

**Agent Flow**:
```
Orchestrator → Meal Planner
  ├── google_search("vegetarian dinner recipes")
  ├── check_pantry_inventory() → ["pasta"]
  ├── recipe_refiner_agent(recipe="Pasta Primavera", restrictions=["vegetarian"])
  └── Returns: 7 dinner recipes
```

**Expected Output**:
```json
{
  "dinners": [
    {
      "day": "Monday",
      "meal_name": "Vegetarian Pasta Primavera",
      "recipe": "Boil pasta, sauté veggies with garlic, toss with olive oil.",
      "uses_pantry_item": "pasta",
      "servings": 4,
      "prep_time": "25 min",
      "ingredients": ["pasta", "tomatoes", "zucchini", "olive oil", "garlic"],
      "refined_by_subagent": true,
      "reference_link": "https://example.com/veggie-pasta"
    }
    // ... 6 more days
  ],
  "shopping_needed": ["tomatoes", "zucchini", "bell peppers"]
}
```

---

## 🛠️ 9. Technology Stack Summary

### Core Technologies (ONLY)

```
┌─────────────────────────────────────────┐
│  AGENT FRAMEWORK                        │
│  Google ADK (Agent Development Kit)     │
│  - Version: Latest                      │
│  - Python SDK                           │
└─────────────────────────────────────────┘
        ↓ uses
┌─────────────────────────────────────────┐
│  LLM                                    │
│  Gemini 2.0 Flash                       │
│  - Via ADK's genai client               │
└─────────────────────────────────────────┘
        ↓ stores in
┌─────────────────────────────────────────┐
│  DATA LAYER                             │
│  - Sessions: InMemorySessionService     │
│  - Memory: ChromaDB (optional)          │
│  - Structured Data: JSON/Firestore      │
└─────────────────────────────────────────┘
        ↓ deployed on
┌─────────────────────────────────────────┐
│  CLOUD PLATFORM                         │
│  Google Cloud (Vertex AI / Cloud Run)   │
└─────────────────────────────────────────┘
```

**Dependencies** (`requirements.txt`):
```
google-adk>=1.0.0
google-cloud-aiplatform>=1.40.0
chromadb>=0.4.0  # Optional, for vector memory
google-cloud-firestore>=2.13.0  # Optional, for persistence
```

---

## 📈 10. Success Metrics

### Technical Metrics
- ✅ Response time < 15 seconds (end-to-end)
- ✅ Agent success rate > 95%
- ✅ Sub-agent refinement accuracy > 90%

### Business Metrics
- ✅ Time saved: 14 hrs → 4 hrs per week (71% reduction)
- ✅ Cost savings: $200/month (reduced food waste)
- ✅ User satisfaction: 4.5+/5

---

## ✅ 11. Implementation Checklist

### Phase 1: Setup (2 hours)
- [ ] Install Google ADK
- [ ] Get Gemini API key
- [ ] Set up project structure
- [ ] Create mock data (activities DB, pantry inventory)

### Phase 2: Agents (6 hours)
- [ ] Build Orchestrator Agent
- [ ] Build Meal Planner Agent + google_search tool
- [ ] Build Recipe Refiner Sub-Agent (agent-as-tool)
- [ ] Build Week Planner Agent (parallel pattern)
- [ ] Build Grocery Planner Agent

**Future Enhancements** (Post-Capstone):
- [ ] Email integration (send plans via Gmail API)
- [ ] Google Calendar integration (add meal events)
- [ ] Calendar reading (check existing events for week planning)

### Phase 3: Integration (2 hours)
- [ ] Implement sequential orchestration
- [ ] Test parallel execution in Week Planner
- [ ] Test sub-agent calls from Meal Planner

### Phase 4: Demo (2 hours)
- [ ] Create Jupyter notebook demo
- [ ] Test both scenarios
- [ ] Record video (< 3 min)

### Phase 5: Deployment (2 hours)
- [ ] Deploy to Cloud Run or Vertex AI
- [ ] Document deployment steps
- [ ] Test cloud endpoint

**Total: ~14 hours**

---

## 📚 12. References

- **Google ADK Documentation**: https://google.github.io/adk-docs/
- **Gemini API**: https://ai.google.dev/gemini-api/docs
- **Kaggle Capstone**: https://www.kaggle.com/competitions/google-5-day-agents-course-capstone
- **ADK Multi-Agent Patterns**: https://google.github.io/adk-docs/concepts/multi-agent/
- **Vertex AI Agent Engine**: https://cloud.google.com/vertex-ai/docs/agent-engine

---

**Document Version:** 2.0 (Simplified & Finalized)  
**Last Updated:** November 30, 2025  
**Author:** Pinkal  
**Status:** ✅ **ARCHITECTURE APPROVED - READY FOR IMPLEMENTATION**
  
