from lyricsgenius import Genius

token = "0iOr6il3Ln7UoU5sfCqXSpI5i4uETv7OWhBSH5NOiPvwdDPG06mnyCMgf-jQfGoE"

genius = Genius(token)
artist = genius.search_artist("yorushika", max_songs=10, sort="popularity")
if artist:
    for song in artist.songs:
        print (song.lyrics) if song.lyrics else print("No lyrics")