"""
Writer AI API Client

This module provides a client for interacting with the Writer AI chat completion API.
"""

import requests
import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WriterMessage:
    """Represents a message in the Writer chat completion."""
    role: str  # "user", "assistant", or "system"
    content: str

class WriterAPIClient:
    """Client for interacting with the Writer AI API."""
    
    def __init__(self, api_key: str, model: str = "palmyra-x5"):
        """
        Initialize the Writer API client.
        
        Args:
            api_key: Your Writer API key
            model: The model to use for completions (default: palmyra-x5)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.writer.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        # Initialize async client
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers)
    
    def chat_completion(
        self,
        messages: List[WriterMessage],
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
        top_p: Optional[float] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Create a chat completion using the Writer API.
        
        Args:
            messages: List of messages forming the conversation
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0 to 2.0)
            top_p: Nucleus sampling threshold
            stream: Whether to stream the response
            
        Returns:
            API response containing the completion
            
        Raises:
            Exception: If the API request fails
        """
        # Convert messages to the format expected by the API
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "stream": stream
        }
        
        # Add optional parameters if provided
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        
        try:
            logger.info(f"Making chat completion request to Writer API with model {self.model}")
            response = requests.post(
                f"{self.base_url}/chat",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info("Successfully received response from Writer API")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Writer API request failed: {e}")
            raise Exception(f"Failed to get response from Writer API: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Writer API response: {e}")
            raise Exception(f"Invalid JSON response from Writer API: {e}")
    
    def generate_activity_description(
        self,
        activity_data: Dict[str, Any],
        style: str = "motivational"
    ) -> str:
        """
        Generate an engaging description for a Strava activity using Writer AI.
        
        Args:
            activity_data: Dictionary containing activity information
            style: Style of description to generate (motivational, casual, technical, humorous)
            
        Returns:
            Generated activity description
        """
        # Extract relevant activity information
        activity_type = activity_data.get("sport_type", activity_data.get("type", "Activity"))
        distance = activity_data.get("distance")
        elapsed_time = activity_data.get("elapsed_time")
        name = activity_data.get("name", "")
        
        # Build context for the AI
        context_parts = [f"Activity type: {activity_type}"]
        
        if distance:
            # Convert distance from meters to more readable units
            if distance >= 1000:
                distance_km = distance / 1000
                context_parts.append(f"Distance: {distance_km:.2f} km")
            else:
                context_parts.append(f"Distance: {distance} meters")
        
        if elapsed_time:
            # Convert elapsed time to hours and minutes
            hours = elapsed_time // 3600
            minutes = (elapsed_time % 3600) // 60
            if hours > 0:
                context_parts.append(f"Duration: {hours}h {minutes}m")
            else:
                context_parts.append(f"Duration: {minutes} minutes")
        
        if name:
            context_parts.append(f"Activity name: {name}")
        
        activity_context = ", ".join(context_parts)
        
        # Create the prompt based on style
        style_instructions = {
            "motivational": "Create an inspiring and motivational description that celebrates the achievement and encourages continued fitness.",
            "casual": "Write a relaxed, friendly description as if sharing with friends on social media.",
            "technical": "Generate a detailed, data-focused description highlighting performance metrics and technical aspects.",
            "humorous": "Create a fun, lighthearted description with some humor while still being encouraging."
        }
        
        instruction = style_instructions.get(style, style_instructions["motivational"])
        
        system_prompt = f"""You are a fitness enthusiast and social media expert who creates engaging Strava activity descriptions. 
{instruction}

Guidelines:
- Keep it concise (50-150 words)
- Be authentic and relatable
- Include relevant emojis
- Avoid being overly boastful
- Make it engaging for social media
- Don't repeat the activity name unless adding context"""

        user_prompt = f"""Create an engaging Strava activity description for this workout:

{activity_context}

Make it {style} in tone and include 2-3 relevant emojis."""

        messages = [
            WriterMessage(role="system", content=system_prompt),
            WriterMessage(role="user", content=user_prompt)
        ]
        
        try:
            response = self.chat_completion(
                messages=messages,
                max_tokens=200,
                temperature=0.8
            )
            
            # Extract the generated description
            if "choices" in response and len(response["choices"]) > 0:
                description = response["choices"][0]["message"]["content"].strip()
                logger.info(f"Generated activity description: {description}")
                return description
            else:
                logger.error("No choices in Writer API response")
                return "Great workout! 💪 Another step towards fitness goals! 🎯"
                
        except Exception as e:
            logger.error(f"Failed to generate activity description: {e}")
            # Return a fallback description
            return "Great workout! 💪 Another step towards fitness goals! 🎯"

    def generate_activity_name(self, activity_data: Dict[str, Any]) -> str:
        """
        Generate a creative name for a Strava activity.
        
        Args:
            activity_data: Dictionary containing activity information
            
        Returns:
            Generated activity name
        """
        activity_type = activity_data.get("sport_type", activity_data.get("type", "Activity"))
        distance = activity_data.get("distance")
        elapsed_time = activity_data.get("elapsed_time")
        
        # Build context
        context_parts = [f"Activity type: {activity_type}"]
        
        if distance and distance >= 1000:
            distance_km = distance / 1000
            context_parts.append(f"Distance: {distance_km:.1f}km")
        
        if elapsed_time:
            minutes = elapsed_time // 60
            context_parts.append(f"Duration: {minutes} minutes")
        
        activity_context = ", ".join(context_parts)
        
        system_prompt = """You are a creative fitness enthusiast who creates catchy, memorable names for workout activities.
Create short, engaging activity names that are:
- 2-6 words long
- Creative but not too quirky
- Appropriate for social media
- Reflect the activity type and effort"""

        user_prompt = f"""Create a catchy name for this workout:

{activity_context}

Give me just the name, no extra text or quotes."""

        messages = [
            WriterMessage(role="system", content=system_prompt),
            WriterMessage(role="user", content=user_prompt)
        ]
        
        try:
            response = self.chat_completion(
                messages=messages,
                max_tokens=50,
                temperature=1.0
            )
            
            if "choices" in response and len(response["choices"]) > 0:
                name = response["choices"][0]["message"]["content"].strip()
                # Remove quotes if present
                name = name.strip('"\'')
                logger.info(f"Generated activity name: {name}")
                return name
            else:
                return f"{activity_type} Session"
                
        except Exception as e:
            logger.error(f"Failed to generate activity name: {e}")
            return f"{activity_type} Session"

    async def generate_activity_description_async(
        self, 
        sport_type: str, 
        duration_minutes: int, 
        distance_km: Optional[float] = None,
        style: str = "motivational"
    ) -> str:
        """Generate an activity description using AI (async version)."""
        try:
            # Build activity context
            activity_context = f"Activity Type: {sport_type}\nDuration: {duration_minutes} minutes"
            if distance_km:
                activity_context += f"\nDistance: {distance_km} km"
            
            # Style-specific prompts
            style_prompts = {
                "motivational": "Create an inspiring and motivational description that celebrates the achievement and encourages future workouts.",
                "casual": "Write a relaxed, friendly description like you're telling a friend about your workout.",
                "technical": "Provide a detailed, data-focused description with specific metrics and performance notes.",
                "humorous": "Write a funny, lighthearted description that brings a smile while describing the workout."
            }
            
            system_prompt = f"""You are a fitness enthusiast creating workout descriptions. {style_prompts.get(style, style_prompts['motivational'])}

Keep descriptions under 200 characters. Use relevant emojis. Be authentic and engaging."""

            user_prompt = f"""Create a {style} description for this workout:

{activity_context}

Write just the description, no extra text."""

            response = await self.client.post(
                "/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 100,
                    "temperature": 0.9
                }
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    description = response_data["choices"][0]["message"]["content"].strip()
                    # Remove quotes if present
                    description = description.strip('"\'')
                    logger.info(f"Generated activity description: {description}")
                    return description
            
            # Fallback description
            return f"Great {sport_type.lower()} session! 💪 Completed {duration_minutes} minutes of awesome training."
                
        except Exception as e:
            logger.error(f"Failed to generate activity description: {e}")
            return f"Great {sport_type.lower()} session! 💪 Completed {duration_minutes} minutes of awesome training."

    async def generate_activity_name_async(
        self, 
        sport_type: str, 
        duration_minutes: int, 
        distance_km: Optional[float] = None
    ) -> str:
        """Generate a funny, joke-based activity name using AI (async version)."""
        # Build activity context
        activity_context = f"Activity Type: {sport_type}\nDuration: {duration_minutes} minutes"
        if distance_km:
            activity_context += f"\nDistance: {distance_km} km"
        
        system_prompt = """You are a hilarious fitness comedian who creates funny, witty activity names that make people smile. Your job is to turn workout descriptions into entertaining, joke-based titles.

Create names that are:
- FUNNY and clever (puns, wordplay, humor)
- Activity-relevant (relate to the sport/workout)
- Positive and motivational through humor
- Concise (under 60 characters)
- Include relevant emojis
- Clean and appropriate humor

Examples:
- "Why I Run: Zombies Can't Catch Me 🧟‍♂️🏃‍♂️"
- "Two Wheels, Too Tired 🚴‍♂️😴"
- "Making Waves & Bad Jokes 🌊😂"
- "Pretzel Mode: Activated 🥨🧘‍♀️"
- "Lifting My Spirits (And Weights) 💪😄"

Be creative and make it genuinely funny!"""

        user_prompt = f"""Create a hilarious, joke-based name for this workout:

{activity_context}

Give me just the funny name with emojis, no extra text or quotes."""

        try:
            response = await self.client.post(
                "/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 70,
                    "temperature": 1.2
                }
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    name = response_data["choices"][0]["message"]["content"].strip()
                    # Remove quotes if present
                    name = name.strip('"\'')
                    logger.info(f"Generated joke activity name: {name}")
                    return name
            
            # Fallback funny names
            fallback_jokes = {
                "Run": "Running Late (But On Purpose) 🏃‍♂️⏰",
                "Ride": "Wheely Good Workout 🚴‍♂️😄",
                "Swim": "Just Keep Swimming (Thanks Dory) 🐠🏊‍♂️",
                "Hike": "Taking a Walk on the Wild Side 🥾🌲",
                "Walk": "Walking My Way to Greatness 🚶‍♂️✨",
                "WeightTraining": "Pumping Iron & Dad Jokes 🏋️‍♂️😂",
                "Yoga": "Finding My Inner Peace (& Outer Pretzel) 🧘‍♀️🥨",
                "CrossCountrySkiing": "Ski-ing My Way to Fitness ⛷️😄",
                "Rowing": "Row, Row, Row Your Gains 🚣‍♂️💪",
                "Elliptical": "Going Nowhere Fast (But Loving It) 🔄😅"
            }
            
            return fallback_jokes.get(sport_type, f"{sport_type} & Giggles 😄💪")
                
        except Exception as e:
            logger.error(f"Failed to generate joke activity name: {e}")
            return f"{sport_type} Comedy Hour 😂💪"

    async def generate_activity_description_with_context(
        self, 
        sport_type: str, 
        duration_minutes: int, 
        distance_km: Optional[float] = None,
        style: str = "motivational",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate an activity description using AI with rich context (async version)."""
        try:
            if context is None:
                context = {}
            
            # Build rich activity context
            activity_context = f"Activity Type: {sport_type}\nDuration: {duration_minutes} minutes"
            if distance_km:
                activity_context += f"\nDistance: {distance_km} km"
            
            # Add rich context details
            context_details = []
            if context.get("location"):
                context_details.append(f"Location: {context['location']}")
            if context.get("time_of_day"):
                context_details.append(f"Time: {context['time_of_day']}")
            if context.get("weather"):
                context_details.append(f"Weather: {context['weather']}")
            if context.get("feeling"):
                context_details.append(f"Feeling: {context['feeling']}")
            if context.get("companions"):
                context_details.append(f"With: {context['companions']}")
            if context.get("intensity"):
                context_details.append(f"Intensity: {context['intensity']}")
            if context.get("equipment"):
                context_details.append(f"Equipment/Setting: {context['equipment']}")
            if context.get("achievements"):
                context_details.append(f"Achievement: {context['achievements']}")
            if context.get("challenges"):
                context_details.append(f"Challenges: {context['challenges']}")
            if context.get("route"):
                context_details.append(f"Route: {context['route']}")
            if context.get("goals"):
                context_details.append(f"Goals: {context['goals']}")
            if context.get("highlights"):
                context_details.append(f"Highlights: {context['highlights']}")
            if context.get("music"):
                context_details.append(f"Entertainment: {context['music']}")
            if context.get("nutrition"):
                context_details.append(f"Nutrition: {context['nutrition']}")
            if context.get("recovery"):
                context_details.append(f"Recovery: {context['recovery']}")
            
            if context_details:
                activity_context += f"\n\nAdditional Context:\n" + "\n".join(context_details)
            
            # Style-specific prompts
            style_prompts = {
                "motivational": "Create an inspiring and motivational description that celebrates the achievement and encourages future workouts. Highlight personal victories and progress.",
                "casual": "Write a relaxed, friendly description like you're telling a friend about your workout. Keep it conversational and authentic.",
                "technical": "Provide a detailed, data-focused description with specific metrics and performance notes. Include technical observations.",
                "humorous": "Write a funny, lighthearted description that brings a smile while describing the workout. Use humor appropriately."
            }
            
            system_prompt = f"""You are a fitness enthusiast creating detailed workout descriptions. {style_prompts.get(style, style_prompts['motivational'])}

Use ALL the provided context to create a rich, personalized description that tells the story of this specific workout. Include:
- The setting and environment
- How they felt during and after
- Any challenges overcome
- Personal achievements or milestones
- Weather or external conditions
- Who they were with or if solo
- Equipment used or route taken

Keep descriptions under 280 characters but make them vivid and personal. Use relevant emojis. Be authentic and engaging."""

            user_prompt = f"""Create a {style} description for this workout using ALL the context provided:

{activity_context}

Write a detailed, personalized description that captures the full experience, not just basic stats."""

            response = await self.client.post(
                "/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 150,
                    "temperature": 0.8
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        description = response_data["choices"][0]["message"]["content"].strip()
                        # Remove quotes if present
                        description = description.strip('"\'')
                        logger.info(f"Generated contextual activity description: {description}")
                        return description
                except Exception as e:
                    logger.error(f"Error parsing description response: {e}")
            else:
                logger.error(f"Writer API error for description: {response.status_code} - {response.text}")
            
            # Fallback description with basic context
            fallback_parts = [f"Great {sport_type.lower()} session! 💪 {duration_minutes} minutes"]
            if context.get("location"):
                fallback_parts.append(f"at {context['location']}")
            if context.get("feeling"):
                fallback_parts.append(f"- {context['feeling']}!")
            
            return " ".join(fallback_parts)
                
        except Exception as e:
            logger.error(f"Failed to generate contextual activity description: {e}")
            return f"Great {sport_type.lower()} session! 💪 Completed {duration_minutes} minutes of awesome training."

    async def generate_activity_name_with_context(
        self, 
        sport_type: str, 
        duration_minutes: int, 
        distance_km: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a funny, joke-based activity name using AI with context (async version)."""
        try:
            if context is None:
                context = {}
                
            # Build activity context for joke generation
            activity_context = f"Activity Type: {sport_type}\nDuration: {duration_minutes} minutes"
            if distance_km:
                activity_context += f"\nDistance: {distance_km} km"
            
            # Add key context for joke creation
            joke_context = []
            if context.get("time_of_day"):
                joke_context.append(f"Time: {context['time_of_day']}")
            if context.get("location"):
                joke_context.append(f"Location: {context['location']}")
            if context.get("weather"):
                joke_context.append(f"Weather: {context['weather']}")
            if context.get("intensity"):
                joke_context.append(f"Intensity: {context['intensity']}")
            if context.get("achievements"):
                joke_context.append(f"Achievement: {context['achievements']}")
            if context.get("challenges"):
                joke_context.append(f"Challenge: {context['challenges']}")
            if context.get("feeling"):
                joke_context.append(f"Feeling: {context['feeling']}")
            if context.get("equipment"):
                joke_context.append(f"Equipment: {context['equipment']}")
            
            if joke_context:
                activity_context += f"\n\nContext:\n" + "\n".join(joke_context)
        
            system_prompt = """You are a hilarious fitness comedian who creates funny, witty activity names that make people smile. Your job is to turn workout descriptions into entertaining, joke-based titles.

Create names that are:
- FUNNY and clever (puns, wordplay, humor)
- Activity-relevant (relate to the sport/workout)
- Context-aware (use weather, location, feelings, etc. for humor)
- Positive and motivational through humor
- Concise (under 60 characters)
- Include relevant emojis
- Clean and appropriate humor

Comedy styles to use:
- Puns and wordplay related to the activity
- Weather-based humor (if applicable)
- Time-of-day jokes
- Achievement/challenge humor
- Self-deprecating but positive jokes
- Fitness stereotypes (in a fun way)

Examples:
- Running: "Why I Run: Zombies Can't Catch Me 🧟‍♂️🏃‍♂️"
- Cycling: "Two Wheels, Too Tired 🚴‍♂️😴"
- Swimming: "Making Waves & Bad Jokes 🌊😂"
- Yoga: "Pretzel Mode: Activated ��🧘‍♀️"
- Weight Training: "Lifting My Spirits (And Weights) 💪😄"
- Morning run: "Coffee? Nah, Endorphins Will Do ☕➡️🏃‍♂️"
- Rainy workout: "Weathering the Storm (Literally) ⛈️💪"
- First time: "Beginner's Luck or Sheer Determination? ��"

Be creative and make it genuinely funny!"""

            user_prompt = f"""Create a hilarious, joke-based name for this workout:

{activity_context}

Make it funny and relevant to the activity and context. Give me just the joke name with emojis, no extra text or quotes."""

            response = await self.client.post(
                "/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 80,
                    "temperature": 1.2  # Higher temperature for more creative/funny results
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        name = response_data["choices"][0]["message"]["content"].strip()
                        # Remove quotes if present
                        name = name.strip('"\'')
                        logger.info(f"Generated joke activity name: {name}")
                        return name
                except Exception as e:
                    logger.error(f"Error parsing name response: {e}")
            else:
                logger.error(f"Writer API error for name: {response.status_code} - {response.text}")
            
            # Fallback funny names based on activity type
            fallback_jokes = {
                "Run": "Running Late (But On Purpose) 🏃‍♂️⏰",
                "Ride": "Wheely Good Workout 🚴‍♂️😄",
                "Swim": "Just Keep Swimming (Thanks Dory) 🐠🏊‍♂️",
                "Hike": "Taking a Walk on the Wild Side 🥾🌲",
                "Walk": "Walking My Way to Greatness 🚶‍♂️✨",
                "WeightTraining": "Pumping Iron & Dad Jokes 🏋️‍♂️😂",
                "Yoga": "Finding My Inner Peace (& Outer Pretzel) 🧘‍♀️🥨",
                "CrossCountrySkiing": "Ski-ing My Way to Fitness ⛷️😄",
                "Rowing": "Row, Row, Row Your Gains 🚣‍♂️💪",
                "Elliptical": "Going Nowhere Fast (But Loving It) 🔄😅"
            }
            
            return fallback_jokes.get(sport_type, f"{sport_type} & Giggles 😄💪")
                
        except Exception as e:
            logger.error(f"Failed to generate joke activity name: {e}")
            return f"{sport_type} Comedy Hour 😂💪"