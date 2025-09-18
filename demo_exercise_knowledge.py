#!/usr/bin/env python3
"""
Demo script to test Weaviate exercise knowledge integration.

This script demonstrates how the exercise knowledge base can be used
to enhance activity parsing and provide semantic search capabilities.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from exercise_knowledge import ExerciseKnowledgeBase

async def demo_exercise_knowledge():
    """Demonstrate exercise knowledge base functionality."""
    print("🏃 Strava Activity Agent - Exercise Knowledge Demo")
    print("=" * 50)
    
    # Initialize the exercise knowledge base
    print("\n1. Initializing Exercise Knowledge Base...")
    # Try different ports in case 8080 is occupied
    for port in [8081, 8082, 8080]:
        try:
            kb = ExerciseKnowledgeBase(weaviate_url=f"http://localhost:{port}")
            if kb.client:
                print(f"✅ Connected to Weaviate on port {port}")
                break
        except:
            continue
    else:
        kb = ExerciseKnowledgeBase()  # Try default
    
    if not kb.client:
        print("❌ Weaviate not available. This demo requires Weaviate to be running.")
        print("   You can run Weaviate locally with Docker:")
        print("   docker run -p 8081:8080 -p 50051:50051 cr.weaviate.io/semitechnologies/weaviate:1.26.1")
        print("   (Note: Using port 8081 since 8080 might be in use)")
        return
    
    print("✅ Exercise Knowledge Base initialized successfully!")
    
    # Demo search queries
    test_queries = [
        "I went running",
        "did some lifting at the gym", 
        "yoga session",
        "bike ride",
        "swimming laps",
        "crossfit workout",
        "trail hiking",
        "spinning class",
        "pilates",
        "marathon training"
    ]
    
    print("\n2. Testing Exercise Term Search...")
    print("-" * 40)
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        results = kb.search_exercises(query, limit=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['name']} (Strava: {result['sport_type']})")
                print(f"      Score: {result.get('score', 'N/A'):.3f}")
                if result.get('keywords'):
                    print(f"      Keywords: {', '.join(result['keywords'][:5])}")
        else:
            print("   No matches found.")
    
    print("\n3. Testing Sport Type Suggestions...")
    print("-" * 40)
    
    sport_types = ["Run", "Ride", "WeightTraining", "Yoga", "Swim"]
    
    for sport_type in sport_types:
        suggestions = kb.get_exercise_suggestions(sport_type)
        print(f"\n🏃 {sport_type} suggestions:")
        
        if suggestions:
            for suggestion in suggestions[:2]:  # Show top 2
                print(f"   • {suggestion['name']}")
                if suggestion.get('keywords'):
                    print(f"     Keywords: {', '.join(suggestion['keywords'][:3])}")
        else:
            print("   No suggestions available.")
    
    print("\n4. Testing Context Enhancement...")
    print("-" * 40)
    
    test_contexts = [
        ("Run", {"location": "park", "time_of_day": "morning"}),
        ("WeightTraining", {"location": "gym", "intensity": "high"}),
        ("Yoga", {"location": "studio", "feeling": "relaxed"})
    ]
    
    for sport_type, context in test_contexts:
        enhanced = kb.enhance_activity_context(sport_type, context)
        print(f"\n🔧 Enhanced context for {sport_type}:")
        print(f"   Original: {context}")
        print(f"   Enhanced: {enhanced}")
    
    print("\n5. Demo Complete! 🎉")
    print("=" * 50)
    print("The exercise knowledge base is ready to enhance your Strava activities!")
    print("It can help with:")
    print("• Better sport type detection from natural language")
    print("• Rich context enhancement with exercise-specific knowledge")
    print("• Semantic search for exercise terms and concepts")
    print("• Improved AI prompt generation with relevant terminology")
    
    # Close the connection
    kb.close()

if __name__ == "__main__":
    asyncio.run(demo_exercise_knowledge())