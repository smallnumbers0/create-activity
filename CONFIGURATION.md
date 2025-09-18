# Strava Activity Agent - Configuration Guide

## Quick Start Checklist

- [ ] Copy `.env.example` to `.env`
- [ ] Create Strava application at https://www.strava.com/settings/api
- [ ] Add your Strava Client ID and Secret to `.env`
- [ ] Run `python main.py`
- [ ] Visit http://localhost:8080
- [ ] Connect with Strava
- [ ] Create your first AI-powered activity!

## Detailed Configuration

### Writer AI Configuration

The Writer AI integration is pre-configured for you:

```env
WRITER_API_KEY=OdZRu6oMEbh7oam2NpLJC9Gijyo1DNyd
WRITER_MODEL=palmyra-x5
```

**Available Models:**
- `palmyra-x5` (recommended) - Most capable model
- `palmyra-x4` - Good balance of speed and quality
- `palmyra-creative` - More creative responses
- `palmyra-fin` - Financial domain optimized
- `palmyra-med` - Medical domain optimized

### Strava Configuration

You need to create your own Strava application:

1. **Go to Strava API Settings:**
   Visit: https://www.strava.com/settings/api

2. **Create New Application:**
   - Application Name: Choose any name (e.g., "My Activity Agent")
   - Category: Select appropriate category
   - Club: Leave blank (optional)
   - Website: `http://localhost:8080`
   - Authorization Callback Domain: `localhost`

3. **Configure Environment:**
   ```env
   STRAVA_CLIENT_ID=your_client_id_from_strava
   STRAVA_CLIENT_SECRET=your_client_secret_from_strava
   STRAVA_REDIRECT_URI=http://localhost:8080/auth/callback
   ```

### OAuth Scopes

The application requests these Strava permissions:
- `activity:write` - Create and update activities
- `activity:read_all` - Read all activities (including private)
- `profile:read_all` - Read athlete profile information

### Application Settings

```env
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
PORT=8080              # Port for web server
```

## Production Deployment

For production deployment, update these settings:

1. **Update Strava App Settings:**
   - Website: Your production domain
   - Authorization Callback Domain: Your production domain (without http://)

2. **Update Environment:**
   ```env
   STRAVA_REDIRECT_URI=https://yourdomain.com/auth/callback
   PORT=80  # or 443 for HTTPS
   ```

3. **Security Considerations:**
   - Use HTTPS in production
   - Implement proper session management
   - Store tokens securely (database, not memory)
   - Add rate limiting
   - Validate all inputs

## Troubleshooting

### Common Issues

1. **"Agent not initialized" error:**
   - Check that all environment variables are set
   - Verify Writer API key is correct
   - Ensure Strava credentials are valid

2. **OAuth redirect errors:**
   - Verify callback domain in Strava app settings
   - Check that redirect URI in .env matches Strava settings
   - Ensure you're using the correct protocol (http/https)

3. **Activity creation fails:**
   - Confirm you've authenticated with Strava
   - Check that required scopes are granted
   - Verify activity data is complete

### Testing Your Configuration

1. **Test Writer AI:**
   ```python
   from src.writer_client import WriterAPIClient
   client = WriterAPIClient("your_api_key")
   # Should work without errors
   ```

2. **Test Strava OAuth:**
   - Start the application
   - Click "Connect with Strava"
   - Should redirect to Strava login

3. **Test Activity Creation:**
   - Complete OAuth flow
   - Try creating a quick activity
   - Check your Strava account for the new activity

## API Rate Limits

### Writer AI
- No specific limits mentioned in documentation
- Implement reasonable delays between requests

### Strava API
- 200 requests per 15 minutes
- 2,000 requests per day
- The application handles token refresh automatically

## Support

If you encounter issues:

1. Check the logs for error messages
2. Verify your configuration against this guide
3. Test each component separately
4. Review the Strava API documentation: https://developers.strava.com/docs/
5. Check Writer AI documentation: https://dev.writer.com/