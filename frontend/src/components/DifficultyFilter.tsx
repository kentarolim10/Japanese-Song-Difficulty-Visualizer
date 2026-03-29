import type { SortField, SortOrder } from "../types";

interface DifficultyFilterProps {
  sortBy: SortField;
  order: SortOrder;
  onSortChange: (sortBy: SortField) => void;
  onOrderToggle: () => void;
}

const SORT_OPTIONS: { value: SortField; label: string }[] = [
  { value: "unique_kanji_count", label: "Unique Kanji" },
  { value: "total_kanji_count", label: "Total Kanji" },
  { value: "lexical_density", label: "Lexical Density" },
  { value: "jlpt_n1_count", label: "JLPT N1 Words" },
  { value: "total_words", label: "Total Words" },
];

export default function DifficultyFilter({
  sortBy,
  order,
  onSortChange,
  onOrderToggle,
}: DifficultyFilterProps) {
  return (
    <div className="flex items-center gap-2">
      <label className="text-sm text-gray-600">Sort by:</label>
      <select
        value={sortBy}
        onChange={(e) => onSortChange(e.target.value as SortField)}
        className="block px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
      >
        {SORT_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <button
        onClick={onOrderToggle}
        className="px-3 py-2 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        title={
          order === "asc"
            ? "Ascending (easiest first)"
            : "Descending (hardest first)"
        }
      >
        {order === "asc" ? (
          <svg
            className="w-5 h-5 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
            />
          </svg>
        ) : (
          <svg
            className="w-5 h-5 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4"
            />
          </svg>
        )}
      </button>
    </div>
  );
}
