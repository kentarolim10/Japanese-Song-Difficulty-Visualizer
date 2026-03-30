from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional, List


# Request
class ArtistAddRequest(BaseModel):
    artist_name: str


# Response
class ArtistAddResponse(BaseModel):
    songs_saved: int
    message: str


class SongAnalysisResponse(BaseModel):
    id: int
    song_id: int

    # JLPT Vocabulary
    jlpt_n5_count: int
    jlpt_n4_count: int
    jlpt_n3_count: int
    jlpt_n2_count: int
    jlpt_n1_count: int
    jlpt_unknown_count: int

    # Kanji
    total_kanji_count: int
    unique_kanji_count: int
    kanji_grade_1_count: int
    kanji_grade_2_count: int
    kanji_grade_3_count: int
    kanji_grade_4_count: int
    kanji_grade_5_count: int
    kanji_grade_6_count: int
    kanji_secondary_count: int
    kanji_uncommon_count: int

    # Bunsetsu
    total_bunsetsu_count: int
    max_bunsetsu_length: int
    min_bunsetsu_length: int

    # Lexical
    total_words: int
    unique_words: int
    lexical_density: float

    # Word frequencies
    word_frequencies: Optional[Dict[str, int]]

    # Special word categories
    onomatopoeia: Optional[List[str]] = None
    proper_nouns: Optional[List[str]] = None
    archaic_words: Optional[List[str]] = None

    analyzed_at: datetime

    class Config:
        from_attributes = True


class SongResponse(BaseModel):
    id: int
    genius_id: int
    title: str
    thumbnail_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SongWithAnalysisResponse(SongResponse):
    analysis: Optional[SongAnalysisResponse] = None


class SongListItemResponse(BaseModel):
    id: int
    genius_id: int
    title: str
    artist_id: int
    artist_name: str
    thumbnail_url: Optional[str] = None
    created_at: datetime
    analysis: SongAnalysisResponse  # Required - songs without analysis excluded

    class Config:
        from_attributes = True


class PaginatedSongsResponse(BaseModel):
    items: List[SongListItemResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# Add song by URL
class SongAddByUrlRequest(BaseModel):
    url: str


class SongAddByUrlResponse(BaseModel):
    id: int
    genius_id: int
    title: str
    artist_name: str
    thumbnail_url: Optional[str] = None
    message: str


# Stats
class SongAveragesResponse(BaseModel):
    unique_kanji_count: float
    total_kanji_count: float
    lexical_density: float
    total_words: float


class ArtistAveragesResponse(BaseModel):
    artist_id: int
    artist_name: str
    song_count: int
    unique_kanji_count: Optional[float] = None
    total_kanji_count: Optional[float] = None
    lexical_density: Optional[float] = None
    total_words: Optional[float] = None