import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from lyricsgenius import Genius

from app.database import get_db
from app.models import Artist, Song
from app.schemas import ArtistAddRequest, ArtistAddResponse

router = APIRouter()

GENIUS_TOKEN = os.getenv("GENIUS_TOKEN")

MAX_SONGS = 50


@router.post("/add", response_model=ArtistAddResponse)
def add_artist(request: ArtistAddRequest, db: Session = Depends(get_db)):
    genius = Genius(GENIUS_TOKEN)
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
        db_artist = Artist(genius_id=artist_id, name=artist_data.name)
        db.add(db_artist)
        db.commit()
        db.refresh(db_artist)

    # Save songs
    songs_saved = 0
    for song in artist_data.songs:
        song_dict = song.to_dict()
        song_id = song_dict['id']
        existing_song = db.query(Song).filter(Song.genius_id == song_id).first()
        if not existing_song:
            db_song = Song(
                genius_id=song_id,
                artist_id=db_artist.id,
                title=song.title,
                lyrics=song.lyrics
            )
            db.add(db_song)
            songs_saved += 1

    db.commit()

    # Refresh to get songs relationship
    db.refresh(db_artist)
    return ArtistAddResponse(
        songs_saved=songs_saved,
        message=f"Saved {songs_saved} new songs"
    )