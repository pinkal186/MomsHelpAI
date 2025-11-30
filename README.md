# 🏠 MomsHelperAI - Intelligent Family Planning System

> 🤖 Multi-agent system built with Google Agent Development Kit (ADK) for automated Indian family meal planning, weekly scheduling, and grocery management using Gemini 2.0 Flash LLM.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📖 Description

MomsHelperAI is an AI-powered family planning assistant designed specifically for Indian households. It uses multiple specialized AI agents to handle meal planning, activity scheduling, and grocery list generation with cultural awareness and dietary preference management.

The system uses Google's ADK framework with Gemini 2.0 Flash model to provide intelligent, context-aware planning that considers family size, dietary restrictions, regional cuisine preferences, and cultural events.

### ✨ Key Capabilities:
- 🍛 **Weekly meal planning** with authentic Indian recipes
- 📅 **Family activity scheduling** with age-appropriate suggestions
- 🛒 **Automated grocery list generation** with pantry tracking
- 🎉 **Cultural event awareness** (festivals, celebrations)
- 🥗 **Multi-dietary restriction support** (vegetarian, vegan, Jain, gluten-free)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🚀 Quick Start

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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📁 Project Structure

```
MomsHelperAI/
├── 🤖 agents/
│   ├── base_agent.py          # Base wrapper for Google ADK agents
│   ├── orchestrator.py        # 🎯 Root coordinator agent
│   ├── meal_planner.py        # 🍽️ Meal planning agent
│   ├── search_agent.py        # 🔍 Google search integration agent
│   ├── week_planner.py        # 📅 Activity scheduling agent
│   └── grocery_planner.py     # 🛒 Shopping list generator agent
├── 📊 models/
│   ├── family.py              # Family data model
│   ├── meal.py                # Meal data model
│   ├── grocery.py             # Grocery data model
│   └── schedule.py            # Schedule data model
├── 💾 storage/
│   ├── base_storage.py        # Storage interface
│   ├── sqlite_storage.py      # SQLite implementation
│   ├── chroma_storage.py      # ChromaDB vector storage
│   └── firestore_storage.py  # Firestore cloud storage
├── 🛠️ tools/
│   ├── recipe_tools.py        # Recipe management functions
│   ├── pantry_tools.py        # Pantry inventory functions
│   ├── schedule_tools.py      # Scheduling functions
│   └── ingredient_tools.py    # Ingredient utilities
├── ⚙️ utils/
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging setup
│   └── validators.py          # Input validation
├── 📂 data/
│   ├── activities_database.json    # Activity templates
│   └── sample_family_data.json     # Sample family data
├── 🧪 test/
│   ├── test_meal_planner.py
│   ├── test_meal_planner_run.py
│   └── test_orchestrator_comprehensive.py
├── main.py                    # 💻 CLI application
├── app.py                     # 🌐 Flask REST API
├── requirements.txt           # 📦 Python dependencies
└── README.md                  # 📄 This file
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🏗️ System Architecture

### 🔄 Agent Flow

```
👤 User Request
    │
    ▼
🎯 OrchestratorAgent (Root Coordinator)
    │
    ├──▶ 🍽️ MealPlannerAgent ──▶ 🔍 SearchAgent (Google Search for recipes)
    │                              │
    │                              ▼
    │                          🌐 Web Recipe Sources
    │
    ├──▶ 📅 WeekPlannerAgent ──▶ 📂 Activity Database
    │
    ├──▶ 🛒 GroceryPlannerAgent ──▶ 💾 Pantry Database
    │
    ▼
✅ Consolidated Response to User
```

### 📊 Data Flow

```
1️⃣ User Input ────────────────────────▶ Orchestrator
                                          │
2️⃣ Orchestrator ──▶ MealPlanner ──▶ SearchAgent (Google Search)
                         │                │
                         │                ▼
                         │            Web Recipes
                         │
                         ▼
                   Meal Plan + Grocery List
                         │
3️⃣ Orchestrator ──▶ WeekPlanner ──▶ Creates schedule using meal plan
                         │
                         ▼
                   Weekly Schedule
                         │
4️⃣ Orchestrator ──▶ GroceryPlanner ──▶ Consolidates grocery items
                         │
                         ▼
                   Optimized Shopping List
                         │
5️⃣ Orchestrator ────────────────────────▶ User (Complete Plan)
```

### 💾 Database Architecture

**🗄️ SQLite (Relational Data)**
- `families`: Family profiles and preferences
- `meals`: Meal plans and history
- `pantry`: Inventory tracking
- `schedules`: Activity schedules

**🔍 ChromaDB (Vector Search)**
- `recipes`: Indian recipe embeddings for semantic search
- `preferences`: Family preference patterns

**📄 JSON Files (Static Data)**
- `activities_database.json`: Age-appropriate activity templates
- `sample_family_data.json`: Default family configurations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🤖 Agent Details & Tool Flow

### 1️⃣ 🎯 OrchestratorAgent
- **Type**: Root Coordinator
- **Pattern**: Sequential execution
- **Tools**: Sub-agents as tools (AgentTool)
- **Tool Type**: `AgentTool` (wraps other agents)
- **Function**: Coordinates all sub-agents and manages workflow
- **Input**: User natural language request
- **Output**: Consolidated response from all agents

---

### 2️⃣ 🍽️ MealPlannerAgent
- **Type**: Specialized planner
- **Tools Used**:
  - `SearchAgent` (AgentTool) - For finding recipes via Google Search
  - `get_family_preferences` (FunctionTool) - Retrieves family dietary data
  - `save_meal_plan` (FunctionTool) - Saves meal plan to database
- **Tool Type**: Mixed (`AgentTool` + `FunctionTool`)
- **Input**: 
  - `family_id`: Family identifier
  - `request`: Natural language request
  - `num_days`: Number of days to plan (default: 7)
  - `dietary_restrictions`: List of restrictions
  - `preferences`: Cuisine and other preferences
- **Output**: JSON with:
  ```json
  {
    "meal_plan": [...],
    "grocery_list": {...},
    "summary": "..."
  }
  ```
- **Function**: Generates culturally appropriate meal plans with recipes from web search

---

### 3️⃣ 🔍 SearchAgent
- **Type**: Search specialist
- **Tools Used**:
  - `google_search` (GoogleSearch) - Google search tool from ADK
- **Tool Type**: `google_search` (Cannot be mixed with other tool types)
- **Input**: Search query with dietary filters
- **Output**: Raw search results from Google
- **Function**: Isolated agent for web search (required due to tool type restrictions)
- **Note**: ⚠️ This agent uses ONLY `google_search` - cannot mix with FunctionTool or CodeExecutionTool

---

### 4️⃣ 📅 WeekPlannerAgent
- **Type**: Scheduling specialist
- **Tools Used**:
  - `get_activity_suggestions` (FunctionTool) - Retrieves activities from database
  - `save_schedule_item` (FunctionTool) - Saves scheduled activities
- **Tool Type**: `FunctionTool`
- **Input**:
  ```json
  {
    "week_start_date": "2025-12-02",
    "meal_plan": {...},
    "kids_activities_db": [...]
  }
  ```
- **Output**:
  ```json
  {
    "weekly_schedule": {...},
    "weekly_summary": {...},
    "agent_suggestion": "..."
  }
  ```
- **Function**: Creates balanced weekly schedules with meals and activities

---

### 5️⃣ 🛒 GroceryPlannerAgent
- **Type**: Shopping specialist
- **Tools Used**:
  - `check_pantry_inventory` (FunctionTool) - Checks what's in stock
  - `consolidate_shopping_list` (FunctionTool) - Merges duplicate items
  - `organize_by_sections` (FunctionTool) - Organizes by store sections
  - `save_shopping_to_pantry` (FunctionTool) - Updates pantry database
- **Tool Type**: `FunctionTool`
- **Input**:
  ```json
  {
    "meal_plan": {...},
    "current_pantry_stock": {...}
  }
  ```
- **Output**:
  ```json
  {
    "shopping_list": {...},
    "total_items": 24,
    "items_already_in_stock": [...],
    "stock_update_required": [...]
  }
  ```
- **Function**: Deduplicates and organizes shopping items by checking pantry

---

### 🔧 Tool Types Summary

| Agent | Tool Type | Specific Tools |
|-------|-----------|---------------|
| 🎯 OrchestratorAgent | `AgentTool` | MealPlanner, WeekPlanner, GroceryPlanner |
| 🍽️ MealPlannerAgent | `AgentTool` + `FunctionTool` | SearchAgent, get_family_preferences, save_meal_plan |
| 🔍 SearchAgent | `google_search` | google_search (isolated) |
| 📅 WeekPlannerAgent | `FunctionTool` | get_activity_suggestions, save_schedule_item |
| 🛒 GroceryPlannerAgent | `FunctionTool` | check_pantry, consolidate_shopping_list, organize_by_sections, save_shopping_to_pantry |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📋 Sample Output

### 💻 CLI Example

```
╔══════════════════════════════════════════════════════════════════════════╗
║          MOMSHELPERAI - Your AI Family Planning Assistant               ║
╚══════════════════════════════════════════════════════════════════════════╝
Session ID: abc123...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Loading sample family data...
✅ Sample family 'Sharma' loaded (ID: sharma_001)
👨‍👩‍👧‍👦 Members: 4 (Rajesh, Priya, Aarav, Ananya)
🥗 Dietary: Vegetarian

You: Plan meals for this week

⏳ Processing request for sharma_001...
This may take a moment as AI agents work together...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 MomsHelperAI Response:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🍽️ WEEKLY MEAL PLAN (7 Days)

Day 1 - Monday:
  🌅 Breakfast: Poha with peanuts and curry leaves
  🌞 Lunch: Dal tadka, jeera rice, mixed vegetable sabzi
  🌙 Dinner: Paneer butter masala, roti, cucumber raita

Day 2 - Tuesday:
  🌅 Breakfast: Idli with sambhar and coconut chutney
  🌞 Lunch: Rajma curry, steamed rice, cabbage stir-fry
  🌙 Dinner: Aloo paratha with curd and pickle

... (continues for 7 days)

🛒 GROCERY SHOPPING LIST

🥬 Vegetables:
  ✓ Tomatoes: 2 kg
  ✓ Onions: 1.5 kg
  ✓ Potatoes: 2 kg
  ✓ Cauliflower: 1 head
  ✓ Spinach: 500g

🥛 Dairy:
  ✓ Milk: 3 liters
  ✓ Paneer: 500g
  ✓ Curd: 1 kg

... (complete categorized list)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Is this plan acceptable? (yes/no/modify):
```

### 🌐 API Response Example

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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| 🤖 AI Framework | Google Agent Development Kit (ADK) |
| 🧠 LLM Model | Gemini 2.0 Flash (`gemini-2.5-flash-lite`) |
| 🔍 Vector Database | ChromaDB (recipe search) |
| 💾 Relational Database | SQLite (local), Firestore (cloud option) |
| 🌐 Web Framework | Flask |
| 🐍 Programming Language | Python 3.10+ |
| ⚡ Async Processing | AsyncIO |
| 🔧 Tools | FunctionTool, AgentTool, google_search |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ⚙️ Setup Instructions

### 📋 Prerequisites
- ✅ Python 3.10 or higher
- ✅ Google API Key (Gemini API)
- ✅ pip package manager

### 📥 Installation

**1️⃣ Clone the repository**
```bash
git clone <repository-url>
cd MomsHelperAI
```

**2️⃣ Install dependencies**
```bash
pip install -r requirements.txt
```

**3️⃣ Configure environment**
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

**4️⃣ Initialize databases**
```bash
# Databases are auto-created on first run
# SQLite: ./data/momshelper.db
# ChromaDB: ./chroma.db
```

**5️⃣ Run the application**
```bash
# CLI mode
python main.py

# API server
python app.py
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 💬 Usage

### 🖥️ CLI Commands

```bash
help                    # Show available commands
family <id>             # Select family by ID
families                # List all families
quit/exit               # Exit application
```

**Natural language examples:**
```
💬 "Plan meals for this week"
💬 "Create shopping list for Diwali party"
💬 "Schedule weekend activities"
💬 "Find vegetarian breakfast recipes"
```

### 🌐 REST API Endpoints

**📨 Chat endpoint**
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "Plan dinner for tonight",
  "family_id": "sharma_001"
}
```

**🏥 Health check**
```bash
GET /health
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🧪 Testing

Run comprehensive tests:
```bash
# All tests
python -m pytest test/

# Specific tests
python test/test_meal_planner.py
python test/test_orchestrator_comprehensive.py
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🚀 Future Enhancements

### 📅 Calendar Integration
- **Google Calendar Sync**: Automatically sync meal schedules and activities to family Google Calendar
- **iCal Export**: Export weekly plans to `.ics` format for Apple Calendar, Outlook, etc.
- **Smart Reminders**: Set up automated reminders for meal prep, shopping trips, and activities
- **Conflict Detection**: Check calendar for existing events before scheduling activities
- **Multi-Calendar Support**: Integrate individual family member calendars for personalized scheduling

### 📧 Email Integration
- **Weekly Plan Emails**: Send automated weekly meal plan and shopping list via email
- **Shopping List SMS**: Text shopping list to family members when they're near grocery stores
- **Recipe Sharing**: Email detailed recipes with instructions to family members
- **Notification System**: Email alerts for upcoming events, low pantry stock, and meal prep reminders
- **PDF Reports**: Generate and email beautifully formatted PDF meal plans and shopping lists

### 🔮 Additional Future Features
- **🍕 Restaurant Integration**: Suggest nearby restaurants when too busy to cook
- **💰 Budget Tracking**: Track grocery expenses and suggest budget-friendly alternatives
- **👥 Multi-Family Sharing**: Share recipes and meal plans with friends and extended family
- **📊 Nutrition Analytics**: Track nutritional values and health goals
- **🎯 Meal Preferences Learning**: AI learns family preferences over time for better suggestions
- **🌍 Regional Cuisine Expansion**: Add more regional Indian cuisines (Bengali, Gujarati, Kerala, etc.)
- **🎉 Festival Special Plans**: Pre-made plans for Diwali, Holi, Eid, Christmas celebrations
- **🏋️ Fitness Integration**: Sync with fitness apps for calorie-aware meal planning
- **🗣️ Voice Assistant**: Integration with Google Assistant, Alexa for hands-free planning
- **📱 Mobile App**: Native iOS and Android apps with push notifications

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


## 📄 License

Built for educational purposes as part of Google Agentic AI Capstone Project.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📞 Support

For issues and questions:
- 📝 Open an issue on GitHub
- 📧 Contact the development team
- 📚 Check the documentation in `/docs` folder

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

<div align="center">

### 🌟 Built with ❤️ using Google Agent Development Kit (ADK) & Gemini 2.0 Flash

**MomsHelperAI** - Making Family Planning Smarter, One Meal at a Time! 🍛

</div>

