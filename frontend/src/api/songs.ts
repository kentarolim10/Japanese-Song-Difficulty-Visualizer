import type { PaginatedSongsResponse, SortField, SortOrder } from "../types";

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
