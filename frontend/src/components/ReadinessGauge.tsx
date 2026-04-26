type Props = {
  percent: number;
  size?: number;
};

export function ReadinessGauge({ percent, size = 180 }: Props) {
  const radius = size * 0.38;
  const cx = size / 2;
  const cy = size / 2;
  const circumference = Math.PI * radius; // half circle
  const clamped = Math.min(Math.max(percent, 0), 100);
  const filled = (clamped / 100) * circumference;

  const color =
    clamped >= 75 ? "#4ade80"
    : clamped >= 50 ? "#fbbf24"
    : "#f87171";

  const label =
    clamped >= 75 ? "Role Ready"
    : clamped >= 50 ? "Partially Ready"
    : "Needs Prep";

  return (
    <div className="readiness-gauge" aria-label={`Readiness: ${clamped}%`}>
      <svg width={size} height={size * 0.6} viewBox={`0 0 ${size} ${size * 0.6}`} overflow="visible">
        {/* Track */}
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke="rgba(255,255,255,0.08)"
          strokeWidth={size * 0.07}
          strokeLinecap="round"
        />
        {/* Fill */}
        <path
          className="gauge-fill"
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke={color}
          strokeWidth={size * 0.07}
          strokeLinecap="round"
          strokeDasharray={`${filled} ${circumference}`}
          style={{
            filter: `drop-shadow(0 0 8px ${color})`,
            transition: "stroke-dasharray 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)",
          }}
        />
      </svg>
      <div className="gauge-text">
        <span className="gauge-percent" style={{ color }}>{clamped}%</span>
        <span className="gauge-label">{label}</span>
      </div>
    </div>
  );
}
