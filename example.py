"""
Example script demonstrating how to use the Strava Activity Agent
"""

import os
from datetime import datetime
from src.strava_activity_agent import StravaActivityAgent

def main():
    """
    Example usage of the Strava Activity Agent
    """
    print("🚴‍♂️ Strava Activity Agent Example 🏃‍♀️")
    print("=" * 50)
    
    try:
        # Initialize the agent
        print("Initializing agent...")
        agent = StravaActivityAgent()
        print("✅ Agent initialized successfully!")
        
        # For this example, you would need to manually handle OAuth
        # In a real application, you'd implement the full OAuth flow
        print("\n⚠️  OAuth Setup Required:")
        print("1. Go to https://www.strava.com/settings/api")
        print("2. Create a new application") 
        print("3. Set Authorization Callback Domain to 'localhost'")
        print("4. Copy your credentials to the .env file")
        print("5. Run the web application with: python main.py")
        print("6. Visit http://localhost:8080 to authenticate and create activities")
        
        # Example of how to create an activity (requires authentication first)
        print("\n📝 Example Activity Creation:")
        print("Once authenticated, you can create activities like this:")
        
        # This is just for demonstration - won't work without auth tokens
        example_activity = {
            "name": "Morning Run",  # Optional - AI can generate this
            "sport_type": "Run",
            "elapsed_time": 3600,  # 1 hour in seconds
            "distance": 5000,      # 5km in meters
            "start_date_local": datetime.now().isoformat()
        }
        
        print(f"Activity data: {example_activity}")
        print("\n🤖 AI Features:")
        print("- Generates creative activity names")
        print("- Creates motivational descriptions")
        print("- Supports multiple description styles:")
        print("  • Motivational: Inspiring and encouraging")
        print("  • Casual: Friendly and relaxed")
        print("  • Technical: Data-focused and detailed")
        print("  • Humorous: Fun and lighthearted")
        
        print("\n🌐 Web Interface:")
        print("The easiest way to use this is through the web interface.")
        print("Run: python main.py")
        print("Then visit: http://localhost:8080")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Set up your .env file with API credentials")
        print("2. Installed all dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    main()