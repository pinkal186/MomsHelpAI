"""
Test API Endpoints - Tests all Flask API endpoints for MomsHelperAI
Run this with: python test_api_endpoints.py
"""

import requests
import json
from datetime import datetime
import time

# Configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_FAMILY_ID = "sharma_001"

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(test_name, status, message=""):
    """Print test result with color coding."""
    status_symbol = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    print(f"{status_symbol} {test_name}")
    if message:
        print(f"  {YELLOW}→{RESET} {message}")

def print_header(text):
    """Print section header."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def test_health_endpoint():
    """Test GET /health endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print_test("Health Check Endpoint", True, f"Service: {data.get('service')}, Version: {data.get('version')}")
                return True
        
        print_test("Health Check Endpoint", False, f"Status code: {response.status_code}")
        return False
    except requests.exceptions.ConnectionError:
        print_test("Health Check Endpoint", False, "Cannot connect to server. Is it running?")
        return False
    except Exception as e:
        print_test("Health Check Endpoint", False, str(e))
        return False

def test_get_families():
    """Test GET /api/families endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/families", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                count = data.get('count', 0)
                print_test("Get All Families", True, f"Found {count} families")
                return True
        
        print_test("Get All Families", False, f"Status code: {response.status_code}")
        return False
    except Exception as e:
        print_test("Get All Families", False, str(e))
        return False

def test_get_family_by_id():
    """Test GET /api/families/<family_id> endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/families/{TEST_FAMILY_ID}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                family = data.get('family', {})
                print_test("Get Family By ID", True, f"Family ID: {family.get('family_id')}")
                return True
        elif response.status_code == 404:
            print_test("Get Family By ID", True, f"Family {TEST_FAMILY_ID} not found (expected)")
            return True
        
        print_test("Get Family By ID", False, f"Status code: {response.status_code}")
        return False
    except Exception as e:
        print_test("Get Family By ID", False, str(e))
        return False

def test_create_family():
    """Test POST /api/families endpoint."""
    try:
        family_data = {
            "id": "test_family_001",
            "name": "Test Family",
            "members": [
                {"name": "John", "age": 35},
                {"name": "Jane", "age": 32},
                {"name": "Kid", "age": 8}
            ],
            "dietary_restrictions": ["vegetarian"],
            "preferred_cuisines": ["Indian"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/families",
            json=family_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print_test("Create Family", True, f"Created: {data.get('family_id')}")
                return True
        
        print_test("Create Family", False, f"Status code: {response.status_code}")
        return False
    except Exception as e:
        print_test("Create Family", False, str(e))
        return False

def test_chat_endpoint():
    """Test POST /api/chat endpoint."""
    try:
        chat_data = {
            "message": "Plan meals for this week",
            "family_id": TEST_FAMILY_ID
        }
        
        print(f"  {YELLOW}Note: This may take 30-60 seconds...{RESET}")
        
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"},
            timeout=120  # Longer timeout for AI processing
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                response_text = data.get('response', '')[:100]
                print_test("Chat Endpoint", True, f"Response: {response_text}...")
                return True
        
        data = response.json()
        error = data.get('error', 'Unknown error')
        print_test("Chat Endpoint", False, f"Error: {error}")
        return False
    except requests.exceptions.Timeout:
        print_test("Chat Endpoint", False, "Request timed out (>120s)")
        return False
    except Exception as e:
        print_test("Chat Endpoint", False, str(e))
        return False

def test_meal_plan_endpoint():
    """Test POST /api/meal-plan endpoint."""
    try:
        meal_plan_data = {
            "family_id": TEST_FAMILY_ID,
            "start_date": datetime.now().strftime('%Y-%m-%d'),
            "days": 3,
            "preferences": "quick and easy meals"
        }
        
        print(f"  {YELLOW}Note: This may take 30-60 seconds...{RESET}")
        
        response = requests.post(
            f"{BASE_URL}/api/meal-plan",
            json=meal_plan_data,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_test("Meal Plan Endpoint", True, f"Planned {data.get('days')} days")
                return True
        
        data = response.json()
        error = data.get('error', 'Unknown error')
        print_test("Meal Plan Endpoint", False, f"Error: {error}")
        return False
    except requests.exceptions.Timeout:
        print_test("Meal Plan Endpoint", False, "Request timed out (>120s)")
        return False
    except Exception as e:
        print_test("Meal Plan Endpoint", False, str(e))
        return False

def test_shopping_list_endpoint():
    """Test POST /api/shopping-list endpoint."""
    try:
        shopping_data = {
            "family_id": TEST_FAMILY_ID,
            "recipes": ["Poha", "Dal Tadka"]
        }
        
        print(f"  {YELLOW}Note: This may take 30-60 seconds...{RESET}")
        
        response = requests.post(
            f"{BASE_URL}/api/shopping-list",
            json=shopping_data,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_test("Shopping List Endpoint", True, "Shopping list created")
                return True
        
        data = response.json()
        error = data.get('error', 'Unknown error')
        print_test("Shopping List Endpoint", False, f"Error: {error}")
        return False
    except requests.exceptions.Timeout:
        print_test("Shopping List Endpoint", False, "Request timed out (>120s)")
        return False
    except Exception as e:
        print_test("Shopping List Endpoint", False, str(e))
        return False

def test_schedule_endpoint():
    """Test POST /api/schedule endpoint."""
    try:
        schedule_data = {
            "family_id": TEST_FAMILY_ID,
            "start_date": datetime.now().strftime('%Y-%m-%d'),
            "special_events": ["Birthday party on Saturday"]
        }
        
        print(f"  {YELLOW}Note: This may take 30-60 seconds...{RESET}")
        
        response = requests.post(
            f"{BASE_URL}/api/schedule",
            json=schedule_data,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_test("Schedule Endpoint", True, "Weekly schedule created")
                return True
        
        data = response.json()
        error = data.get('error', 'Unknown error')
        print_test("Schedule Endpoint", False, f"Error: {error}")
        return False
    except requests.exceptions.Timeout:
        print_test("Schedule Endpoint", False, "Request timed out (>120s)")
        return False
    except Exception as e:
        print_test("Schedule Endpoint", False, str(e))
        return False

def test_recipe_search_endpoint():
    """Test POST /api/recipes/search endpoint."""
    try:
        search_data = {
            "meal_type": "breakfast",
            "dietary": "vegetarian",
            "query": "quick and healthy",
            "family_id": TEST_FAMILY_ID
        }
        
        print(f"  {YELLOW}Note: This may take 30-60 seconds...{RESET}")
        
        response = requests.post(
            f"{BASE_URL}/api/recipes/search",
            json=search_data,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_test("Recipe Search Endpoint", True, "Recipes found")
                return True
        
        data = response.json()
        error = data.get('error', 'Unknown error')
        print_test("Recipe Search Endpoint", False, f"Error: {error}")
        return False
    except requests.exceptions.Timeout:
        print_test("Recipe Search Endpoint", False, "Request timed out (>120s)")
        return False
    except Exception as e:
        print_test("Recipe Search Endpoint", False, str(e))
        return False

def test_404_endpoint():
    """Test 404 error handling."""
    try:
        response = requests.get(f"{BASE_URL}/api/nonexistent", timeout=5)
        
        if response.status_code == 404:
            data = response.json()
            if not data.get('success'):
                print_test("404 Error Handling", True, "Properly handles unknown endpoints")
                return True
        
        print_test("404 Error Handling", False, f"Expected 404, got {response.status_code}")
        return False
    except Exception as e:
        print_test("404 Error Handling", False, str(e))
        return False

def run_all_tests():
    """Run all endpoint tests."""
    print_header("MomsHelperAI - API Endpoint Tests")
    
    print(f"{YELLOW}Server URL:{RESET} {BASE_URL}")
    print(f"{YELLOW}Test Family ID:{RESET} {TEST_FAMILY_ID}")
    print(f"{YELLOW}Timestamp:{RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Track results
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0
    }
    
    # Basic Endpoints
    print_header("Basic Endpoints")
    tests = [
        ("Health Check", test_health_endpoint),
        ("Get Families", test_get_families),
        ("Get Family By ID", test_get_family_by_id),
        ("Create Family", test_create_family),
        ("404 Error Handling", test_404_endpoint),
    ]
    
    for name, test_func in tests:
        results['total'] += 1
        if test_func():
            results['passed'] += 1
        else:
            results['failed'] += 1
        time.sleep(0.5)  # Small delay between tests
    
    # AI-Powered Endpoints (Optional - can be skipped if no API key)
    print_header("AI-Powered Endpoints (Requires API Key)")
    print(f"{YELLOW}Note: These tests require Google API key and may take time{RESET}\n")
    
    ai_tests = [
        ("Chat Endpoint", test_chat_endpoint),
        ("Meal Plan Endpoint", test_meal_plan_endpoint),
        ("Shopping List Endpoint", test_shopping_list_endpoint),
        ("Schedule Endpoint", test_schedule_endpoint),
        ("Recipe Search Endpoint", test_recipe_search_endpoint),
    ]
    
    skip_ai = input(f"{YELLOW}Run AI endpoint tests? (y/n): {RESET}").lower() != 'y'
    
    if not skip_ai:
        for name, test_func in ai_tests:
            results['total'] += 1
            if test_func():
                results['passed'] += 1
            else:
                results['failed'] += 1
            time.sleep(1)  # Delay between AI tests
    else:
        print(f"{YELLOW}Skipping AI endpoint tests{RESET}\n")
    
    # Summary
    print_header("Test Summary")
    print(f"Total Tests: {results['total']}")
    print(f"{GREEN}Passed: {results['passed']}{RESET}")
    print(f"{RED}Failed: {results['failed']}{RESET}")
    
    if results['failed'] == 0:
        print(f"\n{GREEN}✓ All tests passed!{RESET}\n")
    else:
        print(f"\n{RED}✗ Some tests failed. Check the output above.{RESET}\n")
    
    return results

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Starting API Endpoint Tests")
    print("="*70)
    print(f"\n{YELLOW}Make sure the Flask server is running on {BASE_URL}{RESET}")
    print(f"{YELLOW}Run: python app.py{RESET}\n")
    
    input(f"{YELLOW}Press Enter when server is ready...{RESET}")
    
    try:
        results = run_all_tests()
        exit(0 if results['failed'] == 0 else 1)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Tests interrupted by user{RESET}\n")
        exit(1)
    except Exception as e:
        print(f"\n\n{RED}Test runner error: {e}{RESET}\n")
        exit(1)
