"""
Exercise Knowledge Base using Weaviate

This module provides semantic search capabilities for exercise terms, activities,
and fitness knowledge to enhance activity parsing and suggestions.
"""

import os
import logging
from typing import Dict, List, Optional, Any
import weaviate
from weaviate.classes.init import Auth
import json

logger = logging.getLogger(__name__)

class ExerciseKnowledgeBase:
    """Weaviate-powered exercise knowledge base for semantic search."""
    
    def __init__(self, weaviate_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the Exercise Knowledge Base.
        
        Args:
            weaviate_url: Weaviate instance URL (defaults to local)
            api_key: Weaviate API key for cloud instances
        """
        self.weaviate_url = weaviate_url or os.getenv('WEAVIATE_URL', 'http://localhost:8081')
        self.api_key = api_key or os.getenv('WEAVIATE_API_KEY')
        
        try:
            # Initialize Weaviate client
            if self.api_key:
                self.client = weaviate.connect_to_weaviate_cloud(
                    cluster_url=self.weaviate_url,
                    auth_credentials=Auth.api_key(self.api_key)
                )
            else:
                # Parse the URL to extract just the host and port
                if self.weaviate_url.startswith('http://'):
                    host_part = self.weaviate_url.replace('http://', '')
                elif self.weaviate_url.startswith('https://'):
                    host_part = self.weaviate_url.replace('https://', '')
                else:
                    host_part = self.weaviate_url
                
                # Split host and port if present
                if ':' in host_part:
                    host, port = host_part.split(':')
                    port = int(port)
                else:
                    host = host_part
                    port = 8080
                
                self.client = weaviate.connect_to_local(host=host, port=port)
            
            logger.info("Connected to Weaviate successfully")
            
            # Initialize the exercise schema
            self._setup_schema()
            
            # Populate with initial exercise data if empty
            self._populate_initial_data()
            
        except Exception as e:
            logger.warning(f"Failed to connect to Weaviate: {e}. Exercise knowledge features disabled.")
            self.client = None
    
    def _setup_schema(self):
        """Set up the exercise knowledge schema in Weaviate."""
        if not self.client:
            return
            
        try:
            # Check if collection already exists
            if self.client.collections.exists("Exercise"):
                logger.info("Exercise collection already exists")
                return
            
            # Create Exercise collection
            exercise_collection = self.client.collections.create(
                name="Exercise",
                description="Exercise and fitness activity knowledge base",
                properties=[
                    {
                        "name": "name",
                        "dataType": ["text"],
                        "description": "Primary name of the exercise"
                    },
                    {
                        "name": "sport_type",
                        "dataType": ["text"],
                        "description": "Strava sport type category"
                    },
                    {
                        "name": "synonyms",
                        "dataType": ["text[]"],
                        "description": "Alternative names and synonyms"
                    },
                    {
                        "name": "description",
                        "dataType": ["text"],
                        "description": "Description of the exercise"
                    },
                    {
                        "name": "muscle_groups",
                        "dataType": ["text[]"],
                        "description": "Primary muscle groups worked"
                    },
                    {
                        "name": "equipment",
                        "dataType": ["text[]"],
                        "description": "Equipment needed"
                    },
                    {
                        "name": "intensity_level",
                        "dataType": ["text"],
                        "description": "Typical intensity (low, moderate, high, variable)"
                    },
                    {
                        "name": "location_types",
                        "dataType": ["text[]"],
                        "description": "Where this exercise is typically done"
                    },
                    {
                        "name": "keywords",
                        "dataType": ["text[]"],
                        "description": "Related keywords and terms"
                    }
                ]
            )
            
            logger.info("Exercise collection created successfully")
            
        except Exception as e:
            logger.error(f"Failed to set up Weaviate schema: {e}")
    
    def _populate_initial_data(self):
        """Populate the knowledge base with initial exercise data."""
        if not self.client:
            return
            
        try:
            collection = self.client.collections.get("Exercise")
            
            # Check if data already exists
            if collection.aggregate.over_all(total_count=True).total_count > 0:
                logger.info("Exercise data already exists")
                return
            
            # Initial exercise data
            exercises = [
                {
                    "name": "Running",
                    "sport_type": "Run",
                    "synonyms": ["jogging", "sprinting", "trail running", "road running", "treadmill running"],
                    "description": "Cardiovascular exercise involving rapid foot movement",
                    "muscle_groups": ["legs", "core", "cardiovascular"],
                    "equipment": ["running shoes", "treadmill", "track"],
                    "intensity_level": "variable",
                    "location_types": ["outdoor", "gym", "track", "trail", "park"],
                    "keywords": ["cardio", "endurance", "pace", "distance", "marathon", "5k", "10k"]
                },
                {
                    "name": "Cycling",
                    "sport_type": "Ride",
                    "synonyms": ["biking", "road cycling", "mountain biking", "spinning", "indoor cycling"],
                    "description": "Pedaling a bicycle for exercise and transportation",
                    "muscle_groups": ["legs", "core", "cardiovascular"],
                    "equipment": ["bicycle", "helmet", "cycling shoes", "spin bike"],
                    "intensity_level": "variable",
                    "location_types": ["outdoor", "gym", "road", "trail", "mountain"],
                    "keywords": ["pedaling", "gear", "cadence", "hills", "speed", "distance"]
                },
                {
                    "name": "Swimming",
                    "sport_type": "Swim",
                    "synonyms": ["freestyle", "backstroke", "breaststroke", "butterfly", "laps"],
                    "description": "Aquatic exercise using arm and leg movements",
                    "muscle_groups": ["full body", "arms", "legs", "core", "cardiovascular"],
                    "equipment": ["swimsuit", "goggles", "pool", "fins"],
                    "intensity_level": "variable",
                    "location_types": ["pool", "ocean", "lake", "indoor pool", "outdoor pool"],
                    "keywords": ["laps", "stroke", "water", "aquatic", "endurance"]
                },
                {
                    "name": "Weight Training",
                    "sport_type": "WeightTraining",
                    "synonyms": ["strength training", "resistance training", "lifting", "bodybuilding", "powerlifting"],
                    "description": "Exercise using weights to build strength and muscle",
                    "muscle_groups": ["variable", "arms", "legs", "chest", "back", "shoulders"],
                    "equipment": ["dumbbells", "barbells", "machines", "plates", "bench"],
                    "intensity_level": "high",
                    "location_types": ["gym", "home gym", "fitness center"],
                    "keywords": ["reps", "sets", "weight", "muscle", "strength", "gains", "iron"]
                },
                {
                    "name": "Yoga",
                    "sport_type": "Yoga",
                    "synonyms": ["hot yoga", "vinyasa", "hatha", "bikram", "power yoga", "stretching"],
                    "description": "Mind-body practice combining poses, breathing, and meditation",
                    "muscle_groups": ["full body", "core", "flexibility"],
                    "equipment": ["yoga mat", "blocks", "straps"],
                    "intensity_level": "variable",
                    "location_types": ["studio", "home", "park", "beach"],
                    "keywords": ["poses", "asanas", "flexibility", "mindfulness", "balance", "meditation"]
                },
                {
                    "name": "Hiking",
                    "sport_type": "Hike",
                    "synonyms": ["trekking", "trail walking", "mountain hiking", "nature walking"],
                    "description": "Walking in natural environments, often on trails",
                    "muscle_groups": ["legs", "core", "cardiovascular"],
                    "equipment": ["hiking boots", "backpack", "poles", "water"],
                    "intensity_level": "variable",
                    "location_types": ["trail", "mountain", "forest", "park", "nature"],
                    "keywords": ["trail", "elevation", "nature", "outdoor", "adventure", "summit"]
                },
                {
                    "name": "Walking",
                    "sport_type": "Walk",
                    "synonyms": ["power walking", "speed walking", "casual walking", "strolling"],
                    "description": "Basic locomotion exercise at various intensities",
                    "muscle_groups": ["legs", "cardiovascular"],
                    "equipment": ["walking shoes", "comfortable clothing"],
                    "intensity_level": "low",
                    "location_types": ["anywhere", "park", "neighborhood", "treadmill"],
                    "keywords": ["steps", "pace", "casual", "leisure", "recovery"]
                },
                {
                    "name": "Rowing",
                    "sport_type": "Rowing",
                    "synonyms": ["crew", "sculling", "ergometer", "rowing machine"],
                    "description": "Full-body exercise using rowing motion",
                    "muscle_groups": ["full body", "back", "arms", "legs", "core"],
                    "equipment": ["rowing machine", "boat", "oars"],
                    "intensity_level": "high",
                    "location_types": ["gym", "water", "indoor"],
                    "keywords": ["stroke", "catch", "drive", "recovery", "split time"]
                }
            ]
            
            # Insert exercise data
            with collection.batch.dynamic() as batch:
                for exercise in exercises:
                    batch.add_object(exercise)
            
            logger.info(f"Populated knowledge base with {len(exercises)} exercises")
            
        except Exception as e:
            logger.error(f"Failed to populate exercise data: {e}")
    
    def search_exercises(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for exercises using semantic similarity.
        
        Args:
            query: Search query (exercise description, keywords, etc.)
            limit: Maximum number of results to return
            
        Returns:
            List of matching exercises with similarity scores
        """
        if not self.client:
            logger.warning("Weaviate not available, returning empty results")
            return []
        
        try:
            collection = self.client.collections.get("Exercise")
            
            # Perform hybrid search (keyword + semantic)
            response = collection.query.hybrid(
                query=query,
                limit=limit,
                return_metadata=["score"]
            )
            
            results = []
            for obj in response.objects:
                result = {
                    "name": obj.properties.get("name"),
                    "sport_type": obj.properties.get("sport_type"),
                    "synonyms": obj.properties.get("synonyms", []),
                    "description": obj.properties.get("description"),
                    "muscle_groups": obj.properties.get("muscle_groups", []),
                    "equipment": obj.properties.get("equipment", []),
                    "intensity_level": obj.properties.get("intensity_level"),
                    "location_types": obj.properties.get("location_types", []),
                    "keywords": obj.properties.get("keywords", []),
                    "score": obj.metadata.score if hasattr(obj.metadata, 'score') else 0.0
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} exercise matches for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search exercises: {e}")
            return []
    
    def get_exercise_suggestions(self, sport_type: str) -> List[Dict[str, Any]]:
        """
        Get exercise suggestions for a specific sport type.
        
        Args:
            sport_type: Strava sport type
            
        Returns:
            List of exercises matching the sport type
        """
        if not self.client:
            return []
        
        try:
            collection = self.client.collections.get("Exercise")
            
            response = collection.query.where(
                ["sport_type"],
                ["Equal", sport_type],
                limit=10
            )
            
            suggestions = []
            for obj in response.objects:
                suggestion = {
                    "name": obj.properties.get("name"),
                    "description": obj.properties.get("description"),
                    "keywords": obj.properties.get("keywords", []),
                    "equipment": obj.properties.get("equipment", []),
                    "location_types": obj.properties.get("location_types", [])
                }
                suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get exercise suggestions: {e}")
            return []
    
    def enhance_activity_context(self, sport_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance activity context with exercise knowledge.
        
        Args:
            sport_type: Type of sport/exercise
            context: Existing context dictionary
            
        Returns:
            Enhanced context with additional exercise information
        """
        if not self.client:
            return context
        
        try:
            # Get exercise information
            suggestions = self.get_exercise_suggestions(sport_type)
            
            if suggestions:
                exercise = suggestions[0]  # Use the first/best match
                
                # Enhance context with exercise knowledge
                enhanced_context = context.copy()
                
                # Add exercise-specific keywords if not already present
                if not enhanced_context.get("keywords"):
                    enhanced_context["exercise_keywords"] = exercise.get("keywords", [])
                
                # Add equipment information if location suggests it
                if enhanced_context.get("location") and exercise.get("equipment"):
                    location = enhanced_context["location"].lower()
                    equipment = exercise.get("equipment", [])
                    
                    # Try to match location with equipment
                    for equip in equipment:
                        if any(word in location for word in equip.lower().split()):
                            enhanced_context["equipment"] = equip
                            break
                
                # Add muscle group information for better descriptions
                enhanced_context["muscle_groups"] = exercise.get("muscle_groups", [])
                
                # Add intensity information if not present
                if not enhanced_context.get("intensity"):
                    enhanced_context["intensity"] = exercise.get("intensity_level")
                
                logger.info(f"Enhanced context for {sport_type} with exercise knowledge")
                return enhanced_context
            
        except Exception as e:
            logger.error(f"Failed to enhance activity context: {e}")
        
        return context
    
    def close(self):
        """Close the Weaviate client connection."""
        if self.client:
            try:
                self.client.close()
                logger.info("Weaviate client connection closed")
            except Exception as e:
                logger.error(f"Error closing Weaviate client: {e}")