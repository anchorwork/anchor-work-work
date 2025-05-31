import os
import sys
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from fastapi import status

from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
load_dotenv()

from routes.researcher_api       import router as researcher_router
from routes.codex_api            import router as codex_router
from routes.semantic_search_api  import router as semantic_router
from routes.web_search_api       import router as web_router
from routes.save_log_api         import router as save_log_router
from routes.status_api           import router as status_router
from routes.followup_api         import router as followup_router
from routes.briefing_api         import router as briefing_router
from routes.crew_api             import router as crew_router
from agents.coder.coder import router as coder_router

from utils.tools  import load_agent_profile
from routes.memory_api import router as memory_router

# New imports for logging and memory maintenance worker
from utils.logging_config import setup_logging
from utils.memory_maintenance_worker import register_memory_maintenance_worker

# Sentry SDK import
import sentry_sdk

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),  # Set this in your .env and Render dashboard
    traces_sample_rate=1.0,        # Adjust for performance monitoring (1.0 = 100% of requests)
    environment=os.getenv("SENTRY_ENV", "production")
)

app = FastAPI(title="Anchorwork API", version="0.2.0")

# Setup logging early
setup_logging()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3001")],  # Use env var, default to localhost for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# OAuth2 scheme for bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # TODO: Replace with real JWT decode/verify logic
    if not token or token != os.getenv("ANCHORWORK_API_TOKEN"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": "admin"}  # Placeholder user

@app.get("/")
async def root(current_user: dict = Depends(get_current_user)):
    return {"Anchorwork API": "alive"}

@app.get("/ping")
async def ping(current_user: dict = Depends(get_current_user)):
    """
    Lightweight health probe for load‑balancers and front‑end UI.
    Returns 200 OK with {"ok": true}.
    """
    return {"ok": True}

# Include your existing routers
app.include_router(researcher_router)
app.include_router(codex_router)
app.include_router(semantic_router)
app.include_router(web_router)
app.include_router(save_log_router)
app.include_router(status_router)
app.include_router(followup_router)
app.include_router(briefing_router)
app.include_router(coder_router, prefix="/coder")
app.include_router(crew_router)
app.include_router(memory_router)

# Register memory maintenance worker with example agent/session IDs
agent_ids = ["agent1", "agent2"]  # Replace with your actual agent IDs or dynamic source
session_ids = [None]  # Or list of active session IDs

register_memory_maintenance_worker(app, agent_ids, session_ids, interval_seconds=300)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)