#!/usr/bin/env python3
"""
Seed script to fetch popular Japanese artists from Last.fm and add them via the API.
"""

import os
import sys
import time
import requests

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
MAX_ARTISTS = 50
LASTFM_BASE_URL = "http://ws.audioscrobbler.com/2.0/"


def fetch_japanese_artists(page: int = 1, limit: int = 50) -> list[dict]:
    """Fetch top artists tagged as 'japanese' using Last.fm tag.getTopArtists."""
    params = {
        "method": "tag.gettopartists",
        "tag": "japanese",
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "page": page,
        "limit": limit,
    }

    response = requests.get(LASTFM_BASE_URL, params=params)
    response.raise_for_status()

    data = response.json()
    return data.get("topartists", {}).get("artist", [])


def add_artist_to_api(artist_name: str) -> dict:
    """Call the /artists/add endpoint to add an artist."""
    url = f"{API_BASE_URL}/artists/add"
    response = requests.post(url, json={"artist_name": artist_name})
    response.raise_for_status()
    return response.json()


def main():
    if not LASTFM_API_KEY:
        print("Error: LASTFM_API_KEY environment variable is required")
        sys.exit(1)

    print(f"Fetching artists tagged 'japanese' from Last.fm (max {MAX_ARTISTS} artists)...")
    print(f"API endpoint: {API_BASE_URL}/artists/add")
    print("-" * 50)

    page = 1
    total_added = 0
    total_songs = 0

    while total_added < MAX_ARTISTS:
        print(f"\nFetching page {page}...")
        artists = fetch_japanese_artists(page=page)

        if not artists:
            print("No more artists found.")
            break

        print(f"Found {len(artists)} artists on this page")

        for artist in artists:
            if total_added >= MAX_ARTISTS:
                break

            name = artist["name"]
            print(f"  Processing: {name}...")
            try:
                result = add_artist_to_api(name)
                songs_saved = result.get("songs_saved", 0)
                total_songs += songs_saved
                total_added += 1
                print(f"  + {name} - {songs_saved} songs saved ({total_added}/{MAX_ARTISTS})")
            except requests.exceptions.HTTPError as e:
                print(f"  x {name} - Error: {e}")
            except Exception as e:
                print(f"  x {name} - Error: {e}")

            # Small delay to avoid overwhelming the API
            time.sleep(0.5)

        page += 1

    print("-" * 50)
    print(f"Done! Added {total_added} artists with {total_songs} total songs.")


if __name__ == "__main__":
    main()
