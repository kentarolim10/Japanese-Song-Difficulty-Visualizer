from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey                                        
from sqlalchemy.orm import relationship                     
from sqlalchemy.sql import func                             
from app.database import Base                               
                                                              
                                                              
class Artist(Base):                                         
    __tablename__ = "artists"                               
                                                            
    id = Column(Integer, primary_key=True, index=True)      
    genius_id = Column(Integer, unique=True, index=True)    
    name = Column(String(255), nullable=False)              
    created_at = Column(DateTime, server_default=func.now())
                                                            
    songs = relationship("Song", back_populates="artist")   
                                                            
                                                            
class Song(Base):                                           
    __tablename__ = "songs"                                 
                                                            
    id = Column(Integer, primary_key=True, index=True)      
    genius_id = Column(Integer, unique=True, index=True)    
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)                                             
    title = Column(String(255), nullable=False)             
    lyrics = Column(Text)                                   
    created_at = Column(DateTime, server_default=func.now())
                                                            
    artist = relationship("Artist", back_populates="songs")