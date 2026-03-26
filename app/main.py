from fastapi import FastAPI
from app.database import engine, Base
from app.routes import artists, analysis

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Japanese Song Difficulty API")

# Register routes
app.include_router(artists.router, prefix="/artists", tags=["artists"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])


@app.get("/")
def root():
    return {"message": "Japanese Song Difficulty API"}