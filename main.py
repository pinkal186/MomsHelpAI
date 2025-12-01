"""
MomsHelperAI - Main CLI Application
Uses Google ADK with InMemoryRunner for interactive family planning
"""

import asyncio
import sys
from datetime import datetime
from typing import Optional
import uuid

from agents.orchestrator import orchestrator
from storage.sqlite_storage import SQLiteStorage
from storage.chroma_storage import ChromaStorage
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MomsHelperCLI:
    """
    Interactive CLI for MomsHelperAI using Google ADK.
    
    Features:
    - Natural language conversation with orchestrator
    - Session persistence for multi-turn interactions
    - Human-in-the-loop (HITL) workflow for approvals
    - Sample family data loaded on startup
    """
    
    def __init__(self):
        """Initialize CLI with storage and orchestrator."""
        self.storage = SQLiteStorage()
        self.chroma = ChromaStorage()
        self.session_id = str(uuid.uuid4())
        self.current_family_id = None
        
        logger.info("MomsHelperAI CLI initialized")
    
    def print_banner(self):
        """Print welcome banner."""
        print("\n" + "="*70)
        print("MOMSHELPERAI - Your AI Family Planning Assistant")
        print("="*70)
        print("Using Google ADK with Gemini 2.0 Flash")
        print(f"Session ID: {self.session_id[:8]}...")
        print("="*70 + "\n")
    
    def print_help(self):
        """Print available commands."""
        print("\n" + "="*70)
        print("Available Commands:")
        print("="*70)
        print("  help              - Show this help message")
        print("  family <id>       - Select family by ID (e.g., 'family sharma_001')")
        print("  families          - List all families in database")
        print("  quit / exit       - Exit application")
        print("\nNatural Language Requests (examples):")
        print("="*70)
        print("  'Plan meals for this week'")
        print("  'Create a shopping list for Diwali party'")
        print("  'Schedule activities for next weekend'")
        print("  'Find vegetarian breakfast recipes'")
        print("  'Plan a birthday party for 20 guests'")
        print("="*70 + "\n")
    
    async def load_sample_data(self):
        """Load sample family data if database is empty."""
        try:
            families = self.storage.get_all_families()
            
            if not families:
                print("Loading sample family data...")
                
                # Sample Sharma family
                sharma_family = {
                    'id': 'sharma_001',
                    'name': 'Sharma Family',
                    'members': [
                        {'name': 'Rajesh', 'age': 38, 'role': 'father'},
                        {'name': 'Priya', 'age': 35, 'role': 'mother'},
                        {'name': 'Aarav', 'age': 10, 'role': 'son'},
                        {'name': 'Ananya', 'age': 7, 'role': 'daughter'}
                    ],
                    'dietary_restrictions': ['vegetarian'],
                    'preferred_cuisines': ['North Indian', 'South Indian', 'Gujarati'],
                    'allergies': [],
                    'spice_level': 'medium',
                    'meal_timing': {
                        'breakfast': '08:00',
                        'lunch': '13:00',
                        'dinner': '20:00'
                    }
                }
                
                self.storage.create_family(sharma_family)
                self.current_family_id = 'sharma_001'
                
                print("Sample family 'Sharma' loaded (ID: sharma_001)")
                print(f"   Members: {len(sharma_family['members'])} (Rajesh, Priya, Aarav, Ananya)")
                print(f"   Dietary: Vegetarian")
                
            else:
                print(f"Found {len(families)} families in database")
                self.current_family_id = families[0]['id']
                print(f"   Default family: {families[0]['name']} (ID: {self.current_family_id})")
            
            # Load sample recipes into ChromaDB
            print("Loading sample recipes into ChromaDB...")
            self.chroma.initialize_sample_recipes()
            print("Recipe database ready")
            
        except Exception as e:
            logger.error(f"Error loading sample data: {str(e)}")
            print(f"Warning: Could not load sample data: {str(e)}")
    
    def list_families(self):
        """List all families in database."""
        try:
            families = self.storage.get_all_families()
            
            if not families:
                print("\nNo families found in database")
                return
            
            print(f"\nFamilies in Database ({len(families)}):")
            print("="*70)
            
            for family in families:
                print(f"\nID: {family['id']}")
                print(f"Name: {family['name']}")
                print(f"Members: {len(family.get('members', []))}")
                print(f"Dietary: {', '.join(family.get('dietary_restrictions', ['none']))}")
                if family['id'] == self.current_family_id:
                    print("CURRENTLY SELECTED")
                print("="*70)
                
        except Exception as e:
            logger.error(f"Error listing families: {str(e)}")
            print(f"Error: {str(e)}")
    
    def select_family(self, family_id: str):
        """Select a family by ID."""
        try:
            family = self.storage.get_family(family_id)
            
            if not family:
                print(f"Family '{family_id}' not found")
                return
            
            self.current_family_id = family_id
            print(f"\nSelected family: {family['name']} (ID: {family_id})")
            print(f"   Members: {len(family.get('members', []))}")
            print(f"   Dietary: {', '.join(family.get('dietary_restrictions', ['none']))}")
            
        except Exception as e:
            logger.error(f"Error selecting family: {str(e)}")
            print(f"Error: {str(e)}")
    
    async def process_request(self, user_input: str):
        """
        Process user request through orchestrator.
        
        Args:
            user_input: Natural language request from user
        """
        if not self.current_family_id:
            print("Please select a family first (use 'families' to list available families)")
            return
        
        print(f"\nProcessing request for {self.current_family_id}...")
        print("This may take a moment as AI agents work together...\n")
        
        try:
            # Call orchestrator with family context
            response = await orchestrator.handle_request(
                user_request=user_input,
                family_id=self.current_family_id,
                session_id=self.session_id
            )
            
            # Display response
            print("="*70)
            print("MomsHelperAI Response:")
            print("="*70)
            
            # Extract text from response
            if hasattr(response, 'text'):
                print(response.text)
            elif isinstance(response, str):
                print(response)
            else:
                print(str(response))
            
            print("="*70 + "\n")
            
            # HITL: Ask for user approval
            approval = input("Is this plan acceptable? (yes/no/modify): ").strip().lower()
            
            if approval == 'yes':
                print("Great! Plan approved and saved.")
            elif approval == 'no':
                print("Plan rejected. Please provide more details for a better plan.")
            elif approval == 'modify':
                modification = input("What would you like to change? ")
                print(f"\nModifying plan based on: {modification}")
                # Re-process with modification
                await self.process_request(f"{user_input} - MODIFICATION: {modification}")
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            print(f"\nError: {str(e)}")
            print("Please try again or rephrase your request.\n")
    
    async def run(self):
        """Run the interactive CLI."""
        self.print_banner()
        
        # Load sample data
        await self.load_sample_data()
        
        print("\nType 'help' for available commands")
        print("Or just ask me anything in natural language!\n")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Process commands
                if user_input.lower() in ['quit', 'exit']:
                    print("\nGoodbye! Thanks for using MomsHelperAI")
                    break
                
                elif user_input.lower() == 'help':
                    self.print_help()
                
                elif user_input.lower() == 'families':
                    self.list_families()
                
                elif user_input.lower().startswith('family '):
                    family_id = user_input.split(' ', 1)[1].strip()
                    self.select_family(family_id)
                
                else:
                    # Process as natural language request
                    await self.process_request(user_input)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! Thanks for using MomsHelperAI")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                print(f"\nUnexpected error: {str(e)}\n")


async def main():
    """Main entry point."""
    try:
        cli = MomsHelperCLI()
        await cli.run()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the async CLI
    asyncio.run(main())
