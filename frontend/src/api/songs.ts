import type {
  PaginatedSongsResponse,
  SortField,
  SortOrder,
  AddSongResponse,
  Song,
  SongAverages,
  ArtistAverages,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface GetSongsParams {
  page?: number;
  pageSize?: number;
  sortBy?: SortField;
  order?: SortOrder;
  search?: string;
}

export async function getSongs({
  page = 1,
  pageSize = 20,
  sortBy = "unique_kanji_count",
  order = "asc",
  search,
}: GetSongsParams = {}): Promise<PaginatedSongsResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
    sort_by: sortBy,
    order,
  });

  if (search) {
    params.set("search", search);
  }

  const response = await fetch(`${API_BASE_URL}/songs?${params}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch songs: ${response.statusText}`);
  }

  return response.json();
}

export async function addSongByUrl(url: string): Promise<AddSongResponse> {
  const response = await fetch(`${API_BASE_URL}/songs/add-by-url`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to add song: ${response.statusText}`);
  }

  return response.json();
}

export async function getSong(id: number): Promise<Song> {
  const response = await fetch(`${API_BASE_URL}/songs/${id}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch song: ${response.statusText}`);
  }

  return response.json();
}

export async function getSongAverages(): Promise<SongAverages> {
  const response = await fetch(`${API_BASE_URL}/songs/stats/averages`);

  if (!response.ok) {
    throw new Error(`Failed to fetch averages: ${response.statusText}`);
  }

  return response.json();
}

export async function getArtistAverages(artistId: number): Promise<ArtistAverages> {
  const response = await fetch(`${API_BASE_URL}/songs/stats/artist/${artistId}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch artist averages: ${response.statusText}`);
  }

  return response.json();
}

