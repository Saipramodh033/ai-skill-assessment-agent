import { useState } from "react";

import { ReportView } from "./components/ReportView";
import { SkillList } from "./components/SkillList";
import {
  createSession,
  evaluateAnswer,
  extractSkills,
  generateLearningPlan,
  getNextQuestion,
  getReport,
  submitAnswer,
} from "./services/api";
import type { Question, Report, SkillExtractionResult } from "./types/api";
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

  async function startAssessment() {
    const session = await run(() => createSession(jobDescription, resume));
    if (!session) return;
    setSessionId(session.session_id);
    const extracted = await run(() => extractSkills(session.session_id));
    if (!extracted) return;
    setSkills(extracted);
    setAnsweredCount(0);
    setStage("skills");
  }

  async function beginQuestions() {
    const next = await run(() => getNextQuestion(sessionId));
    setQuestion(next);
    setStage("assessment");
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
