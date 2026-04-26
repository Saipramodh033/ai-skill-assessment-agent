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
  "Tip: When learning a new tool, focus on the 'Why' before the 'How'. Understanding the underlying problem it solves is key.",
  "Tip: Admitting what you don't know but explaining how you'd figure it out is often a stronger signal than guessing.",
  "Tip: Interviewers look for how you handle trade-offs and edge cases, not just whether you know the syntax.",
  "Tip: 'Adjacent skills' are the easiest way to level up your career trajectory. Build on what you already know.",
  "Tip: Highlight the business impact of your technical work on your resume, not just the tech stack.",
  "Tip: A good system design answer considers failure modes, scalability limits, and data consistency.",
  "Tip: Keep your resume concise—recruiters and engineers spend seconds scanning it before an interview.",
  "Tip: Real-world engineering is about maintaining systems, not just building them. Mention debugging and observability.",
  "Tip: The best way to learn a new language is to build a project you actually care about, rather than just following tutorials.",
  "Tip: Code reviews are a critical soft skill. Showing you can give and receive constructive feedback is vital.",
  "Tip: When stuck on a bug, explaining it out loud to a rubber duck (or an AI) often reveals the solution.",
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
    }, 8000);
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
