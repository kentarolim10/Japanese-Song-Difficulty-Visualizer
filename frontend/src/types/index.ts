export interface SongAnalysis {
  id: number;
  song_id: number;

  // JLPT Vocabulary
  jlpt_n5_count: number;
  jlpt_n4_count: number;
  jlpt_n3_count: number;
  jlpt_n2_count: number;
  jlpt_n1_count: number;
  jlpt_unknown_count: number;

  // Kanji
  total_kanji_count: number;
  unique_kanji_count: number;
  kanji_grade_1_count: number;
  kanji_grade_2_count: number;
  kanji_grade_3_count: number;
  kanji_grade_4_count: number;
  kanji_grade_5_count: number;
  kanji_grade_6_count: number;
  kanji_secondary_count: number;
  kanji_uncommon_count: number;

  // Bunsetsu
  total_bunsetsu_count: number;
  max_bunsetsu_length: number;
  min_bunsetsu_length: number;

  // Lexical
  total_words: number;
  unique_words: number;
  lexical_density: number;

  // Word frequencies
  word_frequencies: Record<string, number>;

  // Special word categories
  onomatopoeia?: string[];
  proper_nouns?: string[];
  archaic_words?: string[];

  analyzed_at: string;
}

export interface Song {
  id: number;
  genius_id: number;
  title: string;
  artist_id: number;
  artist_name: string;
  thumbnail_url: string | null;
  created_at: string;
  analysis: SongAnalysis;
}

export interface PaginatedSongsResponse {
  items: Song[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export type SortField =
  | "unique_kanji_count"
  | "total_kanji_count"
  | "lexical_density"
  | "jlpt_n1_count"
  | "total_words";

export type SortOrder = "asc" | "desc";

// Add song by URL
export interface AddSongRequest {
  url: string;
}

export interface AddSongResponse {
  id: number;
  genius_id: number;
  title: string;
  artist_name: string;
  thumbnail_url: string | null;
  message: string;
}

// Stats
export interface SongAverages {
  unique_kanji_count: number;
  total_kanji_count: number;
  lexical_density: number;
  total_words: number;
}

export interface ArtistAverages {
  artist_id: number;
  artist_name: string;
  song_count: number;
  unique_kanji_count: number | null;
  total_kanji_count: number | null;
  lexical_density: number | null;
  total_words: number | null;
}
