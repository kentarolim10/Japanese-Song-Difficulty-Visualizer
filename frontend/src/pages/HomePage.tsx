import { useState, useEffect, useCallback, useRef } from "react";
import { getSongs } from "../api/songs";
import type { Song, SortField, SortOrder } from "../types";
import SongList from "../components/SongList";
import SearchBar from "../components/SearchBar";
import DifficultyFilter from "../components/DifficultyFilter";
import AddSongModal from "../components/AddSongModal";

export default function HomePage() {
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [sortBy, setSortBy] = useState<SortField>("unique_kanji_count");
  const [order, setOrder] = useState<SortOrder>("asc");
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  // Reset when filters change
  useEffect(() => {
    setSongs([]);
    setPage(1);
    setHasMore(true);
  }, [sortBy, order, debouncedSearch]);

  // Fetch songs
  const fetchSongs = useCallback(async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    setError(null);

    try {
      const response = await getSongs({
        page,
        sortBy,
        order,
        search: debouncedSearch || undefined,
      });

      setSongs((prev) =>
        page === 1 ? response.items : [...prev, ...response.items],
      );
      setHasMore(response.has_more);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch songs");
    } finally {
      setLoading(false);
    }
  }, [page, sortBy, order, debouncedSearch, loading, hasMore]);

  // Fetch on page/filter change
  useEffect(() => {
    fetchSongs();
  }, [page, sortBy, order, debouncedSearch, fetchSongs]);

  // Infinite scroll observer
  useEffect(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loading) {
          setPage((prev) => prev + 1);
        }
      },
      { threshold: 0.1 },
    );

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [hasMore, loading]);

  const handleSortChange = (newSortBy: SortField) => {
    setSortBy(newSortBy);
  };

  const handleOrderToggle = () => {
    setOrder((prev) => (prev === "asc" ? "desc" : "asc"));
  };

  const handleSongAdded = () => {
    // Reset and refetch songs
    setSongs([]);
    setPage(1);
    setHasMore(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <SearchBar value={search} onChange={setSearch} />
        <DifficultyFilter
          sortBy={sortBy}
          order={order}
          onSortChange={handleSortChange}
          onOrderToggle={handleOrderToggle}
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <SongList songs={songs} sortBy={sortBy} />

      {/* Infinite scroll trigger */}
      <div ref={loadMoreRef} className="h-10 flex items-center justify-center">
        {loading && <div className="text-gray-500">Loading more songs...</div>}
        {!hasMore && songs.length > 0 && (
          <div className="text-gray-400">No more songs to load</div>
        )}
      </div>

      {!loading && songs.length === 0 && (
        <div className="text-center py-10">
          <p className="text-gray-500 mb-4">
            {debouncedSearch
              ? `No songs found for "${debouncedSearch}".`
              : "No songs found. Add some songs to get started."}
          </p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Add Song via Genius Link
          </button>
        </div>
      )}

      <AddSongModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSongAdded={handleSongAdded}
      />
    </div>
  );
}
