"""
FastAPI Web Application for Strava Activity Agent

This module provides a web interface for the Strava Activity Agent,
allowing users to authenticate with Strava and create AI-powered activities.
"""

import os
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from src.strava_activity_agent import StravaActivityAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Strava Activity Agent",
    description="AI-powered Strava activity creation with Writer AI",
    version="1.0.0"
)

# Initialize the agent
try:
    agent = StravaActivityAgent()
    logger.info("Strava Activity Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize agent: {e}")
    agent = None

# Pydantic models for API requests
class PromptActivityRequest(BaseModel):
    prompt: str

class ActivityUpdateRequest(BaseModel):
    updates: Optional[Dict[str, Any]] = None
    regenerate_description: bool = False
    regenerate_name: bool = False
    description_style: str = "motivational"

# Store user sessions (in production, use a proper session store)
user_sessions = {}

def get_daily_joke_title():
    """Generate a daily fitness joke for the title based on the current date."""
    import hashlib
    from datetime import datetime
    
    jokes = [
        "Why don't runners ever get tired of puns? Because they're always running them into the ground! 🏃‍♂️",
        "What do you call a cyclist who doesn't ride bikes? A stand-up comedian! 🚴‍♂️",
        "Why did the swimmer bring a ladder to the pool? Because they heard the pool had deep ends! 🏊‍♂️",
        "What's a runner's favorite type of music? Jog and roll! 🎵",
        "Why don't weightlifters ever get cold? Because they're always pumping iron! 🏋️‍♂️",
        "What do you call a yoga instructor who moonlights as a comedian? A stretch performer! 🧘‍♀️",
        "Why did the hiker break up with the mountain? It was just too rocky! 🥾",
        "What's the difference between a marathon and a joke? One's a long run, the other's a fun run! 😄",
        "Why don't bikes ever get speeding tickets? Because they're two-tired to speed! 🚲",
        "What do you call a workout that's also a breakfast? Eggs-ercise! 🍳",
        "Why did the treadmill go to therapy? It was tired of people running away from their problems! 🏃‍♀️",
        "What's a swimmer's favorite dessert? Pool-ding! 🍮",
        "Why don't fitness trackers ever lie? Because they always step up to the truth! ⌚",
        "What do you call a lazy workout? A rest-ercise! 😴",
        "Why did the gym close down? It just wasn't working out! 💪"
    ]
    
    # Use current date to seed the joke selection (same joke per day)
    today = datetime.now().strftime("%Y-%m-%d")
    joke_hash = int(hashlib.md5(today.encode()).hexdigest(), 16)
    return jokes[joke_hash % len(jokes)]

@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with improved UI and authentication state."""
    is_authenticated = len(user_sessions) > 0
    daily_joke = get_daily_joke_title()
    
    # Get user info if authenticated
    user_name = ""
    if is_authenticated:
        first_session = list(user_sessions.values())[0]
        user_name = first_session.get('athlete', {}).get('firstname', 'Athlete')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Strava Activity Agent - AI-Powered Fitness</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{ 
                max-width: 900px; 
                margin: 0 auto; 
                background: white; 
                padding: 40px; 
                border-radius: 20px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            .header {{
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 2px solid #f0f0f0;
            }}
            h1 {{ 
                color: #fc4c02; 
                font-size: 2.5em;
                margin: 0;
                font-weight: 300;
            }}
            .joke-title {{
                background: linear-gradient(45deg, #ff6b6b, #feca57);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 1.1em;
                margin: 15px 0;
                font-weight: 500;
                min-height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .status-bar {{
                background: {'#d4edda' if is_authenticated else '#fff3cd'};
                color: {'#155724' if is_authenticated else '#856404'};
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
                text-align: center;
                font-weight: 500;
            }}
            .section {{ 
                margin: 30px 0; 
                padding: 25px; 
                border: 1px solid #e0e0e0; 
                border-radius: 15px;
                background: #fafafa;
                transition: all 0.3s ease;
            }}
            .section:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            .hidden {{ display: none; }}
            button {{ 
                background: linear-gradient(45deg, #fc4c02, #ff6b35);
                color: white; 
                padding: 15px 30px; 
                border: none; 
                border-radius: 25px; 
                cursor: pointer; 
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            button:hover {{ 
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(252, 76, 2, 0.4);
            }}
            input, select, textarea {{ 
                padding: 12px; 
                margin: 8px 0; 
                border: 2px solid #ddd; 
                border-radius: 8px;
                width: 100%;
                font-size: 16px;
                transition: border-color 0.3s ease;
            }}
            input:focus, select:focus, textarea:focus {{
                outline: none;
                border-color: #fc4c02;
                box-shadow: 0 0 0 3px rgba(252, 76, 2, 0.1);
            }}
            .form-group {{ margin: 20px 0; }}
            label {{ 
                display: block; 
                margin-bottom: 8px; 
                font-weight: 600;
                color: #333;
            }}
            .description {{ 
                color: #666; 
                margin-bottom: 30px;
                font-size: 1.1em;
                text-align: center;
            }}
            .form-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            @media (max-width: 768px) {{
                .form-grid {{
                    grid-template-columns: 1fr;
                }}
                .container {{
                    padding: 20px;
                    margin: 10px;
                }}
            }}
            .submit-btn {{
                width: 100%;
                padding: 18px;
                font-size: 18px;
                margin-top: 20px;
            }}
            .api-docs {{
                background: #f8f9fa;
                border-left: 4px solid #fc4c02;
                padding: 20px;
                margin: 20px 0;
            }}
            .api-docs code {{
                background: #e9ecef;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
            }}
            .user-welcome {{
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
                padding: 15px 25px;
                border-radius: 50px;
                display: inline-block;
                margin: 10px 0;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚴‍♂️ Strava Activity Agent 🏃‍♀️</h1>
                <div class="joke-title">{daily_joke}</div>
                <p class="description">Create Strava activities with AI-generated descriptions using Writer AI!</p>
            </div>
            
            <div class="status-bar">
                {'✅ Connected to Strava!' if is_authenticated else '⚠️ Authentication Required'}
                {f'<div class="user-welcome">Welcome back, {user_name}! 👋</div>' if is_authenticated else ''}
            </div>
            
            <div class="section {'hidden' if is_authenticated else ''}">
                <h2>🔐 Connect to Strava</h2>
                <p>First, you need to authenticate with Strava to create activities on your account.</p>
                <button onclick="window.location.href='/auth/strava'">Connect with Strava 🚀</button>
            </div>
            
            <div class="section {'' if is_authenticated else 'hidden'}">
                <h2>🎯 Smart Activity Creator</h2>
                <form action="/activity/prompt" method="post">
                    <div class="form-group">
                        <label for="prompt">💬 Tell Me About Your Workout:</label>
                        <textarea 
                            name="prompt" 
                            required 
                            rows="4" 
                            placeholder="e.g., 'Just did a GOATED AF workout at Github hack night. 10 one legged squats on both legs and 10 body weight squats.'"
                            style="resize: vertical; min-height: 100px; font-family: inherit; line-height: 1.4;"
                        ></textarea>
                    </div>
                    <button type="submit" class="submit-btn" style="background: linear-gradient(45deg, #28a745, #20c997);">
                        Create Activity
                    </button>
                </form>
            </div>
            
            <div class="section {'' if is_authenticated else 'hidden'}">
                <h2>🔧 Developer API</h2>
                <div class="api-docs">
                    <p><strong>Interactive API Documentation:</strong> <a href="/docs" target="_blank">View Swagger UI</a></p>
                    <p><strong>Key Endpoints:</strong></p>
                    <ul>
                        <li><code>POST /api/activity/quick</code> - Create activity with minimal input</li>
                        <li><code>POST /api/activity/create</code> - Create activity with full control</li>
                        <li><code>PUT /api/activity/{{id}}</code> - Update existing activity</li>
                        <li><code>GET /api/athlete</code> - Get athlete profile</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <script>
            // Add some interactive flair
            document.addEventListener('DOMContentLoaded', function() {{
                const sections = document.querySelectorAll('.section');
                sections.forEach(section => {{
                    section.addEventListener('mouseenter', function() {{
                        this.style.borderColor = '#fc4c02';
                    }});
                    section.addEventListener('mouseleave', function() {{
                        this.style.borderColor = '#e0e0e0';
                    }});
                }});
                
                // Auto-focus first input if form is visible
                const firstInput = document.querySelector('input[name="duration_minutes"]');
                if (firstInput && !firstInput.closest('.hidden')) {{
                    setTimeout(() => firstInput.focus(), 500);
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/auth/strava")
async def start_strava_auth():
    """Initiate Strava OAuth flow."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    auth_url = agent.get_strava_auth_url()
    return RedirectResponse(url=auth_url)

@app.get("/auth/callback")
async def strava_callback(code: str, scope: str, request: Request):
    """Handle Strava OAuth callback."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        token_data = agent.authenticate_strava(code)
        
        # Store tokens in session (in production, use proper session management)
        session_id = f"user_{token_data['athlete']['id']}"
        user_sessions[session_id] = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_at': token_data['expires_at'],
            'athlete': token_data['athlete']
        }
        
        logger.info(f"Successfully authenticated user {token_data['athlete']['firstname']}")
        
        # Return success page
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Successful</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
                h1 {{ color: #fc4c02; }}
                .success {{ color: #28a745; font-size: 18px; margin: 20px 0; }}
                button {{ background-color: #fc4c02; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 Authentication Successful!</h1>
                <div class="success">
                    Welcome, {token_data['athlete']['firstname']}!<br>
                    You're now connected to Strava and ready to create AI-powered activities.
                </div>
                <button onclick="window.location.href='/'">Create Activities</button>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=400, detail=f"Authentication failed: {e}")

@app.post("/activity/prompt")
async def create_activity_from_prompt(
    prompt: str = Form(..., description="Natural language description of your activity")
):
    """Create an activity from a natural language prompt."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    # Check authentication
    if not user_sessions:
        return HTMLResponse(content="""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 40px; text-align: center;">
            <h2>⚠️ Authentication Required</h2>
            <p>Please authenticate with Strava first.</p>
            <button onclick="window.location.href='/auth/strava'" style="background-color: #fc4c02; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer;">
                Connect with Strava
            </button>
        </body>
        </html>
        """)
    
    # Use the first available session
    session_data = list(user_sessions.values())[0]
    agent.set_strava_tokens(
        session_data['access_token'],
        session_data['refresh_token'],
        session_data['expires_at']
    )
    
    try:
        # Create activity from natural language prompt
        result = await agent.create_activity_from_prompt(prompt)
        
        if result["status"] != "success":
            error_message = result.get("message", "Unknown error occurred")
            return HTMLResponse(content=f"""
            <html>
            <head>
                <title>Parsing Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    h1 {{ color: #fc4c02; text-align: center; }}
                    .error {{ background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .suggestions {{ background-color: #d1ecf1; color: #0c5460; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    button {{ background-color: #fc4c02; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤔 Unable to Parse Activity</h1>
                    <div class="error">
                        <strong>Error:</strong> {error_message}
                    </div>
                    <div class="suggestions">
                        <h3>💡 Try these detailed examples:</h3>
                        <ul style="line-height: 1.6;">
                            <li><strong>Basic:</strong> "I went for a 30 minute run this morning"</li>
                            <li><strong>With location:</strong> "Did a 5k bike ride for 25 minutes around Central Park"</li>
                            <li><strong>With feeling:</strong> "45 minute yoga session at the studio - felt amazing after!"</li>
                            <li><strong>With weather:</strong> "Swam for 40 minutes at the pool, covered 2km despite the cold morning"</li>
                            <li><strong>With achievement:</strong> "First time weight training session for 1 hour at the gym - crushed it!"</li>
                            <li><strong>Rich context:</strong> "Morning trail hike for 90 minutes with my dog, beautiful sunrise and felt super energetic despite the muddy conditions"</li>
                        </ul>
                        <p><strong>💪 Pro tip:</strong> Include activity type, duration, and any details about location, weather, how you felt, who you were with, or special achievements!</p>
                    </div>
                    <div style="text-align: center;">
                        <button onclick="window.location.href='/'">Try Again</button>
                    </div>
                </div>
            </body>
            </html>
            """)
        
        activity = result["activity"]
        parsing_info = result.get("parsing_info", {})
        
        # Return success page with activity details and parsing info
        html_content = f"""
        <html>
        <head>
            <title>Activity Created from Prompt!</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #fc4c02; text-align: center; }}
                .success {{ background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .activity-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .parsing-info {{ background-color: #e7f3ff; color: #004085; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                button {{ background-color: #fc4c02; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px; }}
                .confidence {{ font-weight: bold; color: #28a745; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 Activity Created from Your Prompt!</h1>
                <div class="success">
                    Your natural language description was successfully parsed and turned into a Strava activity!
                </div>
                
                <div class="parsing-info">
                    <h3>🧠 AI Parsing Results:</h3>
                    <p><strong>Original prompt:</strong> "{parsing_info.get('original_prompt', prompt)}"</p>
                    <p><strong>Confidence:</strong> <span class="confidence">{parsing_info.get('confidence', 0)*100:.1f}%</span></p>
                    <p><strong>Understood as:</strong> {parsing_info.get('parsed_data', {}).get('sport_type', 'N/A')} for {parsing_info.get('parsed_data', {}).get('duration_minutes', 'N/A')} minutes</p>
                </div>
                
                <div class="activity-info">
                    <h3>📊 Created Activity:</h3>
                    <p><strong>Name:</strong> {activity.get('name', 'N/A')}</p>
                    <p><strong>Type:</strong> {activity.get('sport_type', 'N/A')}</p>
                    <p><strong>Distance:</strong> {activity.get('distance', 0) / 1000:.2f} km</p>
                    <p><strong>Duration:</strong> {activity.get('elapsed_time', 0) // 60} minutes</p>
                    <p><strong>Description:</strong> {activity.get('description', 'N/A')}</p>
                </div>
                <div style="text-align: center;">
                    <button onclick="window.location.href='/'">Create Another Activity</button>
                    <button onclick="window.open('https://www.strava.com/activities/{activity.get('id')}', '_blank')">
                        View on Strava
                    </button>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to create activity from prompt: {e}")
        return HTMLResponse(content=f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 40px; text-align: center;">
            <h2>❌ Error Creating Activity</h2>
            <p>Failed to create activity from prompt: {str(e)}</p>
            <button onclick="window.location.href='/'" style="background-color: #fc4c02; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer;">
                Go Back
            </button>
        </body>
        </html>
        """)

@app.post("/api/activity/prompt")
async def api_create_activity_from_prompt(request: PromptActivityRequest):
    """Create an activity from a natural language prompt via JSON API."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    # Check for authentication
    if not user_sessions:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Use the first available session
    session_data = list(user_sessions.values())[0]
    agent.set_strava_tokens(
        session_data['access_token'],
        session_data['refresh_token'],
        session_data['expires_at']
    )
    
    try:
        result = await agent.create_activity_from_prompt(request.prompt)
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to parse prompt"))
        
        return {
            "success": True, 
            "activity": result["activity"],
            "parsing_info": result.get("parsing_info", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create activity from prompt: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/activity/{activity_id}")
async def api_update_activity(activity_id: int, request: ActivityUpdateRequest):
    """Update an existing activity."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    # Check for authentication
    if not user_sessions:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Use the first available session
    session_data = list(user_sessions.values())[0]
    agent.set_strava_tokens(
        session_data['access_token'],
        session_data['refresh_token'],
        session_data['expires_at']
    )
    
    try:
        activity = agent.update_activity_with_ai(
            activity_id=activity_id,
            updates=request.updates,
            regenerate_description=request.regenerate_description,
            regenerate_name=request.regenerate_name,
            description_style=request.description_style
        )
        return {"success": True, "activity": activity}
    except Exception as e:
        logger.error(f"Failed to update activity: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/athlete")
async def api_get_athlete():
    """Get the authenticated athlete's profile."""
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    # Check for authentication
    if not user_sessions:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Use the first available session
    session_data = list(user_sessions.values())[0]
    agent.set_strava_tokens(
        session_data['access_token'],
        session_data['refresh_token'],
        session_data['expires_at']
    )
    
    try:
        athlete = agent.get_athlete_profile()
        return {"success": True, "athlete": athlete}
    except Exception as e:
        logger.error(f"Failed to get athlete: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)