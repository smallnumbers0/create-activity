# Strava Activity Creator Agent

An intelligent agent that uses Writer AI to create and update Strava activities with AI-generated descriptions.

## Features

- **Writer AI Integration**: Uses Writer's chat completion API to generate creative activity descriptions
- **Strava API Integration**: Creates and updates activities on your Strava account
- **OAuth Authentication**: Secure authentication flow for Strava access
- **Intelligent Activity Generation**: AI-powered descriptions based on activity data

## Setup

### Prerequisites

- Python 3.8 or higher
- A Strava account
- Writer AI API access

### 1. Clone and Install

```bash
git clone <repository-url>
cd create-activity
pip install -r requirements.txt
```

### 2. Writer AI Setup

The Writer AI API key is already configured for you:
- API Key: `OdZRu6oMEbh7oam2NpLJC9Gijyo1DNyd`
- Model: `palmyra-x5`

### 3. Strava App Setup

1. **Create a Strava Application:**
   - Go to https://www.strava.com/settings/api
   - Click "Create App"
   - Fill in the application details:
     - Application Name: "Activity Agent" (or your preferred name)
     - Category: Choose appropriate category
     - Club: Leave blank (optional)
     - Website: `http://localhost:8080` (for development)
     - Authorization Callback Domain: `localhost`
   - Click "Create"

2. **Get Your Credentials:**
   - Copy your `Client ID` and `Client Secret` from the application page

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your Strava credentials:

```env
# Writer AI Configuration (already set)
WRITER_API_KEY=OdZRu6oMEbh7oam2NpLJC9Gijyo1DNyd
WRITER_MODEL=palmyra-x5

# Strava Configuration (add your values)
STRAVA_CLIENT_ID=your_strava_client_id_here
STRAVA_CLIENT_SECRET=your_strava_client_secret_here
STRAVA_REDIRECT_URI=http://localhost:8080/auth/callback

# Application Configuration
LOG_LEVEL=INFO
PORT=8080
```

### 5. Run the Application

```bash
python main.py
```

The application will start on `http://localhost:8080`

### 6. First Time Setup

1. Open your browser and go to `http://localhost:8080`
2. Click "Connect with Strava"
3. Authorize the application on Strava
4. You'll be redirected back and can start creating activities!

## Usage

### Basic Usage

```python
from strava_activity_agent import StravaActivityAgent

# Initialize the agent
agent = StravaActivityAgent()

# Create a new activity
activity_data = {
    "name": "Morning Run",
    "type": "Run",
    "sport_type": "Run",
    "start_date_local": "2023-09-17T08:00:00Z",
    "elapsed_time": 3600,  # 1 hour in seconds
    "distance": 5000,      # 5km in meters
    "description": "Let AI generate this!"
}

# The agent will use Writer AI to generate a creative description
activity = agent.create_activity(activity_data)
print(f"Created activity: {activity['id']}")
```

### Web Interface

Run the FastAPI server for a web interface:

```bash
python main.py
```

Then visit `http://localhost:8080` to use the web interface.

## API Endpoints

- `GET /`: Web interface for creating activities
- `POST /auth/strava`: Initiate Strava OAuth flow
- `GET /auth/callback`: Handle OAuth callback
- `POST /activity/create`: Create a new activity
- `PUT /activity/{activity_id}`: Update an existing activity

## Configuration

The agent supports various configuration options through environment variables:

- `WRITER_API_KEY`: Your Writer AI API key
- `WRITER_MODEL`: Model to use (default: palmyra-x5)
- `STRAVA_CLIENT_ID`: Your Strava application client ID
- `STRAVA_CLIENT_SECRET`: Your Strava application client secret
- `STRAVA_REDIRECT_URI`: OAuth redirect URI
- `LOG_LEVEL`: Logging level (default: INFO)

## Activity Types Supported

The agent supports all Strava activity types including:
- Running (Run, TrailRun, VirtualRun)
- Cycling (Ride, MountainBikeRide, VirtualRide, EBikeRide)
- Swimming, Hiking, Walking, and many more

## AI-Generated Descriptions

The Writer AI integration creates engaging activity descriptions based on:
- Activity type and duration
- Distance and pace/speed
- Weather conditions (if provided)
- Personal achievements and goals
- Motivational content

## License

MIT License - feel free to use and modify as needed.