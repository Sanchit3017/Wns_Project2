import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import httpx
from shared.config import APIGatewaySettings
from shared.utils.http_client import ServiceClient, propagate_user_context
from shared.security import validate_token_middleware
import uvicorn


settings = APIGatewaySettings()


auth_service = ServiceClient(settings.AUTH_SERVICE_URL)
user_service = ServiceClient(settings.USER_SERVICE_URL)
trip_service = ServiceClient(settings.TRIP_SERVICE_URL)
notification_service = ServiceClient(settings.NOTIFICATION_SERVICE_URL)


app = FastAPI(
    title=settings.APP_NAME,
    description="API Gateway for Travel Management Microservices",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

async def get_user_context(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate token and extract user context"""
    try:
        user_context = validate_token_middleware(credentials.credentials)
        return user_context
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication token")


@app.middleware("http")
async def add_user_context_headers(request: Request, call_next):
    
    if request.url.path in ["/", "/health"] or request.url.path.startswith("/auth"):
        response = await call_next(request)
        return response
    
    
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            user_context = validate_token_middleware(token)
            
            
            request.state.user_id = user_context["user_id"]
            request.state.user_role = user_context["role"]
            request.state.user_email = user_context["email"]
        except Exception as e:
            print(f"Token validation failed: {e}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authentication token"}
            )
    else:
        
        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication required"}
        )
    
    response = await call_next(request)
    return response



@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_auth_service(request: Request, path: str):
    """Proxy requests to auth service"""
    url = f"{settings.AUTH_SERVICE_URL}/auth/{path}"
    
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=await request.body(),
            params=request.query_params
        )
        
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code
        )


@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/drivers/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/employees/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/admin/drivers/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/admin/employees/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_user_service(request: Request, path: str):
    
    if request.url.path.startswith("/drivers"):
        service_path = request.url.path.replace("/drivers", "/users/drivers")
    elif request.url.path.startswith("/employees"):
        service_path = request.url.path.replace("/employees", "/users/employees")
    elif request.url.path.startswith("/admin/drivers"):
        service_path = request.url.path.replace("/admin/drivers", "/users/drivers")
    elif request.url.path.startswith("/admin/employees"):
        service_path = request.url.path.replace("/admin/employees", "/users/employees")
    else:
        service_path = request.url.path.replace("/users", "/users")
    
    url = f"{settings.USER_SERVICE_URL}{service_path}"
    
    
    headers = dict(request.headers)
    if hasattr(request.state, 'user_id'):
        headers.update({
            "X-User-ID": str(request.state.user_id),
            "X-User-Role": request.state.user_role,
            "X-User-Email": request.state.user_email
        })
    
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=await request.body(),
            params=request.query_params
        )
        
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code
        )


@app.api_route("/trips/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_trip_service(request: Request, path: str):
    """Proxy requests to trip service"""
    url = f"{settings.TRIP_SERVICE_URL}/api/trips/{path}"
    
    
    headers = dict(request.headers)
    if hasattr(request.state, 'user_id'):
        headers.update({
            "X-User-ID": str(request.state.user_id),
            "X-User-Role": request.state.user_role,
            "X-User-Email": request.state.user_email
        })
    
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=await request.body(),
            params=request.query_params
        )
        
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code
        )


@app.api_route("/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_notification_service(request: Request, path: str):
    
    url = f"{settings.NOTIFICATION_SERVICE_URL}/api/notifications/{path}"
    
    
    headers = dict(request.headers)
    if hasattr(request.state, 'user_id'):
        headers.update({
            "X-User-ID": str(request.state.user_id),
            "X-User-Role": request.state.user_role,
            "X-User-Email": request.state.user_email
        })
    
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=await request.body(),
            params=request.query_params
        )
        
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code
        )


@app.get("/")
async def root():
    return {
        "service": "API Gateway", 
        "status": "running", 
        "version": "1.0.0",
        "services": {
            "auth": settings.AUTH_SERVICE_URL,
            "user": settings.USER_SERVICE_URL,
            "trip": settings.TRIP_SERVICE_URL,
            "notification": settings.NOTIFICATION_SERVICE_URL
        }
    }


@app.get("/health")
async def health_check():
    
    service_status = {}
    
    services = {
        "auth": settings.AUTH_SERVICE_URL,
        "user": settings.USER_SERVICE_URL,
        "trip": settings.TRIP_SERVICE_URL,
        "notification": settings.NOTIFICATION_SERVICE_URL
    }
    
    for service_name, service_url in services.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}/health")
                service_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": service_url
                }
        except Exception:
            service_status[service_name] = {
                "status": "unreachable",
                "url": service_url
            }
    
    return {
        "status": "healthy",
        "services": service_status
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)