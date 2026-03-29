import { useEffect, useRef } from "react";
import * as d3 from "d3";
import type { SongAnalysis, SongAverages, ArtistAverages } from "../../types";

interface ParallelCoordinatesProps {
  song: SongAnalysis;
  averages: SongAverages;
  artistAverages?: ArtistAverages | null;
}

interface Dimension {
  key: keyof SongAverages;
  label: string;
  domain: [number, number];
}

const DIMENSIONS: Dimension[] = [
  { key: "unique_kanji_count", label: "Unique Kanji", domain: [0, 150] },
  { key: "total_kanji_count", label: "Total Kanji", domain: [0, 300] },
  { key: "lexical_density", label: "Lexical Density", domain: [0, 1] },
  { key: "total_words", label: "Total Words", domain: [0, 600] },
];

export default function ParallelCoordinates({
  song,
  averages,
  artistAverages,
}: ParallelCoordinatesProps) {
  // Check if artist has enough songs to show artist average
  const showArtistLine = artistAverages && artistAverages.song_count >= 2;
  const svgRef = useRef<SVGSVGElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const margin = { top: 40, right: 50, bottom: 60, left: 50 };
    const width = 600;
    const height = 300;
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Clear previous content
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3
      .select(svgRef.current)
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("preserveAspectRatio", "xMidYMid meet");

    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create scales for each dimension
    const xScale = d3
      .scalePoint<string>()
      .domain(DIMENSIONS.map((d) => d.key))
      .range([0, innerWidth]);

    const yScales: Record<string, d3.ScaleLinear<number, number>> = {};
    DIMENSIONS.forEach((dim) => {
      yScales[dim.key] = d3
        .scaleLinear()
        .domain(dim.domain)
        .range([innerHeight, 0]);
    });

    // Draw axes
    DIMENSIONS.forEach((dim) => {
      const xPos = xScale(dim.key)!;

      // Axis line
      g.append("line")
        .attr("x1", xPos)
        .attr("y1", 0)
        .attr("x2", xPos)
        .attr("y2", innerHeight)
        .attr("stroke", "#e5e7eb")
        .attr("stroke-width", 1);

      // Axis ticks and labels
      const axis = d3.axisLeft(yScales[dim.key]).ticks(5);
      g.append("g")
        .attr("transform", `translate(${xPos},0)`)
        .call(axis)
        .selectAll("text")
        .attr("font-size", "10px")
        .attr("fill", "#6b7280");

      // Dimension label
      g.append("text")
        .attr("x", xPos)
        .attr("y", -15)
        .attr("text-anchor", "middle")
        .attr("font-size", "12px")
        .attr("font-weight", "500")
        .attr("fill", "#374151")
        .text(dim.label);
    });

    const avgLine = d3
      .line<Dimension>()
      .x((d) => xScale(d.key)!)
      .y((d) => yScales[d.key](averages[d.key]));

    g.append("path")
      .datum(DIMENSIONS)
      .attr("d", avgLine)
      .attr("fill", "none")
      .attr("stroke", "#9ca3af")
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", "5,5");

    // Tooltip reference for use in point handlers
    const tooltip = d3.select(tooltipRef.current);

    // Draw average points with tooltip
    DIMENSIONS.forEach((dim) => {
      const xPos = xScale(dim.key)!;
      const yPos = yScales[dim.key](averages[dim.key]);
      const value =
        dim.key === "lexical_density"
          ? averages[dim.key].toFixed(2)
          : Math.round(averages[dim.key]);

      g.append("circle")
        .attr("cx", xPos)
        .attr("cy", yPos)
        .attr("r", 5)
        .attr("fill", "#9ca3af")
        .attr("stroke", "white")
        .attr("stroke-width", 1)
        .style("cursor", "pointer")
        .on("mouseover", (event) => {
          tooltip
            .style("opacity", 1)
            .html(`${dim.label} (avg): ${value}`)
            .style("left", `${event.offsetX + 10}px`)
            .style("top", `${event.offsetY - 10}px`);
        })
        .on("mouseout", () => {
          tooltip.style("opacity", 0);
        });
    });

    // Draw artist average line (dotted, orange) if available
    if (showArtistLine && artistAverages) {
      const artistLine = d3
        .line<Dimension>()
        .x((d) => xScale(d.key)!)
        .y((d) => {
          const val = artistAverages[d.key];
          return yScales[d.key](val ?? 0);
        });

      g.append("path")
        .datum(DIMENSIONS)
        .attr("d", artistLine)
        .attr("fill", "none")
        .attr("stroke", "#f97316")
        .attr("stroke-width", 2)
        .attr("stroke-dasharray", "2,2");

      // Draw artist average points with tooltip
      DIMENSIONS.forEach((dim) => {
        const val = artistAverages[dim.key];
        if (val === null) return;

        const xPos = xScale(dim.key)!;
        const yPos = yScales[dim.key](val);
        const displayValue =
          dim.key === "lexical_density" ? val.toFixed(2) : Math.round(val);

        g.append("circle")
          .attr("cx", xPos)
          .attr("cy", yPos)
          .attr("r", 5)
          .attr("fill", "#f97316")
          .attr("stroke", "white")
          .attr("stroke-width", 1)
          .style("cursor", "pointer")
          .on("mouseover", (event) => {
            tooltip
              .style("opacity", 1)
              .html(`${dim.label} (artist): ${displayValue}`)
              .style("left", `${event.offsetX + 10}px`)
              .style("top", `${event.offsetY - 10}px`);
          })
          .on("mouseout", () => {
            tooltip.style("opacity", 0);
          });
      });
    }

    const songLine = d3
      .line<Dimension>()
      .x((d) => xScale(d.key)!)
      .y((d) => yScales[d.key](song[d.key]));

    g.append("path")
      .datum(DIMENSIONS)
      .attr("d", songLine)
      .attr("fill", "none")
      .attr("stroke", "#3b82f6")
      .attr("stroke-width", 2.5);

    // Draw current song points with tooltip
    DIMENSIONS.forEach((dim) => {
      const xPos = xScale(dim.key)!;
      const yPos = yScales[dim.key](song[dim.key]);
      const value =
        dim.key === "lexical_density"
          ? song[dim.key].toFixed(2)
          : Math.round(song[dim.key]);

      g.append("circle")
        .attr("cx", xPos)
        .attr("cy", yPos)
        .attr("r", 6)
        .attr("fill", "#3b82f6")
        .attr("stroke", "white")
        .attr("stroke-width", 2)
        .style("cursor", "pointer")
        .on("mouseover", (event) => {
          tooltip
            .style("opacity", 1)
            .html(`${dim.label}: ${value}`)
            .style("left", `${event.offsetX + 10}px`)
            .style("top", `${event.offsetY - 10}px`);
        })
        .on("mouseout", () => {
          tooltip.style("opacity", 0);
        });
    });

    // Calculate legend position based on number of items
    const legendOffset = showArtistLine ? -130 : -80;
    const legend = svg
      .append("g")
      .attr("transform", `translate(${width / 2 + legendOffset}, ${height - 15})`);

    // Current song legend
    let xOffset = 0;
    legend
      .append("line")
      .attr("x1", xOffset)
      .attr("y1", 0)
      .attr("x2", xOffset + 20)
      .attr("y2", 0)
      .attr("stroke", "#3b82f6")
      .attr("stroke-width", 2.5);
    legend
      .append("text")
      .attr("x", xOffset + 25)
      .attr("y", 4)
      .attr("font-size", "11px")
      .attr("fill", "#374151")
      .text("This Song");

    // Global average legend
    xOffset = 90;
    legend
      .append("line")
      .attr("x1", xOffset)
      .attr("y1", 0)
      .attr("x2", xOffset + 20)
      .attr("y2", 0)
      .attr("stroke", "#9ca3af")
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", "5,5");
    legend
      .append("text")
      .attr("x", xOffset + 25)
      .attr("y", 4)
      .attr("font-size", "11px")
      .attr("fill", "#374151")
      .text("Global Avg");

    // Artist average legend (if shown)
    if (showArtistLine) {
      xOffset = 180;
      legend
        .append("line")
        .attr("x1", xOffset)
        .attr("y1", 0)
        .attr("x2", xOffset + 20)
        .attr("y2", 0)
        .attr("stroke", "#f97316")
        .attr("stroke-width", 2)
        .attr("stroke-dasharray", "2,2");
      legend
        .append("text")
        .attr("x", xOffset + 25)
        .attr("y", 4)
        .attr("font-size", "11px")
        .attr("fill", "#374151")
        .text("Artist Avg");
    }
  }, [song, averages, artistAverages, showArtistLine]);

  return (
    <div className="bg-white rounded-lg shadow-sm border p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Difficulty Comparison
      </h3>
      <div className="relative">
        <svg ref={svgRef} className="w-full" style={{ maxHeight: "320px" }} />
        <div
          ref={tooltipRef}
          className="absolute pointer-events-none bg-gray-900 text-white text-xs px-2 py-1 rounded shadow-lg"
          style={{ opacity: 0, transition: "opacity 0.15s" }}
        />
      </div>
    </div>
  );
}
