import os
import re
import requests
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional
from lyricsgenius import Genius

from app.database import get_db
from app.models import Song, SongAnalysis, Artist
from app.schemas import (
    PaginatedSongsResponse,
    SongListItemResponse,
    SongAnalysisResponse,
    SongAddByUrlRequest,
    SongAddByUrlResponse,
)
from app.services.analyzer import JapaneseSongAnalyzer

router = APIRouter()

VALID_SORT_FIELDS = {
    "unique_kanji_count",
    "total_kanji_count",
    "lexical_density",
    "avg_bunsetsu_length",
    "jlpt_n1_count",
    "total_words",
}


@router.get("", response_model=PaginatedSongsResponse)
def get_songs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("unique_kanji_count"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get paginated list of songs with analysis, sorted by difficulty metric."""

    # Validate sort field
    if sort_by not in VALID_SORT_FIELDS:
        sort_by = "unique_kanji_count"

    # Base query: songs with analysis (inner join excludes songs without analysis)
    query = (
        db.query(Song)
        .join(SongAnalysis)
        .join(Artist)
        .options(joinedload(Song.analysis), joinedload(Song.artist))
    )

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Song.title.ilike(search_term),
                Artist.name.ilike(search_term),
            )
        )

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    sort_column = getattr(SongAnalysis, sort_by)
    if order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    # Apply pagination
    offset = (page - 1) * page_size
    songs = query.offset(offset).limit(page_size).all()

    # Build response
    items = [
        SongListItemResponse(
            id=song.id,
            genius_id=song.genius_id,
            title=song.title,
            artist_name=song.artist.name,
            thumbnail_url=song.thumbnail_url,
            created_at=song.created_at,
            analysis=SongAnalysisResponse.model_validate(song.analysis),
        )
        for song in songs
    ]

    has_more = offset + len(songs) < total

    return PaginatedSongsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more,
    )


# Initialize for add-by-url endpoint
GENIUS_TOKEN = os.getenv("GENIUS_TOKEN")
analyzer = JapaneseSongAnalyzer()


def validate_genius_url(url: str) -> str:
    """Validate and extract song path from Genius URL."""
    url = url.strip()

    # Parse the URL
    parsed = urlparse(url)

    # Check domain
    if parsed.netloc not in ("genius.com", "www.genius.com"):
        raise HTTPException(status_code=400, detail="URL must be from genius.com")

    # Extract and validate path
    path = parsed.path.strip("/")
    if not path:
        raise HTTPException(status_code=400, detail="Invalid Genius URL - no song path found")

    # Check for common invalid paths
    if path in ("", "artists", "albums", "featured"):
        raise HTTPException(status_code=400, detail="Invalid Genius URL - this is not a song page")

    return path


def contains_japanese(text: str) -> bool:
    """Check if text contains Japanese characters (Hiragana, Katakana, or Kanji)."""
    if not text:
        return False
    for char in text:
        if (
            "\u3040" <= char <= "\u309f"  # Hiragana
            or "\u30a0" <= char <= "\u30ff"  # Katakana
            or "\u4e00" <= char <= "\u9fff"  # Kanji
        ):
            return True
    return False


class SongData:
    """Wrapper to hold song data from different sources."""
    def __init__(self, song_dict: dict, lyrics: str):
        self._dict = song_dict
        self.title = song_dict.get("title", "Unknown")
        self.lyrics = lyrics

    def to_dict(self):
        return self._dict


def fetch_song_from_url(genius: Genius, url: str) -> Optional[SongData]:
    """Fetch song data directly from a Genius URL by scraping the page for the song ID."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Extract song ID from the page
        match = re.search(r'"song_id"\s*:\s*(\d+)', response.text)
        if not match:
            match = re.search(r'songs/(\d+)/', response.text)
        if not match:
            return None

        song_id = int(match.group(1))

        # Get song metadata from API
        api_response = genius.song(song_id)
        if not api_response:
            return None

        song_info = api_response.get("song", {})

        # Scrape lyrics directly from the URL (not from search)
        lyrics = genius.lyrics(song_url=url)

        return SongData(song_info, lyrics)
    except Exception:
        return None


@router.post("/add-by-url", response_model=SongAddByUrlResponse)
def add_song_by_url(request: SongAddByUrlRequest, db: Session = Depends(get_db)):
    """Add a song by its Genius URL."""

    # Validate URL
    song_path = validate_genius_url(request.url)

    # Initialize Genius API
    genius = Genius(GENIUS_TOKEN, timeout=30)
    genius.verbose = False
    genius.remove_section_headers = True

    # Try to fetch the exact song from the URL
    song_data = fetch_song_from_url(genius, request.url)

    if not song_data:
        # Fallback: search by slug (less accurate)
        search_query = song_path.replace("-lyrics", "").replace("-", " ")
        search_result = genius.search_song(search_query)
        if search_result:
            song_data = SongData(search_result.to_dict(), search_result.lyrics)

    if not song_data:
        raise HTTPException(status_code=404, detail="Song not found on Genius")

    song_dict = song_data.to_dict()
    song_genius_id = song_dict["id"]

    # Check if song already exists
    existing_song = db.query(Song).filter(Song.genius_id == song_genius_id).first()
    if existing_song:
        return SongAddByUrlResponse(
            id=existing_song.id,
            genius_id=existing_song.genius_id,
            title=existing_song.title,
            artist_name=existing_song.artist.name,
            thumbnail_url=existing_song.thumbnail_url,
            message="Song already exists in database",
        )

    # Check if lyrics contain Japanese
    if not song_data.lyrics:
        raise HTTPException(
            status_code=400,
            detail="No lyrics found for this song on Genius",
        )

    if not contains_japanese(song_data.lyrics):
        raise HTTPException(
            status_code=400,
            detail=f"Song lyrics for '{song_data.title}' do not contain Japanese characters. "
                   "The lyrics on Genius may be romanized. Try finding a version with Japanese text.",
        )

    # Get or create artist
    primary_artist = song_dict.get("primary_artist", {})
    artist_genius_id = primary_artist.get("id")
    artist_name = primary_artist.get("name", "Unknown Artist")
    artist_thumbnail = primary_artist.get("image_url")

    db_artist = db.query(Artist).filter(Artist.genius_id == artist_genius_id).first()
    if not db_artist:
        db_artist = Artist(
            genius_id=artist_genius_id,
            name=artist_name,
            thumbnail_url=artist_thumbnail,
        )
        db.add(db_artist)
        db.flush()

    # Create song
    db_song = Song(
        genius_id=song_genius_id,
        artist_id=db_artist.id,
        title=song_data.title,
        lyrics=song_data.lyrics,
        thumbnail_url=song_dict.get("song_art_image_thumbnail_url"),
    )
    db.add(db_song)
    db.flush()

    # Analyze and create SongAnalysis
    if song_data.lyrics:
        analysis_data = analyzer.analyze(song_data.lyrics)
        db_analysis = SongAnalysis(song_id=db_song.id, **analysis_data)
        db.add(db_analysis)

    db.commit()
    db.refresh(db_song)

    return SongAddByUrlResponse(
        id=db_song.id,
        genius_id=db_song.genius_id,
        title=db_song.title,
        artist_name=db_artist.name,
        thumbnail_url=db_song.thumbnail_url,
        message="Song added and analyzed successfully",
    )
