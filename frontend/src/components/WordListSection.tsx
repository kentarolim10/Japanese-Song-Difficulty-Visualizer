import type { SongAnalysis } from "../types";

interface WordListSectionProps {
  analysis: SongAnalysis;
}

interface WordCategoryProps {
  title: string;
  words: string[];
  colorClass: string;
}

function WordCategory({ title, words, colorClass }: WordCategoryProps) {
  if (!words || words.length === 0) return null;

  return (
    <div className="mb-4">
      <h4 className="text-sm font-medium text-gray-700 mb-2">
        {title} ({words.length})
      </h4>
      <div className="flex flex-wrap gap-1.5">
        {words.map((word, index) => (
          <span
            key={`${word}-${index}`}
            className={`inline-block px-2 py-0.5 text-sm rounded ${colorClass}`}
          >
            {word}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function WordListSection({ analysis }: WordListSectionProps) {
  const hasOnomatopoeia = analysis.onomatopoeia && analysis.onomatopoeia.length > 0;
  const hasProperNouns = analysis.proper_nouns && analysis.proper_nouns.length > 0;
  const hasArchaicWords = analysis.archaic_words && analysis.archaic_words.length > 0;

  const hasAnyWords = hasOnomatopoeia || hasProperNouns || hasArchaicWords;

  if (!hasAnyWords) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-4 h-full">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Special Words
        </h3>
        <p className="text-gray-500 text-sm">No special words detected.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-4 h-full">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Special Words
      </h3>

      <WordCategory
        title="Onomatopoeia"
        words={analysis.onomatopoeia || []}
        colorClass="bg-purple-100 text-purple-800"
      />

      <WordCategory
        title="Proper Nouns"
        words={analysis.proper_nouns || []}
        colorClass="bg-blue-100 text-blue-800"
      />

      <WordCategory
        title="Archaic Words"
        words={analysis.archaic_words || []}
        colorClass="bg-amber-100 text-amber-800"
      />
    </div>
  );
}
