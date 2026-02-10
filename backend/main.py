from fastapi import FastAPI
from backend.database import engine
from backend import models
# from backend.ai_routes import router as ai_router
from backend.analytics_routes import router as analytics_router
from backend.posts_routes import router as posts_router

app = FastAPI()

# create tables once
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "GeoDrive Insight backend running"}

# app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(posts_router, prefix="/posts", tags=["Posts"])
