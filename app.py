"""
MomsHelperAI - Flask Web API
REST API wrapping Google ADK agents with session management
"""

from flask import Flask, request, jsonify, session
from datetime import datetime
import uuid
import asyncio
from functools import wraps

from agents.orchestrator import orchestrator
from storage.sqlite_storage import SQLiteStorage
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Create Flask app
app = Flask(__name__)
if Config.GOOGLE_API_KEY:
    app.secret_key = Config.GOOGLE_API_KEY[:32]  # Use first 32 chars of API key
else:
    app.secret_key = 'dev-secret-key-change-in-production'

# Initialize storage
storage = SQLiteStorage()


def async_route(f):
    """Decorator to run async functions in Flask routes."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'MomsHelperAI',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/families', methods=['GET'])
def get_families():
    """Get all families in database."""
    try:
        # Simplified: return empty list or sample data
        families = []
        # Try to get sample family if exists
        try:
            sample_family = storage.get_family('sharma_001')
            if sample_family:
                families.append(sample_family)
        except:
            pass
        
        return jsonify({
            'success': True,
            'families': families,
            'count': len(families)
        })
    except Exception as e:
        logger.error(f"Error getting families: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/families/<family_id>', methods=['GET'])
def get_family(family_id):
    """Get specific family details."""
    try:
        family = storage.get_family(family_id)
        
        if not family:
            return jsonify({
                'success': False,
                'error': f"Family {family_id} not found"
            }), 404
        
        return jsonify({
            'success': True,
            'family': family
        })
    except Exception as e:
        logger.error(f"Error getting family {family_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/families', methods=['POST'])
def create_family():
    """Create a new family."""
    try:
        data = request.get_json()
        
        if not data or 'id' not in data or 'name' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: id, name'
            }), 400
        
        family_id = storage.create_family(data)
        
        return jsonify({
            'success': True,
            'family_id': family_id,
            'message': f"Family {data['name']} created successfully"
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating family: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chat', methods=['POST'])
@async_route
async def chat():
    """
    Main chat endpoint for conversational AI interaction.
    
    Request body:
    {
        "message": "Plan meals for this week",
        "family_id": "sharma_001",
        "session_id": "optional-session-id"
    }
    
    Response:
    {
        "success": true,
        "response": "AI response text",
        "session_id": "session-id-for-continuity",
        "timestamp": "2024-01-15T10:30:00"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data or 'family_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: message, family_id'
            }), 400
        
        user_message = data['message']
        family_id = data['family_id']
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        logger.info(f"Chat request from family {family_id}: {user_message[:100]}")
        
        # Get family profile for dietary restrictions
        family_profile = storage.get_family(family_id)
        dietary_restrictions = family_profile.get('dietary_restrictions', []) if family_profile else []
        preferred_cuisines = family_profile.get('preferred_cuisines', []) if family_profile else []
        
        # Call orchestrator with proper parameters
        response = await orchestrator.handle_request(
            user_request=user_message,
            family_id=family_id,
            num_days=7,
            dietary_restrictions=dietary_restrictions,
            preferences={"cuisine": preferred_cuisines},
            week_start_date=datetime.now().strftime('%Y-%m-%d')
        )
        
        # Extract response text
        if hasattr(response, 'text'):
            response_text = response.text
        elif isinstance(response, str):
            response_text = response
        else:
            response_text = str(response)
        
        return jsonify({
            'success': True,
            'response': response_text,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/meal-plan', methods=['POST'])
@async_route
async def plan_meals():
    """
    Plan daily or weekly meals.
    
    Request body:
    {
        "family_id": "sharma_001",
        "start_date": "2024-01-15",
        "days": 7,
        "preferences": "quick meals for busy week"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'family_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: family_id'
            }), 400
        
        family_id = data['family_id']
        start_date = data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        days = data.get('days', 7)
        preferences = data.get('preferences', '')
        
        # Get family profile for dietary restrictions
        family_profile = storage.get_family(family_id)
        dietary_restrictions = family_profile.get('dietary_restrictions', []) if family_profile else []
        preferred_cuisines = family_profile.get('preferred_cuisines', []) if family_profile else []
        
        # Create request for orchestrator
        if days == 1:
            message = f"Plan meals for {start_date}. {preferences}"
        else:
            message = f"Plan meals for {days} days starting {start_date}. {preferences}"
        
        response = await orchestrator.handle_request(
            user_request=message,
            family_id=family_id,
            num_days=days,
            dietary_restrictions=dietary_restrictions,
            preferences={"cuisine": preferred_cuisines, "quick_meals": "quick" in preferences.lower()},
            week_start_date=start_date
        )
        
        # Extract response
        if hasattr(response, 'text'):
            response_text = response.text
        else:
            response_text = str(response)
        
        return jsonify({
            'success': True,
            'meal_plan': response_text,
            'family_id': family_id,
            'start_date': start_date,
            'days': days,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error planning meals: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/shopping-list', methods=['POST'])
@async_route
async def create_shopping_list():
    """
    Create shopping list for meal plan.
    
    Request body:
    {
        "family_id": "sharma_001",
        "recipes": ["Poha", "Dal Tadka", "Paneer Butter Masala"]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'family_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: family_id'
            }), 400
        
        family_id = data['family_id']
        recipes = data.get('recipes', [])
        
        # Get family profile
        family_profile = storage.get_family(family_id)
        dietary_restrictions = family_profile.get('dietary_restrictions', []) if family_profile else []
        preferred_cuisines = family_profile.get('preferred_cuisines', []) if family_profile else []
        
        if recipes:
            recipes_text = ", ".join(recipes)
            message = f"Create shopping list for these recipes: {recipes_text}"
        else:
            message = "Create a shopping list for this week's meal plan"
        
        response = await orchestrator.handle_request(
            user_request=message,
            family_id=family_id,
            num_days=7,
            dietary_restrictions=dietary_restrictions,
            preferences={"cuisine": preferred_cuisines},
            week_start_date=datetime.now().strftime('%Y-%m-%d')
        )
        
        # Extract response
        if hasattr(response, 'text'):
            response_text = response.text
        else:
            response_text = str(response)
        
        return jsonify({
            'success': True,
            'shopping_list': response_text,
            'family_id': family_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error creating shopping list: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/schedule', methods=['POST'])
@async_route
async def plan_schedule():
    """
    Plan weekly schedule with activities.
    
    Request body:
    {
        "family_id": "sharma_001",
        "start_date": "2024-01-15",
        "special_events": ["Birthday on Wednesday"]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'family_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: family_id'
            }), 400
        
        family_id = data['family_id']
        start_date = data.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        special_events = data.get('special_events', [])
        
        # Get family profile
        family_profile = storage.get_family(family_id)
        dietary_restrictions = family_profile.get('dietary_restrictions', []) if family_profile else []
        preferred_cuisines = family_profile.get('preferred_cuisines', []) if family_profile else []
        
        # Create request
        events_text = ", ".join(special_events) if special_events else "none"
        message = f"Plan weekly schedule starting {start_date}. Special events: {events_text}"
        
        response = await orchestrator.handle_request(
            user_request=message,
            family_id=family_id,
            num_days=7,
            dietary_restrictions=dietary_restrictions,
            preferences={"cuisine": preferred_cuisines},
            week_start_date=start_date
        )
        
        # Extract response
        if hasattr(response, 'text'):
            response_text = response.text
        else:
            response_text = str(response)
        
        return jsonify({
            'success': True,
            'schedule': response_text,
            'family_id': family_id,
            'start_date': start_date,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error planning schedule: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recipes/search', methods=['POST'])
@async_route
async def search_recipes():
    """
    Search for recipes.
    
    Request body:
    {
        "meal_type": "breakfast",
        "dietary": "vegetarian",
        "query": "quick and healthy"
    }
    """
    try:
        data = request.get_json()
        
        meal_type = data.get('meal_type', 'any')
        dietary = data.get('dietary', '')
        query = data.get('query', '')
        
        # Use default family or create temporary context
        family_id = data.get('family_id', 'sharma_001')
        
        # Get family profile
        family_profile = storage.get_family(family_id)
        dietary_restrictions = family_profile.get('dietary_restrictions', []) if family_profile else []
        if dietary:
            dietary_restrictions.append(dietary)
        preferred_cuisines = family_profile.get('preferred_cuisines', []) if family_profile else []
        
        # Create search request
        message = f"Find {meal_type} recipes that are {dietary} {query}"
        
        response = await orchestrator.handle_request(
            user_request=message,
            family_id=family_id,
            num_days=7,
            dietary_restrictions=dietary_restrictions,
            preferences={"cuisine": preferred_cuisines},
            week_start_date=datetime.now().strftime('%Y-%m-%d')
        )
        
        # Extract response
        if hasattr(response, 'text'):
            response_text = response.text
        else:
            response_text = str(response)
        
        return jsonify({
            'success': True,
            'recipes': response_text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error searching recipes: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested API endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    logger.info("Starting MomsHelperAI Flask API server...")
    
    # Check if API key is configured
    if not Config.GOOGLE_API_KEY:
        print("\n" + "="*70)
        print("WARNING: GOOGLE_API_KEY not configured!")
        print("="*70)
        print("Please set GOOGLE_API_KEY in .env file")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        print("="*70 + "\n")
    else:
        logger.info(f"API Key configured: {Config.GOOGLE_API_KEY[:10]}...")
    
    print("\n" + "="*70)
    print("MOMSHELPERAI - Flask REST API")
    print("="*70)
    print("Using Google ADK with Gemini 2.0 Flash")
    print("\nAvailable endpoints:")
    print("  GET  /health                    - Health check")
    print("  GET  /api/families              - List all families")
    print("  GET  /api/families/<id>         - Get family details")
    print("  POST /api/families              - Create new family")
    print("  POST /api/chat                  - Chat with AI (main endpoint)")
    print("  POST /api/meal-plan             - Plan meals")
    print("  POST /api/shopping-list         - Create shopping list")
    print("  POST /api/schedule              - Plan weekly schedule")
    print("  POST /api/recipes/search        - Search recipes")
    print("="*70)
    print("\nServer starting on http://localhost:5000")
    print("Press CTRL+C to stop\n")
    
    # Run Flask app
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False  # Use False by default for stability
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"\nError starting server: {e}")
        print("Make sure port 5000 is not already in use.\n")
