from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List

from app.database import get_db
from app.models import Song, SongAnalysis
from app.schemas import SongAnalysisResponse, SongWithAnalysisResponse
from app.services.analyzer import JapaneseSongAnalyzer

router = APIRouter()

# Initialize analyzer
analyzer = JapaneseSongAnalyzer()


@router.get("/song/{song_id}", response_model=SongAnalysisResponse)
def get_song_analysis(song_id: int, db: Session = Depends(get_db)):
    """Get analysis for a specific song. If analysis doesn't exist, create it."""
    analysis = db.query(SongAnalysis).filter(SongAnalysis.song_id == song_id).first()
    if analysis:
        return analysis

    # Analysis doesn't exist, check if song exists and analyze it
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    if not song.lyrics:
        raise HTTPException(status_code=400, detail="Song has no lyrics to analyze")

    analysis_data = analyzer.analyze(song.lyrics)
    new_analysis = SongAnalysis(song_id=song_id, **analysis_data)
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)
    return new_analysis


@router.get("/artist/{artist_id}", response_model=List[SongWithAnalysisResponse])
def get_artist_analyses(artist_id: int, db: Session = Depends(get_db)):
    """Get all song analyses for an artist."""
    songs = db.query(Song).filter(Song.artist_id == artist_id).all()
    if not songs:
        raise HTTPException(status_code=404, detail="No songs found for this artist")
    return songs


@router.post("/reanalyze/{song_id}", response_model=SongAnalysisResponse)
def reanalyze_song(song_id: int, db: Session = Depends(get_db)):
    """Re-run analysis for a specific song."""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    if not song.lyrics:
        raise HTTPException(status_code=400, detail="Song has no lyrics to analyze")

    analysis_data = analyzer.analyze(song.lyrics)

    # Update or create analysis
    existing = db.query(SongAnalysis).filter(SongAnalysis.song_id == song_id).first()
    if existing:
        for key, value in analysis_data.items():
            setattr(existing, key, value)
        existing.analyzed_at = func.now()
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_analysis = SongAnalysis(song_id=song_id, **analysis_data)
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)
        return new_analysis
