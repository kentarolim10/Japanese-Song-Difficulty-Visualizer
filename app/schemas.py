from pydantic import BaseModel                              
from datetime import datetime                               
                                                              
                                                              
# Request                                                   
class ArtistAddRequest(BaseModel):                       
    artist_name: str                                                                                                    

                                                                                         
# Response                                                                                                                      
class ArtistAddResponse(BaseModel):                      
    songs_saved: int                                  
    message: str  