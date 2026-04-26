import type { Evaluation } from "../types/api";

type Props = {
  evaluations: Evaluation[];
  size?: number;
};

export function SkillRadar({ evaluations, size = 300 }: Props) {
  if (evaluations.length < 3) {
    // Not enough points for a meaningful polygon — show bar fallback
    return (
      <div className="skill-radar-bars">
        {evaluations.map((e) => (
          <div key={e.skill_id} className="radar-bar-row">
            <span className="radar-bar-label">{e.skill_name}</span>
            <div className="radar-bar-track">
              <div
                className="radar-bar-fill"
                style={{ width: `${e.final_score * 10}%`, "--score": e.final_score } as React.CSSProperties}
              />
            </div>
            <span className="radar-bar-score">{e.final_score.toFixed(1)}</span>
          </div>
        ))}
      </div>
    );
  }

  const center = size / 2;
  const radius = size * 0.38;
  const labelRadius = size * 0.48;
  const count = evaluations.length;

  function angleFor(i: number) {
    return (Math.PI * 2 * i) / count - Math.PI / 2;
  }

  function toXY(angle: number, r: number) {
    return { x: center + r * Math.cos(angle), y: center + r * Math.sin(angle) };
  }

  // Grid rings
  const rings = [0.25, 0.5, 0.75, 1.0];

  // Candidate polygon
  const candidatePoints = evaluations.map((e, i) => {
    const angle = angleFor(i);
    const score = Math.min(Math.max(e.final_score / 10, 0), 1);
    return toXY(angle, score * radius);
  });
  const candidatePolygon = candidatePoints.map((p) => `${p.x},${p.y}`).join(" ");

  // Axes
  const axes = evaluations.map((_, i) => {
    const angle = angleFor(i);
    const outer = toXY(angle, radius);
    return { x1: center, y1: center, x2: outer.x, y2: outer.y };
  });

  // Labels
  const labels = evaluations.map((e, i) => {
    const angle = angleFor(i);
    const pos = toXY(angle, labelRadius);
    return { text: e.skill_name, score: e.final_score, x: pos.x, y: pos.y };
  });

  return (
    <svg
      className="skill-radar-svg"
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      aria-label="Skill radar chart"
    >
      {/* Grid rings */}
      {rings.map((r) => {
        const ringPoints = Array.from({ length: count }, (_, i) => {
          const pos = toXY(angleFor(i), r * radius);
          return `${pos.x},${pos.y}`;
        }).join(" ");
        return (
          <polygon
            key={r}
            points={ringPoints}
            fill="none"
            stroke="rgba(124,58,237,0.15)"
            strokeWidth="1"
          />
        );
      })}

      {/* Axis lines */}
      {axes.map((ax, i) => (
        <line
          key={i}
          x1={ax.x1}
          y1={ax.y1}
          x2={ax.x2}
          y2={ax.y2}
          stroke="rgba(124,58,237,0.2)"
          strokeWidth="1"
        />
      ))}

      {/* Candidate fill polygon */}
      <polygon
        points={candidatePolygon}
        fill="rgba(124,58,237,0.18)"
        stroke="#7c3aed"
        strokeWidth="2"
        strokeLinejoin="round"
      />

      {/* Score dots */}
      {candidatePoints.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r={4} fill="#a78bfa" />
      ))}

      {/* Labels */}
      {labels.map((lbl, i) => {
        const color = lbl.score >= 7 ? "#4ade80" : lbl.score >= 5 ? "#fbbf24" : "#f87171";
        return (
          <text
            key={i}
            x={lbl.x}
            y={lbl.y}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize="10"
            fill={color}
            fontFamily="Inter, sans-serif"
            fontWeight="600"
          >
            {lbl.text.length > 12 ? lbl.text.slice(0, 11) + "…" : lbl.text}
          </text>
        );
      })}
    </svg>
  );
}

// Need React import for CSSProperties
import React from "react";
