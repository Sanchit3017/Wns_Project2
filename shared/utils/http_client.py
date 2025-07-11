import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class ServiceClient:
    """HTTP client for inter-service communication"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
    async def _make_request(self, method: str, endpoint: str, 
                           headers: Optional[Dict] = None, 
                           json_data: Optional[Dict] = None,
                           params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request with error handling and retries"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    params=params
                )
                
                if response.status_code >= 400:
                    logger.error(f"Service request failed: {method} {url} - {response.status_code}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Service request failed: {response.text}"
                    )
                
                return response.json() if response.content else {}
                
            except httpx.TimeoutException:
                logger.error(f"Service request timeout: {method} {url}")
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable"
                )
            except httpx.ConnectError:
                logger.error(f"Service connection error: {method} {url}")
                raise HTTPException(
                    status_code=503,
                    detail="Service unavailable"
                )
    
    async def get(self, endpoint: str, headers: Optional[Dict] = None, 
                  params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        return await self._make_request("GET", endpoint, headers=headers, params=params)
    
    async def post(self, endpoint: str, json_data: Optional[Dict] = None, 
                   headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request"""
        return await self._make_request("POST", endpoint, headers=headers, json_data=json_data)
    
    async def put(self, endpoint: str, json_data: Optional[Dict] = None, 
                  headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request"""
        return await self._make_request("PUT", endpoint, headers=headers, json_data=json_data)
    
    async def delete(self, endpoint: str, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make DELETE request"""
        return await self._make_request("DELETE", endpoint, headers=headers)


def propagate_auth_header(token: str) -> Dict[str, str]:
    """Create authorization header for service-to-service communication"""
    return {"Authorization": f"Bearer {token}"}


def propagate_user_context(user_id: int, role: str) -> Dict[str, str]:
    """Create headers with user context for service communication"""
    return {
        "X-User-ID": str(user_id),
        "X-User-Role": role
    }