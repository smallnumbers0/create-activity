"""
Strava Activity Agent

This module provides the main agent that combines Writer AI and Strava API
to create intelligent, AI-generated activity descriptions and manage Strava activities.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dotenv import load_dotenv

from .writer_client import WriterAPIClient
from .strava_client import StravaAPIClient
from .exercise_knowledge import ExerciseKnowledgeBase

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class StravaActivityAgent:
    """
    Main agent that combines Writer AI and Strava API functionality
    to create and manage Strava activities with AI-generated content.
    """
    
    def __init__(
        self,
        writer_api_key: Optional[str] = None,
        writer_model: str = "palmyra-x5",
        strava_client_id: Optional[str] = None,
        strava_client_secret: Optional[str] = None,
        strava_redirect_uri: Optional[str] = None,
        weaviate_url: Optional[str] = None,
        weaviate_api_key: Optional[str] = None
    ):
        """
        Initialize the Strava Activity Agent.
        
        Args:
            writer_api_key: Writer AI API key (defaults to WRITER_API_KEY env var)
            writer_model: Writer AI model to use (defaults to palmyra-x5)
            strava_client_id: Strava client ID (defaults to STRAVA_CLIENT_ID env var)
            strava_client_secret: Strava client secret (defaults to STRAVA_CLIENT_SECRET env var)
            strava_redirect_uri: OAuth redirect URI (defaults to STRAVA_REDIRECT_URI env var)
            weaviate_url: Weaviate instance URL (defaults to WEAVIATE_URL env var)
            weaviate_api_key: Weaviate API key (defaults to WEAVIATE_API_KEY env var)
        """
        # Initialize Writer client
        self.writer_api_key = writer_api_key or os.getenv('WRITER_API_KEY')
        if not self.writer_api_key:
            raise ValueError("Writer API key is required. Set WRITER_API_KEY environment variable or pass it explicitly.")
        
        self.writer_client = WriterAPIClient(
            api_key=self.writer_api_key,
            model=writer_model or os.getenv('WRITER_MODEL', 'palmyra-x5')
        )
        
        # Initialize Strava client
        self.strava_client_id = strava_client_id or os.getenv('STRAVA_CLIENT_ID')
        self.strava_client_secret = strava_client_secret or os.getenv('STRAVA_CLIENT_SECRET')
        self.strava_redirect_uri = strava_redirect_uri or os.getenv('STRAVA_REDIRECT_URI')
        
        if not all([self.strava_client_id, self.strava_client_secret, self.strava_redirect_uri]):
            raise ValueError("Strava credentials are required. Set STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, and STRAVA_REDIRECT_URI environment variables.")
        
        self.strava_client = StravaAPIClient(
            client_id=self.strava_client_id,
            client_secret=self.strava_client_secret,
            redirect_uri=self.strava_redirect_uri
        )
        
        # Initialize Exercise Knowledge Base
        self.exercise_kb = ExerciseKnowledgeBase(
            weaviate_url=weaviate_url,
            api_key=weaviate_api_key
        )
        
        logger.info("Strava Activity Agent initialized successfully with exercise knowledge base")
    
    def search_exercise_terms(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for exercise terms and related concepts using the knowledge base.
        
        Args:
            query: Search query for exercise terms
            limit: Maximum number of results to return
            
        Returns:
            List of exercise matches with related terms and concepts
        """
        try:
            return self.exercise_kb.search_exercises(query, limit)
        except Exception as e:
            logger.error(f"Failed to search exercise terms: {e}")
            return []
    
    def get_exercise_suggestions_for_sport(self, sport_type: str) -> List[Dict[str, Any]]:
        """
        Get exercise suggestions and terminology for a specific sport type.
        
        Args:
            sport_type: Strava sport type
            
        Returns:
            List of related exercises and terminology
        """
        try:
            return self.exercise_kb.get_exercise_suggestions(sport_type)
        except Exception as e:
            logger.error(f"Failed to get exercise suggestions: {e}")
            return []
    
    def get_strava_auth_url(self, scopes: Optional[List[str]] = None) -> str:
        """
        Get the Strava OAuth authorization URL.
        
        Args:
            scopes: List of OAuth scopes to request
            
        Returns:
            Authorization URL
        """
        return self.strava_client.get_authorization_url(scopes)
    
    def authenticate_strava(self, authorization_code: str) -> Dict[str, Any]:
        """
        Complete Strava OAuth authentication.
        
        Args:
            authorization_code: Authorization code from OAuth callback
            
        Returns:
            Token response from Strava
        """
        return self.strava_client.exchange_token(authorization_code)
    
    def set_strava_tokens(self, access_token: str, refresh_token: str, expires_at: int):
        """
        Set Strava tokens manually.
        
        Args:
            access_token: The access token
            refresh_token: The refresh token
            expires_at: Token expiration timestamp
        """
        self.strava_client.set_tokens(access_token, refresh_token, expires_at)
    
    def create_activity_with_ai(
        self,
        activity_data: Dict[str, Any],
        generate_description: bool = True,
        generate_name: bool = False,
        description_style: str = "motivational"
    ) -> Dict[str, Any]:
        """
        Create a Strava activity with AI-generated content.
        
        Args:
            activity_data: Base activity data (name, type, duration, etc.)
            generate_description: Whether to generate AI description
            generate_name: Whether to generate AI name (overrides provided name)
            description_style: Style for AI description (motivational, casual, technical, humorous)
            
        Returns:
            Created activity data from Strava
        """
        # Make a copy to avoid modifying the original
        enhanced_activity = activity_data.copy()
        
        # Generate AI name if requested
        if generate_name:
            try:
                ai_name = self.writer_client.generate_activity_name(activity_data)
                enhanced_activity['name'] = ai_name
                logger.info(f"Generated AI name: {ai_name}")
            except Exception as e:
                logger.warning(f"Failed to generate AI name, using provided/default: {e}")
        
        # Generate AI description if requested
        if generate_description:
            try:
                ai_description = self.writer_client.generate_activity_description(
                    activity_data, 
                    style=description_style
                )
                enhanced_activity['description'] = ai_description
                logger.info(f"Generated AI description: {ai_description}")
            except Exception as e:
                logger.warning(f"Failed to generate AI description: {e}")
                enhanced_activity['description'] = "Great workout! 💪"
        
        # Ensure required fields are present
        if 'name' not in enhanced_activity:
            enhanced_activity['name'] = f"{enhanced_activity.get('sport_type', 'Activity')} Session"
        
        # Set default start time if not provided
        if 'start_date_local' not in enhanced_activity:
            enhanced_activity['start_date_local'] = datetime.now().isoformat()
        
        # Create the activity on Strava
        try:
            created_activity = self.strava_client.create_activity(enhanced_activity)
            logger.info(f"Successfully created activity with ID: {created_activity.get('id')}")
            return created_activity
        except Exception as e:
            logger.error(f"Failed to create activity on Strava: {e}")
            raise
    
    def update_activity_with_ai(
        self,
        activity_id: int,
        updates: Optional[Dict[str, Any]] = None,
        regenerate_description: bool = False,
        regenerate_name: bool = False,
        description_style: str = "motivational"
    ) -> Dict[str, Any]:
        """
        Update a Strava activity with AI-generated content.
        
        Args:
            activity_id: ID of the activity to update
            updates: Additional updates to apply
            regenerate_description: Whether to regenerate the description with AI
            regenerate_name: Whether to regenerate the name with AI
            description_style: Style for AI description
            
        Returns:
            Updated activity data from Strava
        """
        if updates is None:
            updates = {}
        
        # Get existing activity data for AI generation
        if regenerate_description or regenerate_name:
            try:
                existing_activity = self.strava_client.get_activity(activity_id)
                
                # Generate new name if requested
                if regenerate_name:
                    ai_name = self.writer_client.generate_activity_name(existing_activity)
                    updates['name'] = ai_name
                    logger.info(f"Generated new AI name: {ai_name}")
                
                # Generate new description if requested
                if regenerate_description:
                    ai_description = self.writer_client.generate_activity_description(
                        existing_activity,
                        style=description_style
                    )
                    updates['description'] = ai_description
                    logger.info(f"Generated new AI description: {ai_description}")
                    
            except Exception as e:
                logger.error(f"Failed to fetch activity for AI generation: {e}")
                # Continue with manual updates only
        
        if not updates:
            raise ValueError("No updates provided")
        
        # Update the activity on Strava
        try:
            updated_activity = self.strava_client.update_activity(activity_id, updates)
            logger.info(f"Successfully updated activity {activity_id}")
            return updated_activity
        except Exception as e:
            logger.error(f"Failed to update activity {activity_id}: {e}")
            raise
    
    def create_quick_activity(
        self,
        sport_type: str,
        duration_minutes: int,
        distance_km: Optional[float] = None,
        name: Optional[str] = None,
        description_style: str = "motivational"
    ) -> Dict[str, Any]:
        """
        Create a quick activity with minimal input.
        
        Args:
            sport_type: Type of sport (Run, Ride, Swim, etc.)
            duration_minutes: Duration in minutes
            distance_km: Distance in kilometers (optional)
            name: Activity name (will generate if not provided)
            description_style: Style for AI description
            
        Returns:
            Created activity data
        """
        activity_data = {
            'sport_type': sport_type,
            'elapsed_time': duration_minutes * 60,  # Convert to seconds
            'start_date_local': datetime.now().isoformat()
        }
        
        if distance_km:
            activity_data['distance'] = distance_km * 1000  # Convert to meters
        
        if name:
            activity_data['name'] = name
        
        return self.create_activity_with_ai(
            activity_data=activity_data,
            generate_description=True,
            generate_name=not bool(name),  # Generate name only if not provided
            description_style=description_style
        )
    
    def get_athlete_profile(self) -> Dict[str, Any]:
        """
        Get the authenticated athlete's profile.
        
        Returns:
            Athlete profile data
        """
        return self.strava_client.get_athlete()
    
    def get_recent_activities(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent activities for the authenticated athlete.
        
        Args:
            count: Number of activities to retrieve
            
        Returns:
            List of recent activities
        """
        return self.strava_client.get_activities(per_page=count)
    
    def enhance_activity_description(
        self,
        activity_id: int,
        style: str = "motivational"
    ) -> str:
        """
        Generate and apply an enhanced AI description to an existing activity.
        
        Args:
            activity_id: ID of the activity to enhance
            style: Style for the description
            
        Returns:
            The generated description
        """
        try:
            # Get the activity data
            activity = self.strava_client.get_activity(activity_id)
            
            # Generate new description
            new_description = self.writer_client.generate_activity_description(
                activity, 
                style=style
            )
            
            # Update the activity
            self.strava_client.update_activity(
                activity_id,
                {'description': new_description}
            )
            
            logger.info(f"Enhanced description for activity {activity_id}")
            return new_description
            
        except Exception as e:
            logger.error(f"Failed to enhance activity description: {e}")
            raise

    async def parse_activity_prompt(self, prompt: str) -> Dict[str, Any]:
        """Parse a natural language prompt to extract activity details using AI with exercise knowledge enhancement."""
        try:
            # First, use exercise knowledge base to enhance understanding
            exercise_matches = self.exercise_kb.search_exercises(prompt)
            
            # Build enhanced context for AI prompt
            enhanced_context = ""
            if exercise_matches:
                top_exercise = exercise_matches[0]
                enhanced_context = f"""
Based on exercise knowledge, this appears to be related to:
- Exercise: {top_exercise['name']} (Strava type: {top_exercise['sport_type']})
- Keywords: {', '.join(top_exercise.get('keywords', []))}
- Equipment: {', '.join(top_exercise.get('equipment', []))}
- Typical locations: {', '.join(top_exercise.get('location_types', []))}
"""

            system_prompt = f"""You are an expert fitness activity parser enhanced with exercise knowledge. Parse the user's natural language description and extract structured activity data with rich context.

{enhanced_context}

CRITICAL: You MUST return ONLY a valid JSON object. Do not include any explanatory text, markdown formatting, or code blocks. Just pure JSON.

Return this exact JSON structure:
{{
    "sport_type": "one of: Run, Ride, Swim, Hike, Walk, WeightTraining, Yoga, CrossCountrySkiing, Rowing, Elliptical",
    "duration_minutes": number (required),
    "distance_km": number or null (optional),
    "name": null,
    "description_style": "one of: motivational, casual, technical, humorous",
    "confidence": number between 0-1,
    "context": {{
        "location": "string or null",
        "time_of_day": "string or null",
        "weather": "string or null",
        "feeling": "string or null",
        "companions": "string or null",
        "intensity": "string or null",
        "equipment": "string or null",
        "goals": "string or null",
        "achievements": "string or null",
        "challenges": "string or null",
        "route": "string or null",
        "music": "string or null",
        "nutrition": "string or null",
        "recovery": "string or null",
        "highlights": "string or null"
    }}
}}

Examples:
"I went for a 30 minute run this morning in the park, felt great!" 
{{"sport_type": "Run", "duration_minutes": 30, "distance_km": null, "name": null, "description_style": "casual", "confidence": 0.9, "context": {{"location": "park", "time_of_day": "morning", "feeling": "felt great", "route": "park", "companions": "alone"}}}}

"Did a tough 5k bike ride for 25 minutes, windy but pushed through!" 
{{"sport_type": "Ride", "duration_minutes": 25, "distance_km": 5, "name": null, "description_style": "motivational", "confidence": 0.95, "context": {{"intensity": "tough", "weather": "windy", "challenges": "windy conditions", "achievements": "pushed through despite wind"}}}}

Return ONLY the JSON object for this prompt:"""

            response = await self.writer_client.client.post(
                "/v1/chat/completions",
                json={
                    "model": "palmyra-x5",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 800,
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"} if hasattr(self, 'supports_json_mode') else None
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                try:
                    ai_response = response.json()
                    if "choices" not in ai_response or len(ai_response["choices"]) == 0:
                        logger.error(f"Invalid AI response structure: {ai_response}")
                        return {"status": "error", "message": "AI returned invalid response structure"}
                    
                    content = ai_response["choices"][0]["message"]["content"].strip()
                    logger.info(f"AI response content: {content}")
                    
                    if not content:
                        logger.error("AI returned empty content")
                        return {"status": "error", "message": "AI returned empty response"}
                    
                    # Try to parse the JSON response
                    try:
                        import json
                        # Clean up common JSON formatting issues
                        content_cleaned = content.strip()
                        if content_cleaned.startswith('```json'):
                            content_cleaned = content_cleaned.replace('```json', '').replace('```', '').strip()
                        
                        parsed_data = json.loads(content_cleaned)
                        
                        # Validate required fields
                        if not isinstance(parsed_data.get("duration_minutes"), (int, float)) or parsed_data["duration_minutes"] <= 0:
                            raise ValueError("Invalid duration_minutes")
                        
                        # Set defaults for missing fields
                        parsed_data.setdefault("description_style", "casual")
                        parsed_data.setdefault("confidence", 0.5)
                        parsed_data.setdefault("context", {})
                        
                        # Enhance with exercise knowledge
                        if exercise_matches:
                            sport_type = parsed_data.get("sport_type")
                            enhanced_context = self.exercise_kb.enhance_activity_context(sport_type, parsed_data["context"])
                            parsed_data["context"] = enhanced_context
                            
                            # Add exercise knowledge metadata
                            parsed_data["exercise_knowledge"] = {
                                "matched_exercise": exercise_matches[0]["name"],
                                "confidence_score": exercise_matches[0]["score"],
                                "suggested_keywords": exercise_matches[0].get("keywords", [])
                            }
                        
                        return {
                            "status": "success",
                            "parsed_data": parsed_data,
                            "original_prompt": prompt
                        }
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse AI response as JSON: {content}")
                        # Try to extract basic info with regex as fallback
                        return await self._fallback_parse_prompt(prompt)
                        
                except Exception as e:
                    logger.error(f"Error processing AI response: {str(e)}")
                    return await self._fallback_parse_prompt(prompt)
                    
            else:
                logger.error(f"Writer API error: {response.status_code} - {await response.atext()}")
                return await self._fallback_parse_prompt(prompt)
                
        except Exception as e:
            logger.error(f"Error parsing activity prompt: {str(e)}")
            return await self._fallback_parse_prompt(prompt)

    async def _fallback_parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """Fallback method to parse prompts when AI fails, enhanced with exercise knowledge."""
        import re
        
        try:
            prompt_lower = prompt.lower()
            
            # Extract duration with regex
            duration_match = re.search(r'(\d+)\s*(?:minute|min|hr|hour)', prompt_lower)
            if not duration_match:
                return {"status": "error", "message": "Could not find duration in your description. Please include how long you exercised (e.g., '30 minutes')."}
            
            duration = int(duration_match.group(1))
            if 'hour' in duration_match.group(0) or 'hr' in duration_match.group(0):
                duration *= 60  # Convert hours to minutes
            
            # Extract distance if present
            distance = None
            distance_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:km|k|mile)', prompt_lower)
            if distance_match:
                distance = float(distance_match.group(1))
                if 'mile' in distance_match.group(0):
                    distance *= 1.609  # Convert miles to km
            
            # Use exercise knowledge base to determine sport type
            exercise_matches = self.exercise_kb.search_exercises(prompt)
            sport_type = "Run"  # Default
            
            if exercise_matches:
                # Use the best match from exercise knowledge
                top_match = exercise_matches[0]
                sport_type = top_match["sport_type"]
                logger.info(f"Exercise knowledge suggested sport type: {sport_type} for prompt: {prompt}")
            else:
                # Fallback to keyword matching
                if any(word in prompt_lower for word in ['bike', 'cycling', 'cycle', 'rode']):
                    sport_type = "Ride"
                elif any(word in prompt_lower for word in ['swim', 'swimming', 'pool']):
                    sport_type = "Swim"
                elif any(word in prompt_lower for word in ['hike', 'hiking', 'trail']):
                    sport_type = "Hike"
                elif any(word in prompt_lower for word in ['walk', 'walking']):
                    sport_type = "Walk"
                elif any(word in prompt_lower for word in ['yoga', 'stretching']):
                    sport_type = "Yoga"
                elif any(word in prompt_lower for word in ['weight', 'lifting', 'gym', 'strength']):
                    sport_type = "WeightTraining"
                elif any(word in prompt_lower for word in ['rowing', 'row']):
                    sport_type = "Rowing"
                elif any(word in prompt_lower for word in ['ski', 'skiing']):
                    sport_type = "CrossCountrySkiing"
                elif any(word in prompt_lower for word in ['elliptical']):
                    sport_type = "Elliptical"
            
            # Extract basic context
            context = {}
            if any(word in prompt_lower for word in ['morning', 'am']):
                context['time_of_day'] = 'morning'
            elif any(word in prompt_lower for word in ['evening', 'night', 'pm']):
                context['time_of_day'] = 'evening'
            elif any(word in prompt_lower for word in ['afternoon']):
                context['time_of_day'] = 'afternoon'
            
            if any(word in prompt_lower for word in ['park', 'outdoor', 'outside']):
                context['location'] = 'outdoor'
            elif any(word in prompt_lower for word in ['gym', 'indoor']):
                context['location'] = 'gym'
            
            if any(word in prompt_lower for word in ['felt great', 'amazing', 'awesome', 'fantastic']):
                context['feeling'] = 'great'
            elif any(word in prompt_lower for word in ['tough', 'hard', 'difficult', 'challenging']):
                context['feeling'] = 'challenging'
            
            # Enhance context with exercise knowledge if available
            if exercise_matches:
                enhanced_context = self.exercise_kb.enhance_activity_context(sport_type, context)
                context = enhanced_context
            
            parsed_data = {
                "sport_type": sport_type,
                "duration_minutes": duration,
                "distance_km": distance,
                "name": None,
                "description_style": "casual",
                "confidence": 0.3,  # Lower confidence for fallback parsing
                "context": context
            }
            
            # Add exercise knowledge metadata if available
            if exercise_matches:
                parsed_data["exercise_knowledge"] = {
                    "matched_exercise": exercise_matches[0]["name"],
                    "confidence_score": exercise_matches[0]["score"],
                    "suggested_keywords": exercise_matches[0].get("keywords", []),
                    "fallback_method": True
                }
            
            return {
                "status": "success",
                "parsed_data": parsed_data,
                "original_prompt": prompt,
                "method": "fallback_with_exercise_knowledge"
            }
            
        except Exception as e:
            logger.error(f"Error in fallback parsing: {str(e)}")
            return {"status": "error", "message": f"Failed to parse activity: {str(e)}"}

    async def create_activity_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Create a Strava activity from a natural language prompt."""
        try:
            # First, parse the prompt to extract activity details
            parse_result = await self.parse_activity_prompt(prompt)
            
            if parse_result["status"] != "success":
                return parse_result
            
            parsed_data = parse_result["parsed_data"]
            
            # Validate confidence level
            if parsed_data.get("confidence", 0) < 0.3:
                return {
                    "status": "error", 
                    "message": "Unable to understand the activity details from your prompt. Please be more specific about the activity type and duration."
                }
            
            # Create activity using parsed data
            result = await self.create_quick_activity_with_ai(
                sport_type=parsed_data["sport_type"],
                duration_minutes=int(parsed_data["duration_minutes"]),
                distance_km=parsed_data.get("distance_km"),
                name=parsed_data.get("name"),
                description_style=parsed_data.get("description_style", "casual"),
                context=parsed_data.get("context", {})
            )
            
            # Add parsing information to the result
            if result["status"] == "success":
                result["parsing_info"] = {
                    "original_prompt": prompt,
                    "parsed_data": parsed_data,
                    "confidence": parsed_data.get("confidence", 0)
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating activity from prompt: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def create_quick_activity_with_ai(self, sport_type: str, duration_minutes: int, 
                                           distance_km: Optional[float] = None, 
                                           name: Optional[str] = None,
                                           description_style: str = "motivational",
                                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a Strava activity with AI-generated content (async version)."""
        try:
            if context is None:
                context = {}
                
            # Generate AI-powered name if not provided
            if not name:
                name = await self.writer_client.generate_activity_name_with_context(
                    sport_type, duration_minutes, distance_km, context
                )
            
            # Generate AI-powered description
            description = await self.writer_client.generate_activity_description_with_context(
                sport_type, duration_minutes, distance_km, description_style, context
            )
            
            # Create the activity on Strava
            activity_data = {
                "name": name,
                "sport_type": sport_type,
                "start_date_local": datetime.now().isoformat(),
                "elapsed_time": duration_minutes * 60,  # Convert to seconds
                "description": description,
                "trainer": False,
                "commute": False
            }
            
            if distance_km:
                activity_data["distance"] = distance_km * 1000  # Convert to meters
            
            activity = self.strava_client.create_activity(activity_data)
            
            return {
                "status": "success",
                "activity": activity,
                "ai_generated": {
                    "name": name,
                    "description": description
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating activity with AI: {str(e)}")
            return {"status": "error", "message": str(e)}