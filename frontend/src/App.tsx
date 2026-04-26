import { useEffect, useState } from "react";

import { ReportView } from "./components/ReportView";
import { SkillList } from "./components/SkillList";
import {
  createSession,
  deleteSession,
  evaluateAnswer,
  extractSkills,
  generateLearningPlan,
  getNextQuestion,
  getReport,
  getSession,
  listSessions,
  submitAnswer,
} from "./services/api";
import type { Question, Report, SessionSummary, SkillExtractionResult } from "./types/api";
import "./styles.css";

type Stage = "input" | "skills" | "assessment" | "report";

export default function App() {
  const [stage, setStage] = useState<Stage>("input");
  const [jobDescription, setJobDescription] = useState("");
  const [resume, setResume] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [skills, setSkills] = useState<SkillExtractionResult | null>(null);
  const [question, setQuestion] = useState<Question | null>(null);
  const [answer, setAnswer] = useState("");
  const [report, setReport] = useState<Report | null>(null);
  const [history, setHistory] = useState<SessionSummary[]>([]);
  const [historyQuery, setHistoryQuery] = useState("");
  const [historyStatusFilter, setHistoryStatusFilter] = useState<"all" | "completed" | "in_progress">("all");
  const [answeredCount, setAnsweredCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const totalQuestions = Math.max((skills?.assessment_targets.length ?? 0) * 2, 2);

  async function run<T>(action: () => Promise<T>) {
    setLoading(true);
    setError("");
    try {
      return await action();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      return null;
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refreshHistory();
  }, []);

  async function refreshHistory() {
    const items = await run(() => listSessions());
    if (!items) return;
    setHistory(items);
  }

  async function startAssessment() {
    const session = await run(() => createSession(jobDescription, resume));
    if (!session) return;
    setSessionId(session.session_id);
    const extracted = await run(() => extractSkills(session.session_id));
    if (!extracted) return;
    setSkills(extracted);
    setAnsweredCount(0);
    setStage("skills");
    await refreshHistory();
  }

  async function beginQuestions() {
    const next = await run(() => getNextQuestion(sessionId));
    if (!next) return;
    setQuestion(next);
    setStage("assessment");
  }

  async function openPastAssessment(id: string) {
    const session = await run(() => getSession(id));
    if (!session) return;

    setSessionId(session.session_id);
    setJobDescription(session.job_description);
    setResume(session.resume);
    setSkills(session.extracted_skills);
    setAnsweredCount(session.answers.length);
    setAnswer("");

    const hasFinalReport = Boolean(session.final_report && Object.keys(session.final_report).length > 0);
    if (hasFinalReport) {
      const finalReport = await run(() => getReport(id));
      if (!finalReport) return;
      setReport(finalReport);
      setStage("report");
      return;
    }

    if (session.extracted_skills) {
      const next = await run(() => getNextQuestion(id));
      if (next) {
        setQuestion(next);
        setStage("assessment");
        return;
      }
      setStage("skills");
      return;
    }

    setStage("input");
  }

  async function removePastAssessment(id: string) {
    const confirmed = window.confirm("Delete this assessment permanently?");
    if (!confirmed) return;
    const deleted = await run(() => deleteSession(id));
    if (deleted === null) return;
    if (sessionId === id) {
      setSessionId("");
      setJobDescription("");
      setResume("");
      setSkills(null);
      setQuestion(null);
      setAnswer("");
      setReport(null);
      setAnsweredCount(0);
      setStage("input");
    }
    await refreshHistory();
  }

  const filteredHistory = history.filter((item) => {
    if (historyStatusFilter !== "all" && item.status !== historyStatusFilter) return false;
    const query = historyQuery.trim().toLowerCase();
    if (!query) return true;
    return (
      item.title.toLowerCase().includes(query) ||
      item.session_id.toLowerCase().includes(query)
    );
  });

  function formatLocalDate(value: string) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(date);
  }

  async function submitCurrentAnswer() {
    if (!question || !answer.trim()) return;
    const submitted = await run(() => submitAnswer(sessionId, question.question_id, answer));
    if (!submitted) return;
    const evaluated = await run(() => evaluateAnswer(sessionId, question.question_id));
    if (!evaluated) return;
    setAnsweredCount((count) => count + 1);
    setAnswer("");
    const next = await run(() => getNextQuestion(sessionId));
    if (next) {
      setQuestion(next);
      return;
    }

    await run(() => generateLearningPlan(sessionId));
    const finalReport = await run(() => getReport(sessionId));
    if (finalReport) {
      setReport(finalReport);
      setStage("report");
    }
  }

  return (
    <main>
      <header>
        <p>AI Skill Assessment Agent</p>
        <h1>Evaluate real role readiness from answers, not claims.</h1>
      </header>

      {error && <div className="error">{error}</div>}

      {stage === "input" && (
        <>
          <section className="input-grid">
            <label>
              Job Description
              <textarea
                value={jobDescription}
                onChange={(event) => setJobDescription(event.target.value)}
                placeholder="Paste the target role description..."
              />
            </label>
            <label>
              Candidate Resume
              <textarea
                value={resume}
                onChange={(event) => setResume(event.target.value)}
                placeholder="Paste the resume content..."
              />
            </label>
            <button disabled={loading} onClick={startAssessment}>
              {loading ? "Extracting..." : "Extract Skills"}
            </button>
          </section>

          <section className="panel history-panel">
            <div className="history-header">
              <h2>Past Assessments</h2>
              <button disabled={loading} onClick={refreshHistory}>
                Refresh
              </button>
            </div>
            <div className="history-controls">
              <input
                type="search"
                value={historyQuery}
                onChange={(event) => setHistoryQuery(event.target.value)}
                placeholder="Search by title or session id..."
              />
              <select
                value={historyStatusFilter}
                onChange={(event) =>
                  setHistoryStatusFilter(event.target.value as "all" | "completed" | "in_progress")
                }
              >
                <option value="all">All</option>
                <option value="completed">Completed</option>
                <option value="in_progress">In Progress</option>
              </select>
            </div>
            {history.length === 0 ? (
              <p className="muted">No previous assessments found yet.</p>
            ) : filteredHistory.length === 0 ? (
              <p className="muted">No assessments match your current filters.</p>
            ) : (
              <ul className="history-list">
                {filteredHistory.map((item) => (
                  <li key={item.session_id}>
                    <div>
                      <strong>{item.title}</strong>
                      <p className="muted">
                        {item.readiness_percent === null ? "Readiness: pending" : `Readiness: ${item.readiness_percent}%`}
                      </p>
                      <small className="muted">Updated: {formatLocalDate(item.last_updated)}</small>
                    </div>
                    <div className="history-actions">
                      <button disabled={loading} onClick={() => openPastAssessment(item.session_id)}>
                        {item.status === "completed" ? "Open Report" : "Continue"}
                      </button>
                      <button
                        disabled={loading}
                        className="danger"
                        onClick={() => removePastAssessment(item.session_id)}
                      >
                        Delete
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}

      {stage === "skills" && skills && (
        <>
          <div className="skills-grid">
            <SkillList title="JD Skills" skills={skills.required_skills} />
            <SkillList title="Resume Skills" skills={skills.resume_skills} />
            <SkillList title="Assessment Targets" skills={skills.assessment_targets} />
          </div>
          <button disabled={loading} onClick={beginQuestions}>
            {loading ? "Preparing..." : "Begin Assessment"}
          </button>
        </>
      )}

      {stage === "assessment" && question && (
        <section className="question-card">
          <p>{question.skill_name}</p>
          <div className="progress">
            <span>
              Question {Math.min(answeredCount + 1, totalQuestions)} of {totalQuestions}
            </span>
            <progress max={totalQuestions} value={Math.min(answeredCount, totalQuestions)} />
          </div>
          <h2>{question.question}</h2>
          <textarea
            value={answer}
            onChange={(event) => setAnswer(event.target.value)}
            placeholder="Answer with concrete reasoning, examples, and outcomes..."
          />
          <button disabled={loading || !answer.trim()} onClick={submitCurrentAnswer}>
            {loading ? "Evaluating..." : "Submit Answer"}
          </button>
        </section>
      )}

      {stage === "report" && report && <ReportView report={report} />}
    </main>
  );
}
