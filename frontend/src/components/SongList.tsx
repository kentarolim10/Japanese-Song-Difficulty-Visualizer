import { Link } from "react-router-dom";
import type { Song, SortField } from "../types";

interface SongListProps {
  songs: Song[];
  sortBy: SortField;
}

const SORT_LABELS: Record<SortField, string> = {
  unique_kanji_count: "Unique Kanji",
  total_kanji_count: "Total Kanji",
  lexical_density: "Lexical Density",
  avg_bunsetsu_length: "Avg Phrase Length",
  jlpt_n1_count: "JLPT N1 Words",
  total_words: "Total Words",
};

function getDifficultyValue(song: Song, sortBy: SortField): string {
  const value = song.analysis[sortBy];
  if (typeof value === "number") {
    return sortBy === "lexical_density" ? value.toFixed(3) : value.toString();
  }
  return "-";
}

function getDifficultyColor(song: Song, sortBy: SortField): string {
  const value = song.analysis[sortBy];
  if (typeof value !== "number") return "bg-gray-100 text-gray-800";

  // Normalize based on typical ranges
  let normalized: number;
  switch (sortBy) {
    case "unique_kanji_count":
      normalized = Math.min(value / 100, 1);
      break;
    case "total_kanji_count":
      normalized = Math.min(value / 200, 1);
      break;
    case "lexical_density":
      normalized = value;
      break;
    case "avg_bunsetsu_length":
      normalized = Math.min(value / 10, 1);
      break;
    case "jlpt_n1_count":
      normalized = Math.min(value / 50, 1);
      break;
    case "total_words":
      normalized = Math.min(value / 500, 1);
      break;
    default:
      normalized = 0.5;
  }

  if (normalized < 0.33) return "bg-green-100 text-green-800";
  if (normalized < 0.66) return "bg-yellow-100 text-yellow-800";
  return "bg-red-100 text-red-800";
}

export default function SongList({ songs, sortBy }: SongListProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Song
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Artist
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              {SORT_LABELS[sortBy]}
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              JLPT Breakdown
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {songs.map((song) => (
            <tr key={song.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <Link
                  to={`/song/${song.id}`}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  {song.title}
                </Link>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                {song.artist_name}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getDifficultyColor(
                    song,
                    sortBy,
                  )}`}
                >
                  {getDifficultyValue(song, sortBy)}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex gap-1 text-xs">
                  <span className="px-1.5 py-0.5 bg-green-50 text-green-700 rounded">
                    N5: {song.analysis.jlpt_n5_count}
                  </span>
                  <span className="px-1.5 py-0.5 bg-lime-50 text-lime-700 rounded">
                    N4: {song.analysis.jlpt_n4_count}
                  </span>
                  <span className="px-1.5 py-0.5 bg-yellow-50 text-yellow-700 rounded">
                    N3: {song.analysis.jlpt_n3_count}
                  </span>
                  <span className="px-1.5 py-0.5 bg-orange-50 text-orange-700 rounded">
                    N2: {song.analysis.jlpt_n2_count}
                  </span>
                  <span className="px-1.5 py-0.5 bg-red-50 text-red-700 rounded">
                    N1: {song.analysis.jlpt_n1_count}
                  </span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
