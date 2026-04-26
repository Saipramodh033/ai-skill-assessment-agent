import { useEffect, useState } from "react";

import { LoadingOverlay } from "./components/LoadingOverlay";
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
type LoadingStage = "extracting" | "generating" | "evaluating" | "gaps" | "plan" | "report" | null;

export default function App() {
  const [stage, setStage] = useState<Stage>("input");
  const [loadingStage, setLoadingStage] = useState<LoadingStage>(null);
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
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [error, setError] = useState("");

  const isLoading = loadingStage !== null;

  async function run<T>(loadStage: LoadingStage, action: () => Promise<T>): Promise<T | null> {
    setLoadingStage(loadStage);
    setError("");
    try {
      return await action();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong";
      setError(msg);
      return null;
    } finally {
      setLoadingStage(null);
    }
  }

  useEffect(() => {
    void refreshHistory();
  }, []);

  async function refreshHistory() {
    const items = await run(null, () => listSessions());
    if (items) setHistory(items);
  }

  async function startAssessment() {
    const session = await run("extracting", () => createSession(jobDescription, resume));
    if (!session) return;
    setSessionId(session.session_id);

    const extracted = await run("extracting", () => extractSkills(session.session_id));
    if (!extracted) return;
    setSkills(extracted);
    setAnsweredCount(0);
    setTotalQuestions(extracted.assessment_targets.length * 3);
    setStage("skills");
    void refreshHistory();
  }

  async function beginQuestions() {
    const next = await run("generating", () => getNextQuestion(sessionId));
    if (!next) return;
    setQuestion(next);
    setStage("assessment");
  }

  async function openPastAssessment(id: string) {
    const session = await run(null, () => getSession(id));
    if (!session) return;

    setSessionId(session.session_id);
    setJobDescription(session.job_description);
    setResume(session.resume);
    setSkills(session.extracted_skills);
    setAnsweredCount(session.answers.length);
    setAnswer("");
    if (session.extracted_skills) {
      setTotalQuestions(session.extracted_skills.assessment_targets.length * 3);
    }

    const hasFinalReport = Boolean(session.final_report && Object.keys(session.final_report).length > 0);
    if (hasFinalReport) {
      const finalReport = await run("report", () => getReport(id));
      if (!finalReport) return;
      setReport(finalReport);
      setStage("report");
      return;
    }

    if (session.extracted_skills) {
      const next = await run("generating", () => getNextQuestion(id));
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
    const deleted = await run(null, () => deleteSession(id));
    if (deleted === null) return;
    if (sessionId === id) {
      resetState();
    }
    void refreshHistory();
  }

  function resetState() {
    setSessionId("");
    setJobDescription("");
    setResume("");
    setSkills(null);
    setQuestion(null);
    setAnswer("");
    setReport(null);
    setAnsweredCount(0);
    setTotalQuestions(0);
    setStage("input");
    setError("");
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

    const submitted = await run("evaluating", () =>
      submitAnswer(sessionId, question.question_id, answer)
    );
    if (!submitted) return;

    const evaluated = await run("evaluating", () =>
      evaluateAnswer(sessionId, question.question_id)
    );
    if (!evaluated) return;
    setAnsweredCount((count) => count + 1);
    setAnswer("");

    const next = await run("generating", () => getNextQuestion(sessionId));
    if (next) {
      setQuestion(next);
      return;
    }

    // All questions answered — generate learning plan and report
    const plan = await run("plan", () => generateLearningPlan(sessionId));
    if (!plan) return;

    const finalReport = await run("report", () => getReport(sessionId));
    if (finalReport) {
      setReport(finalReport);
      setStage("report");
      void refreshHistory();
    }
  }

  const progressPercent = totalQuestions > 0 ? Math.round((answeredCount / totalQuestions) * 100) : 0;

  return (
    <>
      {isLoading && <LoadingOverlay stage={loadingStage!} />}

      <div className={`app-shell ${isLoading ? "app-blurred" : ""}`}>
        <header className="app-header" id="top">
          <div className="header-inner">
            <div className="header-brand">
              <span className="brand-icon">⚡</span>
              <span className="brand-name">SkillProbe</span>
              <span className="brand-tag">AI Assessment</span>
            </div>
            {stage !== "input" && (
              <button className="btn-ghost" onClick={resetState} title="Start over">
                ← New Assessment
              </button>
            )}
          </div>
        </header>

        <main className="app-main">
          {error && (
            <div className="error-banner" role="alert">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
              <button className="error-dismiss" onClick={() => setError("")}>✕</button>
            </div>
          )}

          {/* ── INPUT STAGE ─────────────────────────────────────────── */}
          {stage === "input" && (
            <div className="input-stage" id="input-stage">
              <div className="hero-section">
                <h1 className="hero-title">
                  Assess real skills,<br />
                  <span className="gradient-text">not paper claims.</span>
                </h1>
                <p className="hero-subtitle">
                  Paste a job description and a resume. Our AI agent conducts a
                  conversational technical assessment, identifies genuine gaps,
                  and builds a personalised learning plan with curated resources.
                </p>
              </div>

              <div className="input-grid" id="input-form">
                <div className="input-field">
                  <label htmlFor="jd-input" className="field-label">
                    <span className="field-icon">📋</span> Job Description
                  </label>
                  <textarea
                    id="jd-input"
                    className="textarea"
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    placeholder="Paste the full job description here…"
                    rows={12}
                  />
                  <span className="field-hint">Include responsibilities, required skills, and tech stack.</span>
                </div>
                <div className="input-field">
                  <label htmlFor="resume-input" className="field-label">
                    <span className="field-icon">📄</span> Candidate Resume
                  </label>
                  <textarea
                    id="resume-input"
                    className="textarea"
                    value={resume}
                    onChange={(e) => setResume(e.target.value)}
                    placeholder="Paste the resume text here…"
                    rows={12}
                  />
                  <span className="field-hint">Plain text is sufficient — no need to format.</span>
                </div>
              </div>

              <div className="input-actions">
                <button
                  id="start-btn"
                  className="btn-primary btn-lg"
                  disabled={isLoading || !jobDescription.trim() || !resume.trim()}
                  onClick={startAssessment}
                >
                  {isLoading ? "Analysing…" : "Start Assessment →"}
                </button>
              </div>

              {/* History Panel */}
              <section className="history-panel" id="history-panel" aria-label="Past assessments">
                <div className="history-header">
                  <h2>Past Assessments</h2>
                  <button className="btn-ghost btn-sm" disabled={isLoading} onClick={refreshHistory}>
                    Refresh
                  </button>
                </div>
                <div className="history-controls">
                  <input
                    id="history-search"
                    type="search"
                    className="search-input"
                    value={historyQuery}
                    onChange={(e) => setHistoryQuery(e.target.value)}
                    placeholder="Search by title or session ID…"
                  />
                  <select
                    id="history-filter"
                    className="filter-select"
                    value={historyStatusFilter}
                    onChange={(e) => setHistoryStatusFilter(e.target.value as "all" | "completed" | "in_progress")}
                  >
                    <option value="all">All</option>
                    <option value="completed">Completed</option>
                    <option value="in_progress">In Progress</option>
                  </select>
                </div>
                {history.length === 0 ? (
                  <p className="muted-text">No previous assessments yet. Start one above.</p>
                ) : filteredHistory.length === 0 ? (
                  <p className="muted-text">No assessments match your filters.</p>
                ) : (
                  <ul className="history-list">
                    {filteredHistory.map((item) => (
                      <li key={item.session_id} className="history-item">
                        <div className="history-info">
                          <strong className="history-title">{item.title}</strong>
                          <div className="history-meta">
                            <span className={`badge badge-sm ${item.status === "completed" ? "badge-green" : "badge-amber"}`}>
                              {item.status === "completed" ? "Complete" : "In Progress"}
                            </span>
                            {item.readiness_percent !== null && (
                              <span className="history-readiness">{item.readiness_percent}% ready</span>
                            )}
                            <span className="muted-text">Updated: {formatLocalDate(item.last_updated)}</span>
                          </div>
                        </div>
                        <div className="history-actions">
                          <button
                            className="btn-secondary btn-sm"
                            disabled={isLoading}
                            onClick={() => openPastAssessment(item.session_id)}
                          >
                            {item.status === "completed" ? "View Report" : "Resume"}
                          </button>
                          <button
                            className="btn-danger btn-sm"
                            disabled={isLoading}
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
            </div>
          )}

          {/* ── SKILLS STAGE ────────────────────────────────────────── */}
          {stage === "skills" && skills && (
            <div className="skills-stage" id="skills-stage">
              <div className="stage-header">
                <h1 className="stage-title">Skill Analysis Complete</h1>
                <p className="stage-desc">
                  We identified {skills.assessment_targets.length} skills to assess.
                  Each will have {3} adaptive questions tailored to your background.
                </p>
              </div>

              <div className="skills-grid">
                <SkillList title="Role Requirements" icon="📋" skills={skills.required_skills} />
                <SkillList title="Your Skills" icon="📄" skills={skills.resume_skills} />
                <SkillList title="Assessment Targets" icon="🎯" skills={skills.assessment_targets} highlight />
              </div>

              <div className="stage-actions">
                <button
                  id="begin-assessment-btn"
                  className="btn-primary btn-lg"
                  disabled={isLoading}
                  onClick={beginQuestions}
                >
                  Begin Assessment →
                </button>
              </div>
            </div>
          )}

          {/* ── ASSESSMENT STAGE ─────────────────────────────────────── */}
          {stage === "assessment" && question && (
            <div className="assessment-stage" id="assessment-stage">
              <div className="assessment-progress">
                <div className="progress-info">
                  <span className="skill-badge">{question.skill_name}</span>
                  <span className="progress-text">
                    Question {answeredCount + 1} of {totalQuestions || "…"}
                  </span>
                </div>
                <div className="progress-track">
                  <div
                    className="progress-fill"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
              </div>

              <div className="question-card" id="question-card">
                <div className="question-meta">
                  <span className={`difficulty-badge difficulty-${question.difficulty}`}>
                    {question.difficulty}
                  </span>
                  <span className="question-type">{question.type}</span>
                </div>
                <h2 className="question-text">{question.question}</h2>

                {question.expected_signals.length > 0 && (
                  <details className="signals-hint">
                    <summary>What are we looking for?</summary>
                    <ul className="signals-list">
                      {question.expected_signals.map((sig, i) => (
                        <li key={i}>{sig}</li>
                      ))}
                    </ul>
                  </details>
                )}

                <textarea
                  id="answer-input"
                  className="answer-textarea"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Answer with concrete reasoning, real examples, and outcomes. Depth matters more than length."
                  rows={8}
                  disabled={isLoading}
                />
                <div className="answer-actions">
                  <span className="answer-hint">
                    {answer.trim().split(/\s+/).filter(Boolean).length} words
                  </span>
                  <button
                    id="submit-answer-btn"
                    className="btn-primary"
                    disabled={isLoading || !answer.trim()}
                    onClick={submitCurrentAnswer}
                  >
                    Submit Answer →
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* ── REPORT STAGE ─────────────────────────────────────────── */}
          {stage === "report" && report && (
            <ReportView report={report} onReset={resetState} />
          )}
        </main>

        <footer className="app-footer">
          <p>SkillProbe · Powered by Gemini AI · Assessment results are AI-generated</p>
        </footer>
      </div>
    </>
  );
}
