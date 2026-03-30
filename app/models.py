from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base                               
                                                              
                                                              
class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    genius_id = Column(Integer, unique=True, index=True)
    name = Column(String(255), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    songs = relationship("Song", back_populates="artist")   
                                                            
                                                            
class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    genius_id = Column(Integer, unique=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    title = Column(String(255), nullable=False)
    lyrics = Column(Text)
    thumbnail_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    artist = relationship("Artist", back_populates="songs")
    analysis = relationship("SongAnalysis", back_populates="song", uselist=False)


class SongAnalysis(Base):
    __tablename__ = "song_analyses"

    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), unique=True, nullable=False)

    # JLPT Vocabulary Counts
    jlpt_n5_count = Column(Integer, default=0)
    jlpt_n4_count = Column(Integer, default=0)
    jlpt_n3_count = Column(Integer, default=0)
    jlpt_n2_count = Column(Integer, default=0)
    jlpt_n1_count = Column(Integer, default=0)
    jlpt_unknown_count = Column(Integer, default=0)

    # Kanji Complexity
    total_kanji_count = Column(Integer, default=0)
    unique_kanji_count = Column(Integer, default=0)
    kanji_grade_1_count = Column(Integer, default=0)
    kanji_grade_2_count = Column(Integer, default=0)
    kanji_grade_3_count = Column(Integer, default=0)
    kanji_grade_4_count = Column(Integer, default=0)
    kanji_grade_5_count = Column(Integer, default=0)
    kanji_grade_6_count = Column(Integer, default=0)
    kanji_secondary_count = Column(Integer, default=0)
    kanji_uncommon_count = Column(Integer, default=0)

    # Bunsetsu Statistics
    total_bunsetsu_count = Column(Integer, default=0)
    avg_bunsetsu_length = Column(Float, default=0.0)
    max_bunsetsu_length = Column(Integer, default=0)
    min_bunsetsu_length = Column(Integer, default=0)

    # Lexical Density
    total_words = Column(Integer, default=0)
    unique_words = Column(Integer, default=0)
    lexical_density = Column(Float, default=0.0)

    # Word Frequencies (stored as JSON)
    word_frequencies = Column(JSON)

    # Special Word Categories (stored as JSON lists)
    onomatopoeia = Column(JSON)
    proper_nouns = Column(JSON)
    archaic_words = Column(JSON)

    # Timestamp
    analyzed_at = Column(DateTime, server_default=func.now())

    # Relationship
    song = relationship("Song", back_populates="analysis")