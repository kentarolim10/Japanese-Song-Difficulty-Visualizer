import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from lyricsgenius import Genius

from app.database import get_db
from app.utils import contains_japanese
from app.models import Artist, Song, SongAnalysis
from app.schemas import ArtistAddRequest, ArtistAddResponse
from app.services.analyzer import JapaneseSongAnalyzer

# Initialize analyzer (singleton pattern for data loading)
analyzer = JapaneseSongAnalyzer()

router = APIRouter()

GENIUS_TOKEN = os.getenv("GENIUS_TOKEN")

MAX_SONGS = 50


    )