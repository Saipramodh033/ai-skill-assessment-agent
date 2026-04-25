import type { Report } from "../types/api";

type Props = {
  report: Report;
};

export function ReportView({ report }: Props) {
  return (
    <section className="report">
      <div className="readiness">
        <span>Role readiness</span>
        <strong>{report.readiness_percent}%</strong>
        <p>{report.summary}</p>
        {report.llm_config && (
          <p className="muted">
            AI source: {report.llm_config.gemini_api_key_configured ? "Gemini configured" : "Gemini not configured"} ·
            {" "}Model:{" "}
            {report.llm_config.gemini_model}
          </p>
        )}
      </div>

      {report.ai_status && (
        <section className="panel">
          <h2>AI Trace</h2>
          <ul className="skill-list">
            {Object.entries(report.ai_status).map(([stage, status]) => (
              <li key={stage}>
                <strong>{stage.replace("_", " ")}</strong>
                <span>{status}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <h2>Skill Evaluation</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Skill</th>
              <th>Score /10</th>
              <th>Confidence</th>
              <th>Justification</th>
            </tr>
          </thead>
          <tbody>
            {report.skill_evaluation.map((evaluation) => (
              <tr key={evaluation.skill_id}>
                <td>{evaluation.skill_name}</td>
                <td>{evaluation.final_score}</td>
                <td>{evaluation.confidence}</td>
                <td>{evaluation.justification}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Key Gaps</h2>
      {report.key_gaps.length === 0 ? (
        <p className="muted">No high-impact gaps were identified from the completed assessment.</p>
      ) : (
        <ul className="gap-list">
          {report.key_gaps.map((gap) => (
            <li key={`${gap.skill}-${gap.severity}`}>
              <strong>{gap.skill}</strong>
              <span>{gap.severity}</span>
              <p>{gap.reason}</p>
            </li>
          ))}
        </ul>
      )}

      <h2>Learning Plan</h2>
      <div className="steps">
        {report.learning_plan.map((step) => (
          <article key={step.step}>
            <span>Step {step.step}</span>
            <h3>{step.focus}</h3>
            <p className="muted">{step.time_estimate}</p>
            <ul>
              {step.resources.map((resource) => (
                <li key={resource}>{resource}</li>
              ))}
            </ul>
            <p>{step.outcome}</p>
          </article>
        ))}
      </div>

      <h2>Final Recommendation</h2>
      <p>{report.final_recommendation}</p>
    </section>
  );
}
