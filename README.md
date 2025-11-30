# MomsHelperAI - Intelligent Family Planning System

Multi-agent system built with Google Agent Development Kit (ADK) for automated Indian family meal planning, weekly scheduling, and grocery management using Gemini 2.0 Flash LLM.

==============================================================================

## Description

MomsHelperAI is an AI-powered family planning assistant designed specifically for Indian households. It uses multiple specialized AI agents to handle meal planning, activity scheduling, and grocery list generation with cultural awareness and dietary preference management.

The system uses Google's ADK framework with Gemini 2.0 Flash model to provide intelligent, context-aware planning that considers family size, dietary restrictions, regional cuisine preferences, and cultural events.

Key capabilities:
- Weekly meal planning with authentic Indian recipes
- Family activity scheduling with age-appropriate suggestions
- Automated grocery list generation with pantry tracking
- Cultural event awareness (festivals, celebrations)
- Multi-dietary restriction support (vegetarian, vegan, Jain, gluten-free)

==============================================================================

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key in .env file
# GOOGLE_API_KEY=your_api_key_here

# Run CLI interface
python main.py

# Run REST API server
python app.py

# Run Jupyter notebook
jupyter notebook MomsHelperAI_Demo.ipynb
```

==============================================================================

## Project Structure

```
MomsHelperAI/
├── agents/
│   ├── base_agent.py          # Base wrapper for Google ADK agents
│   ├── orchestrator.py        # Root coordinator agent
│   ├── meal_planner.py        # Meal planning agent
│   ├── recipe_refiner.py      # Recipe search with ChromaDB
│   ├── week_planner.py        # Activity scheduling agent
│   ├── grocery_planner.py     # Shopping list generator
│   └── search_agent.py        # Web search integration
├── models/
│   ├── family.py              # Family data model
│   ├── meal.py                # Meal data model
│   ├── grocery.py             # Grocery data model
│   └── schedule.py            # Schedule data model
├── storage/
│   ├── base_storage.py        # Storage interface
│   ├── sqlite_storage.py      # SQLite implementation
│   ├── chroma_storage.py      # ChromaDB vector storage
│   └── firestore_storage.py  # Firestore cloud storage
├── tools/
│   ├── recipe_tools.py        # Recipe management functions
│   ├── pantry_tools.py        # Pantry inventory functions
│   ├── schedule_tools.py      # Scheduling functions
│   └── ingredient_tools.py    # Ingredient utilities
├── utils/
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging setup
│   └── validators.py          # Input validation
├── data/
│   ├── activities_database.json    # Activity templates
│   └── sample_family_data.json     # Sample family data
├── test/
│   ├── test_meal_planner.py
│   ├── test_meal_planner_run.py
│   └── test_orchestrator_comprehensive.py
├── main.py                    # CLI application
├── app.py                     # Flask REST API
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

==============================================================================

## System Architecture

### Agent Flow

```
User Request
    |
    v
OrchestratorAgent (Root Coordinator)
    |
    +---> MealPlannerAgent --> RecipeRefinerAgent (ChromaDB search)
    |                              |
    |                              v
    |                          Recipe Database
    |
    +---> WeekPlannerAgent --> Activity Database
    |
    +---> GroceryPlannerAgent --> Pantry Database
    |
    v
Consolidated Response
```

### Data Flow

```
1. User Input --> Orchestrator
2. Orchestrator --> MealPlanner (generates meal plan + grocery list)
3. MealPlanner --> RecipeRefiner (searches recipes in ChromaDB)
4. Orchestrator --> WeekPlanner (creates schedule using meal plan)
5. Orchestrator --> GroceryPlanner (consolidates grocery items)
6. Orchestrator --> User (returns complete plan)
```

### Database Architecture

**SQLite (Relational Data)**
- families: Family profiles and preferences
- meals: Meal plans and history
- pantry: Inventory tracking
- schedules: Activity schedules

**ChromaDB (Vector Search)**
- recipes: Indian recipe embeddings for semantic search
- preferences: Family preference patterns

**JSON Files (Static Data)**
- activities_database.json: Age-appropriate activity templates
- sample_family_data.json: Default family configurations

==============================================================================

## Agent and Tool Flow

### 1. OrchestratorAgent
- Type: Root Coordinator
- Pattern: Sequential execution
- Tools: Sub-agents as tools
- Function: Coordinates all sub-agents and manages workflow

### 2. MealPlannerAgent
- Type: Specialized planner
- Tools: RecipeRefinerAgent (AgentTool), family data functions
- Input: Family ID, dietary restrictions, number of days
- Output: JSON with meal_plan array and grocery_list object
- Function: Generates culturally appropriate meal plans

### 3. RecipeRefinerAgent
- Type: Search specialist
- Tools: ChromaDB vector search
- Input: Recipe query, dietary filters
- Output: Matching recipes with ingredients
- Function: Semantic recipe search

### 4. WeekPlannerAgent
- Type: Scheduling specialist
- Tools: Activity database, schedule functions
- Input: Meal plan, family data, date range
- Output: Weekly schedule with activities
- Function: Creates balanced activity schedules

### 5. GroceryPlannerAgent
- Type: Shopping specialist
- Tools: Pantry check, ingredient consolidation
- Input: Grocery list from meals, pantry inventory
- Output: Optimized shopping list by category
- Function: Deduplicates and organizes shopping items

==============================================================================

## Sample Output

### CLI Example

```
MOMSHELPERAI - Your AI Family Planning Assistant
==============================================================================
Session ID: abc123...
==============================================================================

Loading sample family data...
Sample family 'Sharma' loaded (ID: sharma_001)
Members: 4 (Rajesh, Priya, Aarav, Ananya)
Dietary: Vegetarian

You: Plan meals for this week

Processing request for sharma_001...
This may take a moment as AI agents work together...

==============================================================================
MomsHelperAI Response:
==============================================================================

WEEKLY MEAL PLAN (7 Days)

Day 1 - Monday:
  Breakfast: Poha with peanuts and curry leaves
  Lunch: Dal tadka, jeera rice, mixed vegetable sabzi
  Dinner: Paneer butter masala, roti, cucumber raita

Day 2 - Tuesday:
  Breakfast: Idli with sambhar and coconut chutney
  Lunch: Rajma curry, steamed rice, cabbage stir-fry
  Dinner: Aloo paratha with curd and pickle

... (continues for 7 days)

GROCERY SHOPPING LIST

Vegetables:
  - Tomatoes: 2 kg
  - Onions: 1.5 kg
  - Potatoes: 2 kg
  - Cauliflower: 1 head
  - Spinach: 500g

Dairy:
  - Milk: 3 liters
  - Paneer: 500g
  - Curd: 1 kg

... (complete categorized list)

==============================================================================

Is this plan acceptable? (yes/no/modify):
```

### API Response Example

```json
{
  "meal_plan": {
    "meal_plan": [
      {
        "day": "Monday",
        "breakfast": "Poha with peanuts",
        "lunch": "Dal tadka with rice",
        "dinner": "Paneer butter masala with roti"
      }
    ],
    "grocery_list": {
      "vegetables": [
        {"item": "Tomatoes", "quantity": "2 kg"},
        {"item": "Onions", "quantity": "1.5 kg"}
      ],
      "dairy": [
        {"item": "Milk", "quantity": "3 liters"}
      ]
    },
    "summary": "7-day vegetarian meal plan for family of 4"
  },
  "weekly_schedule": {
    "days": [
      {
        "date": "2025-12-01",
        "activities": [
          {"time": "08:00", "activity": "Breakfast - Poha"},
          {"time": "10:00", "activity": "Kids - School"},
          {"time": "16:00", "activity": "Kids - Homework time"},
          {"time": "20:00", "activity": "Family - Dinner together"}
        ]
      }
    ]
  },
  "shopping_list": {
    "total_items": 24,
    "categories": ["vegetables", "dairy", "spices", "grains"],
    "organized_list": {}
  },
  "agents_executed": ["MealPlanner", "WeekPlanner", "GroceryPlanner"],
  "execution_summary": "Planned 7 days with 21 meals, 28 activities, 24 grocery items"
}
```

==============================================================================

## Technology Stack

- AI Framework: Google Agent Development Kit (ADK)
- LLM: Gemini 2.0 Flash
- Vector Database: ChromaDB (recipe search)
- Relational Database: SQLite (local), Firestore (cloud option)
- Web Framework: Flask
- Language: Python 3.10+
- Async: AsyncIO

==============================================================================

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Google API Key (Gemini API)
- pip package manager

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd MomsHelperAI
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

4. Initialize databases
```bash
# Databases are auto-created on first run
# SQLite: ./data/momshelper.db
# ChromaDB: ./chroma.db
```

5. Run the application
```bash
# CLI mode
python main.py

# API server
python app.py
```

==============================================================================

## Usage

### CLI Commands

```
help                    Show available commands
family <id>             Select family by ID
families                List all families
quit/exit               Exit application

Natural language examples:
  "Plan meals for this week"
  "Create shopping list for Diwali party"
  "Schedule weekend activities"
  "Find vegetarian breakfast recipes"
```

### REST API Endpoints

```bash
# Chat endpoint
POST /api/chat
Content-Type: application/json
{
  "message": "Plan dinner for tonight",
  "family_id": "sharma_001"
}

# Health check
GET /health
```

==============================================================================

## Testing

Run comprehensive tests:
```bash
# All tests
python -m pytest test/

# Specific tests
python test/test_meal_planner.py
python test/test_orchestrator_comprehensive.py
```

==============================================================================

## License

Built for educational purposes.

==============================================================================
