from fastapi import FastAPI
from app.database import engine, Base
from app.routes import artists, analysis, songs
from fastapi.middleware.cors import CORSMiddleware

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Japanese Song Difficulty API")

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(artists.router, prefix="/artists", tags=["artists"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
app.include_router(songs.router, prefix="/songs", tags=["songs"])


@app.get("/")
def root():
    return {"message": "Japanese Song Difficulty API"}