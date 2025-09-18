"""
Strava API Client

This module provides a client for interacting with the Strava API, including
OAuth authentication and activity management.
"""

import requests
import json
import logging
import urllib.parse
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class StravaAPIClient:
    """Client for interacting with the Strava API."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize the Strava API client.
        
        Args:
            client_id: Your Strava application client ID
            client_secret: Your Strava application client secret
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = "https://www.strava.com/api/v3"
        self.oauth_url = "https://www.strava.com/oauth"
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
    
    def get_authorization_url(self, scopes: List[str] = None) -> str:
        """
        Generate the OAuth authorization URL for Strava.
        
        Args:
            scopes: List of required scopes (default: ['activity:write', 'activity:read_all'])
            
        Returns:
            Authorization URL
        """
        if scopes is None:
            scopes = ['activity:write', 'activity:read_all', 'profile:read_all']
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ','.join(scopes),
            'approval_prompt': 'force'
        }
        
        query_string = urllib.parse.urlencode(params)
        auth_url = f"{self.oauth_url}/authorize?{query_string}"
        
        logger.info(f"Generated authorization URL with scopes: {scopes}")
        return auth_url
    
    def exchange_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            authorization_code: The authorization code from the OAuth callback
            
        Returns:
            Token response from Strava
            
        Raises:
            Exception: If token exchange fails
        """
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'grant_type': 'authorization_code'
        }
        
        try:
            logger.info("Exchanging authorization code for access token")
            response = requests.post(
                f"{self.oauth_url}/token",
                data=payload,
                timeout=30
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            # Store tokens
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
            self.token_expires_at = token_data['expires_at']
            
            logger.info("Successfully obtained access token")
            return token_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Token exchange failed: {e}")
            raise Exception(f"Failed to exchange authorization code: {e}")
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh the access token using the refresh token.
        
        Returns:
            New token response from Strava
            
        Raises:
            Exception: If token refresh fails
        """
        if not self.refresh_token:
            raise Exception("No refresh token available")
        
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            logger.info("Refreshing access token")
            response = requests.post(
                f"{self.oauth_url}/token",
                data=payload,
                timeout=30
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            # Update tokens
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
            self.token_expires_at = token_data['expires_at']
            
            logger.info("Successfully refreshed access token")
            return token_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Token refresh failed: {e}")
            raise Exception(f"Failed to refresh access token: {e}")
    
    def _ensure_valid_token(self):
        """Ensure we have a valid access token, refresh if necessary."""
        if not self.access_token:
            raise Exception("No access token available. Please authenticate first.")
        
        # Check if token is expired (with 5 minute buffer)
        current_time = datetime.now().timestamp()
        if self.token_expires_at and (current_time + 300) >= self.token_expires_at:
            logger.info("Access token is expired, refreshing...")
            self.refresh_access_token()
    
    def _make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the Strava API.
        
        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            API response
            
        Raises:
            Exception: If the request fails
        """
        self._ensure_valid_token()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Strava API request failed: {method} {url} - {e}")
            raise Exception(f"Strava API request failed: {e}")
    
    def get_athlete(self) -> Dict[str, Any]:
        """
        Get the authenticated athlete's profile.
        
        Returns:
            Athlete profile data
        """
        logger.info("Fetching authenticated athlete profile")
        return self._make_authenticated_request('GET', '/athlete')
    
    def create_activity(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new activity on Strava.
        
        Args:
            activity_data: Activity data including name, type, sport_type, etc.
            
        Returns:
            Created activity data
            
        Raises:
            Exception: If activity creation fails
        """
        required_fields = ['name', 'sport_type', 'start_date_local', 'elapsed_time']
        
        # Validate required fields
        for field in required_fields:
            if field not in activity_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Prepare activity payload
        payload = {
            'name': activity_data['name'],
            'sport_type': activity_data['sport_type'],
            'start_date_local': activity_data['start_date_local'],
            'elapsed_time': activity_data['elapsed_time']
        }
        
        # Add optional fields
        optional_fields = [
            'type', 'description', 'distance', 'trainer', 'commute'
        ]
        
        for field in optional_fields:
            if field in activity_data:
                payload[field] = activity_data[field]
        
        logger.info(f"Creating activity: {payload['name']} ({payload['sport_type']})")
        
        try:
            result = self._make_authenticated_request('POST', '/activities', data=payload)
            logger.info(f"Successfully created activity with ID: {result.get('id')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create activity: {e}")
            raise
    
    def update_activity(self, activity_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing activity on Strava.
        
        Args:
            activity_id: The ID of the activity to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated activity data
        """
        # Allowed fields for updating
        allowed_fields = [
            'name', 'type', 'sport_type', 'description', 'trainer', 
            'commute', 'hide_from_home', 'gear_id'
        ]
        
        # Filter to only allowed fields
        payload = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if not payload:
            raise ValueError("No valid fields provided for update")
        
        logger.info(f"Updating activity {activity_id} with fields: {list(payload.keys())}")
        
        try:
            result = self._make_authenticated_request(
                'PUT', 
                f'/activities/{activity_id}', 
                data=payload
            )
            logger.info(f"Successfully updated activity {activity_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update activity {activity_id}: {e}")
            raise
    
    def get_activity(self, activity_id: int) -> Dict[str, Any]:
        """
        Get details of a specific activity.
        
        Args:
            activity_id: The ID of the activity
            
        Returns:
            Activity data
        """
        logger.info(f"Fetching activity {activity_id}")
        return self._make_authenticated_request('GET', f'/activities/{activity_id}')
    
    def get_activities(
        self, 
        before: Optional[int] = None,
        after: Optional[int] = None,
        page: int = 1,
        per_page: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get a list of the authenticated athlete's activities.
        
        Args:
            before: Epoch timestamp to filter activities before this time
            after: Epoch timestamp to filter activities after this time
            page: Page number
            per_page: Number of activities per page
            
        Returns:
            List of activity data
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if before:
            params['before'] = before
        if after:
            params['after'] = after
        
        logger.info(f"Fetching activities (page {page}, {per_page} per page)")
        return self._make_authenticated_request('GET', '/athlete/activities', params=params)
    
    def set_tokens(self, access_token: str, refresh_token: str, expires_at: int):
        """
        Set tokens manually (e.g., from stored credentials).
        
        Args:
            access_token: The access token
            refresh_token: The refresh token
            expires_at: Token expiration timestamp
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = expires_at
        logger.info("Tokens set manually")