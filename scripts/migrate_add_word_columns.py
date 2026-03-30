"""
Migration script to add onomatopoeia, proper_nouns, and archaic_words columns
to the song_analyses table.

Run this script once after updating the model.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine

def migrate():
    """Add new JSON columns to song_analyses table."""
    columns_to_add = [
        ("onomatopoeia", "JSONB"),
        ("proper_nouns", "JSONB"),
        ("archaic_words", "JSONB"),
    ]

    with engine.connect() as conn:
        for column_name, column_type in columns_to_add:
            try:
                conn.execute(text(
                    f"ALTER TABLE song_analyses ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
                ))
                print(f"Added column: {column_name}")
            except Exception as e:
                print(f"Column {column_name} may already exist: {e}")
        conn.commit()

    print("Migration completed!")

if __name__ == "__main__":
    migrate()
