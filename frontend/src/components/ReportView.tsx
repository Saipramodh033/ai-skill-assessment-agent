import type { AdjacentSkill, Evaluation, Gap, LearningStep, Report, Resource } from "../types/api";
import { ReadinessGauge } from "./ReadinessGauge";
import { SkillRadar } from "./SkillRadar";

type Props = {
  report: Report;
  onReset: () => void;
};

const RESOURCE_ICON: Record<string, string> = {
  course: "🎓",
  book: "📚",
  docs: "📖",
  video: "▶️",
  article: "📝",
};

const DIFFICULTY_CLASS: Record<string, string> = {
  easy: "badge-green",
  medium: "badge-amber",
  hard: "badge-red",
};

const SEVERITY_CLASS: Record<string, string> = {
  high: "badge-red",
  medium: "badge-amber",
};

const CRITICALITY_CLASS: Record<string, string> = {
  critical: "badge-red",
  high: "badge-orange",
  medium: "badge-amber",
  low: "badge-muted",
};

function ResourceCard({ resource }: { resource: Resource }) {
  const icon = RESOURCE_ICON[resource.resource_type] ?? "🔗";
  const hasUrl = resource.url && resource.url.startsWith("http");
  return (
    <div className="resource-card">
      <span className="resource-icon">{icon}</span>
      <div className="resource-info">
        {hasUrl ? (
          <a href={resource.url} target="_blank" rel="noopener noreferrer" className="resource-title">
            {resource.title}
          </a>
        ) : (
          <span className="resource-title">{resource.title}</span>
        )}
        <span className={`resource-badge ${resource.free ? "badge-green" : "badge-muted"}`}>
          {resource.free ? "Free" : "Paid"}
        </span>
      </div>
    </div>
  );
}

function GapCard({ gap }: { gap: Gap }) {
  let typeLabel = "Failed Assessment";
  let typeClass = "badge-red";
  if (gap.gap_type === "missing_from_resume") {
    typeLabel = "Missing from Resume";
    typeClass = "badge-orange";
  } else if (gap.gap_type === "unassessed") {
    typeLabel = "Unassessed / Needs Verification";
    typeClass = "badge-muted";
  }

  return (
    <div className={`gap-card gap-${gap.severity} gap-${gap.gap_type}`}>
      <div className="gap-header">
        <strong className="gap-skill">{gap.skill}</strong>
        <div className="gap-badges">
          <span className={`badge ${typeClass}`}>{typeLabel}</span>
          <span className={`badge ${SEVERITY_CLASS[gap.severity] ?? "badge-muted"}`}>{gap.severity} severity</span>
          <span className={`badge ${CRITICALITY_CLASS[gap.role_criticality] ?? "badge-muted"}`}>
            {gap.role_criticality} priority
          </span>
        </div>
      </div>
      <p className="gap-reason">{gap.reason}</p>
    </div>
  );
}

function AdjacentSkillCard({ adj }: { adj: AdjacentSkill }) {
  return (
    <div className="adjacent-card">
      <div className="adjacent-header">
        <span className="adjacent-icon">🚀</span>
        <strong className="adjacent-skill">{adj.skill}</strong>
        <span className={`badge ${DIFFICULTY_CLASS[adj.acquisition_difficulty] ?? "badge-muted"}`}>
          {adj.acquisition_difficulty}
        </span>
        <span className="badge badge-purple">{adj.estimated_weeks}w</span>
      </div>
      <p className="adjacent-rationale">{adj.rationale}</p>
      {adj.why_adjacent && (
        <p className="adjacent-bridge">
          <span className="bridge-label">Bridge:</span> {adj.why_adjacent}
        </p>
      )}
    </div>
  );
}

function EvalRow({ ev }: { ev: Evaluation }) {
  const scoreColor =
    ev.final_score >= 7 ? "#4ade80" : ev.final_score >= 5 ? "#fbbf24" : "#f87171";
  return (
    <tr className="eval-row">
      <td className="eval-skill">{ev.skill_name}</td>
      <td>
        <div className="score-cell">
          <span className="score-value" style={{ color: scoreColor }}>
            {ev.final_score.toFixed(1)}
          </span>
          <div className="score-bar-track">
            <div
              className="score-bar-fill"
              style={{ width: `${ev.final_score * 10}%`, background: scoreColor }}
            />
          </div>
        </div>
      </td>
      <td>
        <span className="concept-score">{ev.concept_score.toFixed(1)}</span>
      </td>
      <td>
        <span className="app-score">{ev.application_score.toFixed(1)}</span>
      </td>
      <td>
        <span className={`badge badge-sm ${ev.confidence === "high" ? "badge-green" : ev.confidence === "medium" ? "badge-amber" : "badge-red"}`}>
          {ev.confidence}
        </span>
      </td>
      <td className="eval-justification">{ev.justification}</td>
    </tr>
  );
}

function LearningStepCard({ step }: { step: LearningStep }) {
  return (
    <div className={`step-card ${step.is_adjacent_skill ? "step-adjacent" : ""}`}>
      <div className="step-number">
        <span>{step.step}</span>
      </div>
      <div className="step-body">
        <div className="step-header">
          <h3 className="step-focus">{step.focus}</h3>
          {step.is_adjacent_skill && (
            <span className="badge badge-purple">Adjacent Skill</span>
          )}
        </div>
        {step.skill_gap && (
          <p className="step-gap-label">
            Addresses: <strong>{step.skill_gap}</strong>
          </p>
        )}
        <div className="step-meta">
          <span className="step-time">⏱ {step.time_estimate}</span>
          {step.weekly_hours > 0 && (
            <span className="step-hours">~{step.weekly_hours}h/week</span>
          )}
        </div>
        <p className="step-outcome">
          <span className="outcome-label">Milestone:</span> {step.outcome}
        </p>
        {step.resources.length > 0 && (
          <div className="step-resources">
            {step.resources.map((r, i) => (
              <ResourceCard key={i} resource={r} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export function ReportView({ report, onReset }: Props) {
  const hasAdjacent = report.adjacent_skills && report.adjacent_skills.length > 0;
  const gapSteps = report.learning_plan.filter((s) => !s.is_adjacent_skill);
  const adjacentSteps = report.learning_plan.filter((s) => s.is_adjacent_skill);

  return (
    <section className="report-view" id="report">
      {/* Hero Section */}
      <div className="report-overview-grid">
        <div className="overview-card readiness-card">
          <h3 className="card-subtitle">Role Readiness</h3>
          <ReadinessGauge percent={report.readiness_percent} size={220} />
          <div className="readiness-meta">
            <p className="readiness-summary">{report.summary}</p>
            {report.total_weeks_to_readiness && (
              <div className="readiness-timeline">
                <span className="timeline-icon">📅</span>
                <span>Estimated <strong>{report.total_weeks_to_readiness} weeks</strong> to role readiness</span>
              </div>
            )}
          </div>
        </div>

        {report.skill_evaluation.length >= 2 && (
          <div className="overview-card radar-card">
            <h3 className="card-subtitle">Skill Profile Overview</h3>
            <div className="radar-container">
              <SkillRadar evaluations={report.skill_evaluation} size={280} />
            </div>
          </div>
        )}
      </div>

      {/* Skill Evaluation Table */}
      <div className="report-section">
        <h2 className="section-title">
          <span className="section-icon">🎯</span> Skill Evaluation
        </h2>
        <div className="table-wrap">
          <table className="eval-table">
            <thead>
              <tr>
                <th>Skill</th>
                <th>Overall /10</th>
                <th>Concept</th>
                <th>Application</th>
                <th>Confidence</th>
                <th>Justification</th>
              </tr>
            </thead>
            <tbody>
              {report.skill_evaluation.map((ev) => (
                <EvalRow key={ev.skill_id} ev={ev} />
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Key Gaps */}
      <div className="report-section">
        <h2 className="section-title">
          <span className="section-icon">⚠️</span> Identified Gaps
        </h2>
        {report.key_gaps.some(g => g.gap_type === "unassessed") && (
          <p className="section-desc">
            Note: Some skills claimed on the resume could not be fully assessed due to time constraints, but the resume evidence was weak. These require further verification.
          </p>
        )}
        {report.key_gaps.length === 0 ? (
          <p className="muted-text">No significant gaps identified. Candidate demonstrates strong role readiness.</p>
        ) : (
          <div className="gap-grid">
            {report.key_gaps.map((gap, i) => (
              <GapCard key={i} gap={gap} />
            ))}
          </div>
        )}
      </div>

      {/* Adjacent Skills */}
      {hasAdjacent && (
        <div className="report-section">
          <h2 className="section-title">
            <span className="section-icon">🚀</span> Growth Opportunities
          </h2>
          <p className="section-desc">
            Skills you can realistically acquire given your existing background and demonstrated strengths.
          </p>
          <div className="adjacent-grid">
            {report.adjacent_skills.map((adj, i) => (
              <AdjacentSkillCard key={i} adj={adj} />
            ))}
          </div>
        </div>
      )}

      {/* Learning Plan */}
      <div className="report-section">
        <h2 className="section-title">
          <span className="section-icon">📚</span> Personalised Learning Plan
        </h2>
        {gapSteps.length > 0 && (
          <>
            <h3 className="subsection-title">Gap Closing Steps</h3>
            <div className="steps-list">
              {gapSteps.map((step) => (
                <LearningStepCard key={step.step} step={step} />
              ))}
            </div>
          </>
        )}
        {adjacentSteps.length > 0 && (
          <>
            <h3 className="subsection-title">Adjacent Skill Path</h3>
            <div className="steps-list">
              {adjacentSteps.map((step) => (
                <LearningStepCard key={step.step} step={step} />
              ))}
            </div>
          </>
        )}
      </div>

      {/* Final Recommendation */}
      <div className="report-section recommendation-section">
        <h2 className="section-title">
          <span className="section-icon">✅</span> Final Recommendation
        </h2>
        <p className="recommendation-text">{report.final_recommendation}</p>
      </div>

      {/* Actions */}
      <div className="report-actions">
        <button className="btn-secondary" onClick={() => window.print()}>
          Export PDF
        </button>
        <button className="btn-primary" onClick={onReset}>
          Start New Assessment
        </button>
      </div>

      {/* Debug AI Trace (collapsed) */}
      {report.ai_status && (
        <details className="ai-trace">
          <summary>AI Pipeline Trace</summary>
          <ul className="trace-list">
            {Object.entries(report.ai_status).map(([stage, status]) => (
              <li key={stage}>
                <span className="trace-stage">{stage.replace(/_/g, " ")}</span>
                <span className={`trace-status ${status.startsWith("error") ? "trace-error" : "trace-ok"}`}>
                  {status}
                </span>
              </li>
            ))}
          </ul>
          {report.llm_config && (
            <p className="trace-model">
              Model: {report.llm_config.gemini_model} ·{" "}
              {report.llm_config.gemini_api_key_configured ? "API key configured" : "API key missing"}
            </p>
          )}
        </details>
      )}
    </section>
  );
}
