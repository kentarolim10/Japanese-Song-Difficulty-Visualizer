import { useState, useEffect, useRef } from "react";
import * as d3 from "d3";
import type { SongAnalysis, VocabItem } from "../types";

interface JLPTSectionProps {
  analysis: SongAnalysis;
}

type JLPTLevel = "N5" | "N4" | "N3" | "N2" | "N1";

const LEVELS: JLPTLevel[] = ["N5", "N4", "N3", "N2", "N1"];
const LEVEL_COLORS: Record<JLPTLevel, string> = {
  N5: "#22c55e", // green
  N4: "#84cc16", // lime
  N3: "#eab308", // yellow
  N2: "#f97316", // orange
  N1: "#ef4444", // red
};

export default function JLPTSection({ analysis }: JLPTSectionProps) {
  const [selectedLevel, setSelectedLevel] = useState<JLPTLevel>("N5");
  const svgRef = useRef<SVGSVGElement>(null);

  // Get counts for each level
  const counts: Record<JLPTLevel, number> = {
    N5: analysis.jlpt_n5_count,
    N4: analysis.jlpt_n4_count,
    N3: analysis.jlpt_n3_count,
    N2: analysis.jlpt_n2_count,
    N1: analysis.jlpt_n1_count,
  };

  // Get vocab items for selected level (enriched with reading/definition)
  const vocabItems: VocabItem[] = analysis.jlpt_vocab?.[selectedLevel] || [];

  // Draw bar chart
  useEffect(() => {
    if (!svgRef.current) return;

    const margin = { top: 20, right: 30, bottom: 20, left: 35 };
    const width = 250;
    const height = 180;
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3
      .select(svgRef.current)
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("preserveAspectRatio", "xMidYMid meet");

    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const maxCount = Math.max(...LEVELS.map((l) => counts[l]), 1);

    const yScale = d3
      .scaleBand<JLPTLevel>()
      .domain(LEVELS)
      .range([0, innerHeight])
      .padding(0.3);

    const xScale = d3.scaleLinear().domain([0, maxCount]).range([0, innerWidth]);

    // Draw bars
    g.selectAll("rect")
      .data(LEVELS)
      .join("rect")
      .attr("y", (d) => yScale(d)!)
      .attr("x", 0)
      .attr("height", yScale.bandwidth())
      .attr("width", (d) => xScale(counts[d]))
      .attr("fill", (d) => (d === selectedLevel ? LEVEL_COLORS[d] : "#d1d5db"))
      .attr("rx", 4)
      .style("cursor", "pointer")
      .on("click", (_, d) => setSelectedLevel(d));

    // Draw labels
    g.selectAll(".label")
      .data(LEVELS)
      .join("text")
      .attr("class", "label")
      .attr("x", -5)
      .attr("y", (d) => yScale(d)! + yScale.bandwidth() / 2)
      .attr("text-anchor", "end")
      .attr("dominant-baseline", "middle")
      .attr("font-size", "12px")
      .attr("font-weight", (d) => (d === selectedLevel ? "600" : "400"))
      .attr("fill", (d) => (d === selectedLevel ? LEVEL_COLORS[d] : "#6b7280"))
      .text((d) => d);

    // Draw count labels
    g.selectAll(".count")
      .data(LEVELS)
      .join("text")
      .attr("class", "count")
      .attr("x", (d) => xScale(counts[d]) + 5)
      .attr("y", (d) => yScale(d)! + yScale.bandwidth() / 2)
      .attr("dominant-baseline", "middle")
      .attr("font-size", "11px")
      .attr("fill", "#6b7280")
      .text((d) => counts[d]);
  }, [counts, selectedLevel]);

  const getTooltipContent = (item: VocabItem): string => {
    if (item.reading && item.definition) {
      return `${item.word} (${item.reading}): ${item.definition}`;
    } else if (item.reading) {
      return `${item.word} (${item.reading})`;
    }
    return item.word;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        JLPT Vocabulary
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <div>
          <svg ref={svgRef} className="w-full" style={{ maxHeight: "180px" }} />
          <p className="text-xs text-gray-500 text-center mt-1">
            Click a bar to view words
          </p>
        </div>

        {/* Word List */}
        <div>
          <h4
            className="text-sm font-medium mb-2"
            style={{ color: LEVEL_COLORS[selectedLevel] }}
          >
            {selectedLevel} Vocabulary ({vocabItems.length} unique)
          </h4>

          {vocabItems.length > 0 ? (
            <div className="flex flex-wrap gap-1.5 max-h-48 overflow-y-auto">
              {vocabItems.map((item, index) => (
                <span
                  key={`${item.word}-${index}`}
                  className="inline-block px-2 py-0.5 text-sm rounded cursor-help transition-colors hover:text-white"
                  style={{
                    backgroundColor: `${LEVEL_COLORS[selectedLevel]}20`,
                    color: LEVEL_COLORS[selectedLevel],
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.backgroundColor = LEVEL_COLORS[selectedLevel];
                    e.currentTarget.style.color = "white";
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.backgroundColor = `${LEVEL_COLORS[selectedLevel]}20`;
                    e.currentTarget.style.color = LEVEL_COLORS[selectedLevel];
                  }}
                  title={getTooltipContent(item)}
                >
                  {item.word}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No {selectedLevel} words found</p>
          )}
        </div>
      </div>
    </div>
  );
}
