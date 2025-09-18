# Strava Activity Agent with Exercise Knowledge 🏃‍♂️🧠

An intelligent Strava activity creation tool powered by Writer AI and enhanced with Weaviate-based exercise knowledge for semantic understanding of fitness activities.

## Features ✨

### Core Functionality
- **AI-Powered Activity Creation**: Uses Writer AI (palmyra-x5) to generate hilarious, contextual activity titles and descriptions
- **Natural Language Parsing**: Converts plain English descriptions into structured Strava activities
- **Complete Strava Integration**: Full OAuth 2.0 authentication and activity management
- **Robust Error Handling**: Multiple fallback parsing mechanisms for reliable operation

### New: Exercise Knowledge Base 🧠
- **Semantic Exercise Search**: Weaviate-powered vector search for exercise terms and concepts
- **Smart Sport Type Detection**: Enhanced recognition of activities from natural language
- **Contextual Enhancement**: Automatically enriches activity data with exercise-specific knowledge
- **Rich Exercise Database**: Pre-populated with comprehensive fitness terminology and relationships

## Quick Start 🚀

### Prerequisites
- Python 3.8+
- Writer AI API key
- Strava API credentials
- (Optional) Weaviate instance for exercise knowledge features

### Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd create-activity
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment configuration**:
Create a `.env` file:
```bash
# Required: Writer AI
WRITER_API_KEY=your_writer_api_key_here

# Required: Strava API
STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
STRAVA_REDIRECT_URI=http://localhost:8080/auth/strava/callback

# Optional: Weaviate (for exercise knowledge features)
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your_weaviate_api_key  # Only for cloud instances
```

3. **Optional: Setup Weaviate locally**:
```bash
# Run Weaviate with Docker (for exercise knowledge features)
# Note: If port 8080 is in use, try 8081:
docker run -p 8081:8080 -p 50051:50051 \
  cr.weaviate.io/semitechnologies/weaviate:1.26.1

# Then update your environment:
WEAVIATE_URL=http://localhost:8081
```

4. **Run the application**:
```bash
python main.py
```

Visit `http://localhost:8080` and start creating activities!

## Exercise Knowledge Demo 🎯

Test the exercise knowledge features:
```bash
python demo_exercise_knowledge.py
```

This will demonstrate:
- Semantic search for exercise terms
- Sport type suggestions
- Context enhancement
- Exercise knowledge integration

## API Endpoints 🛠️

### Core Activity Management
- `GET /` - Web interface
- `GET /auth/strava` - Start Strava authentication
- `POST /activities/quick` - Create activity with structured data
- `POST /activities/prompt` - Create activity from natural language
- `GET /activities` - List recent activities

### New: Exercise Knowledge
- `GET /exercises/search?q={query}` - Search exercise terms semantically
- `GET /exercises/suggestions/{sport_type}` - Get exercise suggestions for sport type

## Usage Examples 💡

### Natural Language Activity Creation
The system now understands complex exercise descriptions:

```python
# These all work with enhanced exercise knowledge:
"I did a 45 minute crossfit session at the gym"
"Went for an hour bike ride through the mountains" 
"30 minute yoga flow in the studio this morning"
"Hit the weights for a solid strength training session"
"Morning trail run for 5k, felt amazing!"
```

### Exercise Knowledge Search
```python
# Search for exercise concepts
agent.search_exercise_terms("high intensity interval training")
# Returns: HIIT workouts, CrossFit, circuit training...

agent.search_exercise_terms("peaceful mindful movement")  
# Returns: Yoga, tai chi, stretching...
```

## How It Works 🔍

### Enhanced Parsing Pipeline
1. **Exercise Knowledge Lookup**: Input text is semantically searched against exercise database
2. **AI Parsing with Context**: Writer AI receives enhanced prompts with exercise knowledge
3. **Smart Fallback**: If AI fails, exercise knowledge provides intelligent sport type detection
4. **Context Enhancement**: Additional exercise-specific metadata enriches the final activity

### Exercise Knowledge Schema
The Weaviate database contains:
- Exercise names and synonyms
- Strava sport type mappings
- Equipment and location associations
- Muscle groups and intensity levels
- Related keywords and terminology

## Configuration Options ⚙️

### Weaviate Setup Options

**Local Development** (Recommended):
```bash
# Simple local setup
docker run -p 8080:8080 -p 50051:50051 cr.weaviate.io/semitechnologies/weaviate:1.26.1
```

**Weaviate Cloud**:
```bash
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=your_api_key
```

**Without Weaviate** (Fallback mode):
- Exercise knowledge features will be disabled
- System falls back to keyword-based sport type detection
- All other features work normally

### Writer AI Configuration
```bash
WRITER_API_KEY=your_api_key
WRITER_MODEL=palmyra-x5  # Optional, defaults to palmyra-x5
```

## Development 🛠️

### Project Structure
```
create-activity/
├── src/
│   ├── strava_activity_agent.py    # Enhanced main agent
│   ├── exercise_knowledge.py       # NEW: Weaviate integration
│   ├── writer_client.py           # Writer AI client
│   └── strava_client.py           # Strava API client
├── main.py                        # FastAPI web application
├── demo_exercise_knowledge.py     # NEW: Demo script
└── requirements.txt               # Updated with Weaviate
```

### Adding New Exercises
Exercises are automatically populated on first run. To add custom exercises:

```python
from src.exercise_knowledge import ExerciseKnowledgeBase

kb = ExerciseKnowledgeBase()
# Add custom exercise data to the knowledge base
```

### Testing Exercise Knowledge
```bash
# Run the demo to see exercise knowledge in action
python demo_exercise_knowledge.py

# Test specific queries programmatically
python -c "
from src.exercise_knowledge import ExerciseKnowledgeBase
kb = ExerciseKnowledgeBase()
print(kb.search_exercises('strength training'))
"
```

## Troubleshooting 🔧

### Weaviate Connection Issues
```bash
# Check if Weaviate is running
curl http://localhost:8080/v1/.well-known/ready

# View logs
docker logs <weaviate_container_id>
```

### Exercise Knowledge Not Working
- Exercise knowledge features are optional and gracefully disabled if Weaviate isn't available
- Check WEAVIATE_URL environment variable
- Verify Weaviate is accessible
- For cloud instances, ensure WEAVIATE_API_KEY is set

### Writer AI Issues
- Verify WRITER_API_KEY is correct
- Check API quota and usage
- Review logs for specific error messages

## Advanced Features 🚀

### Custom Exercise Knowledge
You can extend the exercise database with domain-specific knowledge:
- Add new exercise types
- Define custom synonyms and keywords
- Create specialized sport categories
- Implement custom context enhancement rules

### Integration Examples
```python
# Search for exercises matching user input
results = agent.search_exercise_terms("cardio workout")

# Get suggestions for a specific sport
suggestions = agent.get_exercise_suggestions_for_sport("Run")

# Create activity with enhanced knowledge
activity = await agent.create_activity_from_prompt(
    "Did some HIIT training for 30 minutes"
)
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Add tests for new exercise knowledge features
4. Submit a pull request

## License 📄

MIT License - feel free to use and modify as needed.

---

**Powered by Writer AI 🤖 + Enhanced with Weaviate Exercise Knowledge 🧠**