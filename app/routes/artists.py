import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from lyricsgenius import Genius

from app.database import get_db
from app.models import Artist, Song, SongAnalysis
from app.schemas import ArtistAddRequest, ArtistAddResponse
from app.services.analyzer import JapaneseSongAnalyzer

# Initialize analyzer (singleton pattern for data loading)
analyzer = JapaneseSongAnalyzer()

router = APIRouter()

GENIUS_TOKEN = os.getenv("GENIUS_TOKEN")

MAX_SONGS = 50


def contains_japanese(text: str) -> bool:
    """Check if text contains Japanese characters (Hiragana, Katakana, or Kanji)."""
    if not text:
        return False
    for char in text:
        if ('\u3040' <= char <= '\u309f' or  # Hiragana
            '\u30a0' <= char <= '\u30ff' or  # Katakana
            '\u4e00' <= char <= '\u9fff'):   # Kanji
            return True
    return False


@router.post("/add", response_model=ArtistAddResponse)
def add_artist(request: ArtistAddRequest, db: Session = Depends(get_db)):
    genius = Genius(GENIUS_TOKEN, timeout=30)
    genius.verbose = False

    # Search for artist on Genius
    artist_data = genius.search_artist(request.artist_name, max_songs=MAX_SONGS, sort="popularity")

    if not artist_data:
        raise HTTPException(status_code=404, detail="Artist not found")

    # Get artist info as dict
    artist_dict = artist_data.to_dict()
    artist_id = artist_dict['id']

    # Check if artist already exists
    db_artist = db.query(Artist).filter(Artist.genius_id == artist_id).first()

    if not db_artist:
        db_artist = Artist(
            genius_id=artist_id,
            name=artist_data.name,
            thumbnail_url=artist_dict.get('image_url')
        )
        db.add(db_artist)
        db.commit()
        db.refresh(db_artist)

    # Save songs
    songs_saved = 0
    for song in artist_data.songs:
        # Skip if lyrics are not Japanese
        if not contains_japanese(song.lyrics):
            continue

        song_dict = song.to_dict()
        song_id = song_dict['id']
        existing_song = db.query(Song).filter(Song.genius_id == song_id).first()
        if not existing_song:
            db_song = Song(
                genius_id=song_id,
                artist_id=db_artist.id,
                title=song.title,
                lyrics=song.lyrics,
                thumbnail_url=song_dict.get('song_art_image_thumbnail_url')
            )
            db.add(db_song)
            db.flush()  # Get the song ID before creating analysis

            # Analyze the song and create SongAnalysis
            if song.lyrics:
                analysis_data = analyzer.analyze(song.lyrics)
                db_analysis = SongAnalysis(song_id=db_song.id, **analysis_data)
                db.add(db_analysis)

            songs_saved += 1

    db.commit()

    # Refresh to get songs relationship
    db.refresh(db_artist)
    return ArtistAddResponse(
        songs_saved=songs_saved,
        message=f"Saved {songs_saved} new songs"
    )