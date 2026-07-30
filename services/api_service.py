"""Optional API service with auto-disable functionality."""

from __future__ import annotations

from typing import Optional, Dict, Any
import aiohttp
from datetime import datetime

from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class APIService:
    """Service for external API integration with auto-disable capability."""
    
    def __init__(self) -> None:
        """Initialize API service."""
        self.enabled = config.api_enabled
        self.base_url = config.api_base_url
        self.api_key = config.api_key
        self.timeout = config.api_timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self) -> APIService:
        """Async context manager entry."""
        if self.enabled:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._session:
            await self._session.close()
    
    async def get_session(self) -> Optional[aiohttp.ClientSession]:
        """Get or create HTTP session."""
        if not self.enabled:
            return None
        
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        
        return self._session
    
    def is_available(self) -> bool:
        """Check if API service is available."""
        return self.enabled
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make GET request to API."""
        if not self.enabled:
            logger.debug("API service disabled, skipping GET request")
            return None
        
        try:
            session = await self.get_session()
            if not session:
                return None
            
            url = f"{self.base_url}{endpoint}"
            request_headers = {"Authorization": f"Bearer {self.api_key}"}
            if headers:
                request_headers.update(headers)
            
            async with session.get(url, params=params, headers=request_headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"API GET request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error in API GET request: {e}")
            return None
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make POST request to API."""
        if not self.enabled:
            logger.debug("API service disabled, skipping POST request")
            return None
        
        try:
            session = await self.get_session()
            if not session:
                return None
            
            url = f"{self.base_url}{endpoint}"
            request_headers = {"Authorization": f"Bearer {self.api_key}"}
            if headers:
                request_headers.update(headers)
            
            async with session.post(url, data=data, json=json, headers=request_headers) as response:
                if response.status in (200, 201):
                    return await response.json()
                else:
                    logger.warning(f"API POST request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error in API POST request: {e}")
            return None
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make PUT request to API."""
        if not self.enabled:
            logger.debug("API service disabled, skipping PUT request")
            return None
        
        try:
            session = await self.get_session()
            if not session:
                return None
            
            url = f"{self.base_url}{endpoint}"
            request_headers = {"Authorization": f"Bearer {self.api_key}"}
            if headers:
                request_headers.update(headers)
            
            async with session.put(url, data=data, json=json, headers=request_headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"API PUT request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error in API PUT request: {e}")
            return None
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """Make DELETE request to API."""
        if not self.enabled:
            logger.debug("API service disabled, skipping DELETE request")
            return False
        
        try:
            session = await self.get_session()
            if not session:
                return False
            
            url = f"{self.base_url}{endpoint}"
            request_headers = {"Authorization": f"Bearer {self.api_key}"}
            if headers:
                request_headers.update(headers)
            
            async with session.delete(url, params=params, headers=request_headers) as response:
                return response.status in (200, 204)
        except Exception as e:
            logger.error(f"Error in API DELETE request: {e}")
            return False
    
    # Placeholder methods for future API features
    # These can be implemented without changing command code
    
    async def sync_session(self, session_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sync session data to external API (placeholder)."""
        if not self.enabled:
            return None
        
        logger.debug(f"Session sync placeholder: {session_data.get('id')}")
        # Future implementation: await self.post("/sessions", json=session_data)
        return None
    
    async def sync_stats(self, stats_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sync statistics to external API (placeholder)."""
        if not self.enabled:
            return None
        
        logger.debug(f"Stats sync placeholder: {stats_data.get('user_id')}")
        # Future implementation: await self.post("/stats", json=stats_data)
        return None
    
    async def sync_vote(self, vote_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sync vote to external API (placeholder)."""
        if not self.enabled:
            return None
        
        logger.debug(f"Vote sync placeholder: {vote_data.get('target_id')}")
        # Future implementation: await self.post("/votes", json=vote_data)
        return None
    
    async def sync_boost(self, boost_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sync boost to external API (placeholder)."""
        if not self.enabled:
            return None
        
        logger.debug(f"Boost sync placeholder: {boost_data.get('user_id')}")
        # Future implementation: await self.post("/boosts", json=boost_data)
        return None
    
    async def get_external_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get external statistics for user (placeholder)."""
        if not self.enabled:
            return None
        
        logger.debug(f"External stats placeholder: {user_id}")
        # Future implementation: await self.get(f"/users/{user_id}/stats")
        return None
    
    async def health_check(self) -> bool:
        """Check if API is healthy (placeholder)."""
        if not self.enabled:
            return False
        
        logger.debug("API health check placeholder")
        # Future implementation: return await self.get("/health") is not None
        return True


# Global API service instance
api_service = APIService()
