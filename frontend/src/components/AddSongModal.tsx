import { useState } from "react";
import { addSongByUrl } from "../api/songs";
import type { AddSongResponse } from "../types";

interface AddSongModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSongAdded: () => void;
}

export default function AddSongModal({
  isOpen,
  onClose,
  onSongAdded,
}: AddSongModalProps) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<AddSongResponse | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      const response = await addSongByUrl(url);
      setSuccess(response);
      setUrl("");
      onSongAdded();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add song");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setUrl("");
    setError(null);
    setSuccess(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Add Song</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label
              htmlFor="genius-url"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Genius Song URL
            </label>
            <input
              id="genius-url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://genius.com/Artist-song-title-lyrics"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={loading}
            />
            <p className="mt-1 text-xs text-gray-500">
              Paste a link to any song page on{" "}
              <a
                href="https://genius.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-yellow-400"
              >
                genius.com
              </a>
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded text-sm">
              <p className="font-medium">{success.message}</p>
              <p className="mt-1">
                Added: {success.title} by {success.artist_name}
              </p>
            </div>
          )}

          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
              disabled={loading}
            >
              {success ? "Close" : "Cancel"}
            </button>
            {!success && (
              <button
                type="submit"
                disabled={loading || !url.trim()}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Adding..." : "Add Song"}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
