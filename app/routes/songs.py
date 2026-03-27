from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional

from app.database import get_db
from app.models import Song, SongAnalysis, Artist
from app.schemas import PaginatedSongsResponse, SongListItemResponse, SongAnalysisResponse

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
