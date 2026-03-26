import subprocess
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Song, Artist


def clear_database():
    """Delete all records from songs and artists tables."""
    db = SessionLocal()
    try:
        # Delete songs first (foreign key constraint)
        deleted_songs = db.query(Song).delete()
        deleted_artists = db.query(Artist).delete()
        db.commit()
        print(f"Cleared {deleted_songs} songs and {deleted_artists} artists")
    finally:
        db.close()


def run_seed_script():
    """Run the seed_artists.py script as a subprocess."""
    script_path = Path(__file__).parent / "seed_artists.py"
    result = subprocess.run([sys.executable, str(script_path)], check=True)
    return result.returncode


if __name__ == "__main__":
    print("Clearing database...")
    clear_database()
    print("Running seed script...")
    run_seed_script()
    print("Done!")
