import { useParams, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { getSong, getSongAverages, getArtistAverages } from "../api/songs";
import type { Song, SongAverages, ArtistAverages } from "../types";
import ParallelCoordinates from "../components/charts/ParallelCoordinates";

export default function SongDashboard() {
  const { id } = useParams<{ id: string }>();
  const [song, setSong] = useState<Song | null>(null);
  const [averages, setAverages] = useState<SongAverages | null>(null);
  const [artistAverages, setArtistAverages] = useState<ArtistAverages | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      if (!id) return;

      setLoading(true);
      setError(null);

      try {
        const [songData, avgData] = await Promise.all([
          getSong(parseInt(id)),
          getSongAverages(),
        ]);
        setSong(songData);
        setAverages(avgData);

        // Fetch artist averages after we have the song
        const artistAvgData = await getArtistAverages(songData.artist_id);
        setArtistAverages(artistAvgData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load song");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error || !song || !averages) {
    return (
      <div className="space-y-6">
        <Link
          to="/"
          className="inline-flex items-center text-blue-600 hover:text-blue-800"
        >
          <svg
            className="w-4 h-4 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to song list
        </Link>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error || "Song not found"}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link
        to="/"
        className="inline-flex items-center text-blue-600 hover:text-blue-800"
      >
        <svg
          className="w-4 h-4 mr-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 19l-7-7 7-7"
          />
        </svg>
        Back to song list
      </Link>

      {/* Song Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center gap-4">
          {song.thumbnail_url ? (
            <img
              src={song.thumbnail_url}
              alt={song.title}
              className="w-20 h-20 rounded-lg object-cover"
            />
          ) : (
            <div className="w-20 h-20 rounded-lg bg-gray-200 flex items-center justify-center">
              <svg
                className="w-8 h-8 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
                />
              </svg>
            </div>
          )}
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{song.title}</h1>
            <p className="text-gray-600">{song.artist_name}</p>
          </div>
        </div>
      </div>

      {/* Parallel Coordinates Chart */}
      <ParallelCoordinates
        song={song.analysis}
        averages={averages}
        artistAverages={artistAverages}
      />
    </div>
  );
}
