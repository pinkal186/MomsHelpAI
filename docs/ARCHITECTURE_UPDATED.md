# MomsHelperAI - Updated Architecture with SearchAgent

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    OrchestratorAgent                         │
│                 (Root Coordinator)                           │
│                 Model: gemini-2.5-flash-lite                 │
└───────────────┬─────────────────┬──────────────────┬─────────┘
                │                 │                  │
                ▼                 ▼                  ▼
    ┌───────────────────┐ ┌──────────────┐ ┌────────────────┐
    │ MealPlannerAgent  │ │WeekPlanner   │ │GroceryPlanner  │
    │                   │ │Agent         │ │Agent           │
    └─────────┬─────────┘ └──────────────┘ └────────────────┘
              │
              │ Uses 4 tools:
              │
              ├─► SearchAgent (AgentTool)
              │   └─► google_search ◄── ISOLATED HERE
              │
              ├─► RecipeRefinerAgent (AgentTool)
              │   └─► refine_recipe_for_family (function)
              │
              ├─► get_family_preferences (function)
              │
              └─► save_meal_plan (function)
```

## Key Design Decision: SearchAgent Isolation

### Why Separate SearchAgent?

**Problem:**
```python
# ❌ This fails with API error:
tools = [
    google_search,              # GoogleSearchTool object
    AgentTool(sub_agent),       # AgentTool object
    function1,                  # Python callable
    function2                   # Python callable
]
# Error: "Tools at indices [1] are not compatible with AFC"
```

**Solution:**
```python
# ✅ This works:
# SearchAgent (separate):
tools = [google_search]  # ONLY google_search

# MealPlanner:
tools = [
    AgentTool(search_agent),       # SearchAgent as tool
    AgentTool(recipe_refiner),     # Other sub-agents
    function1,                     # Functions
    function2
]
```

## Tool Compatibility Matrix

| Tool Type         | google_search | AgentTool | Functions |
|-------------------|---------------|-----------|-----------|
| **google_search** | ✅            | ❌        | ❌        |
| **AgentTool**     | ❌            | ✅        | ✅        |
| **Functions**     | ❌            | ✅        | ✅        |

## Workflow Example

```
User Request: "Plan vegetarian meals"
       │
       ▼
┌─────────────────────────────────────┐
│   MealPlannerAgent                  │
│                                     │
│  Step 1: get_family_preferences()  │
│          ↓                          │
│     Returns: {dietary: vegetarian} │
│                                     │
│  Step 2: SearchAgent ←─────────────┼─► SearchAgent
│          "Find vegetarian recipes" │      │
│          ↓                          │      ├─► google_search
│     Returns: Recipe list            │      └─► Returns results
│                                     │
│  Step 3: RecipeRefinerAgent ←──────┼─► RecipeRefinerAgent  
│          "Adjust for 4 servings"   │      │
│          ↓                          │      ├─► refine_recipe_for_family()
│     Returns: Refined recipes        │      └─► Returns adjusted
│                                     │
│  Step 4: save_meal_plan()          │
│          ↓                          │
│     Returns: {status: success}     │
└─────────────────────────────────────┘
```

## Benefits of This Architecture

1. **Compatibility** - No tool mixing conflicts
2. **Modularity** - Each agent has single responsibility
3. **Reusability** - SearchAgent can be used by any agent
4. **Testability** - Can test search functionality independently
5. **Maintainability** - Clear boundaries between components

## Files Changed

### New Files
- `agents/search_agent.py` - Dedicated search agent

### Modified Files
- `agents/meal_planner.py` - Uses SearchAgent instead of direct google_search
- `test/test_gemini_flash.py` - Updated test documentation

### Documentation
- `docs/SEARCH_AGENT_SOLUTION.md` - Detailed solution explanation
