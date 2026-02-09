from fastapi import FastAPI
from backend.ai_routes import router as ai_router

app = FastAPI()   # 👈 MUST come first

app.include_router(ai_router, prefix="/ai", tags=["AI"])
