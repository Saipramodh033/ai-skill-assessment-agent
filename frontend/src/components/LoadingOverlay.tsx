import { useEffect, useState } from "react";

type Props = {
  stage: string;
  message?: string;
};

const STAGE_MESSAGES: Record<string, string> = {
  extracting: "Analysing job description and resume…",
  generating: "Generating adaptive question…",
  evaluating: "Evaluating your answer…",
  gaps: "Identifying skill gaps…",
  plan: "Building your personalised learning plan…",
  report: "Compiling final report…",
};

const TIPS = [
  "Tip: Depth of experience matters more than listing 50 frameworks on your resume.",
  "Tip: When answering, structure your response using the STAR method (Situation, Task, Action, Result).",
  "Tip: Admitting what you don't know but explaining how you'd figure it out is often a strong signal.",
  "Tip: Interviewers look for how you handle trade-offs, not just whether you know the syntax.",
  "Tip: 'Adjacent skills' are the easiest way to level up your career trajectory.",
  "Tip: Highlight the business impact of your technical work on your resume.",
  "Tip: A good system design answer considers failure modes and scalability limits.",
  "Tip: Keep your resume concise—recruiters spend seconds scanning it before an interview.",
];

export function LoadingOverlay({ stage, message }: Props) {
  const [tipIndex, setTipIndex] = useState(0);
  const [fade, setFade] = useState(true);
  const label = message ?? STAGE_MESSAGES[stage] ?? "Processing…";

  // Cycle tips every 4 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setFade(false); // trigger fade out
      setTimeout(() => {
        setTipIndex((prev) => (prev + 1) % TIPS.length);
        setFade(true); // trigger fade in
      }, 300); // wait for CSS fade transition
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-overlay" role="status" aria-live="polite">
      <div className="loading-content">
        <div className="spinner-ring">
          <div />
          <div />
          <div />
          <div />
        </div>
        <p className="loading-label">{label}</p>
        <div className="loading-dots">
          <span /><span /><span />
        </div>
        <div className="loading-tip-container">
          <p className={`loading-tip ${fade ? "fade-in" : "fade-out"}`}>
            💡 {TIPS[tipIndex]}
          </p>
        </div>
      </div>
    </div>
  );
}
