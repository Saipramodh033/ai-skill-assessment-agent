import type { Question, Report, SessionState, SessionSummary, SkillExtractionResult } from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let detail = "Request failed";
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // body may not be JSON
    }
    throw new Error(`[${response.status}] ${detail}`);
  }

  // 204 No Content — return undefined safely
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function createSession(jobDescription: string, resume: string) {
  return request<{ session_id: string }>("/sessions", {
    method: "POST",
    body: JSON.stringify({ job_description: jobDescription, resume }),
  });
}

export async function listSessions() {
  return request<SessionSummary[]>("/sessions");
}

export async function getSession(sessionId: string) {
  return request<SessionState>(`/sessions/${sessionId}`);
}

export async function deleteSession(sessionId: string) {
  return request<void>(`/sessions/${sessionId}`, { method: "DELETE" });
}

export async function extractSkills(sessionId: string) {
  return request<SkillExtractionResult>(`/sessions/${sessionId}/extract-skills`, {
    method: "POST",
  });
}

export async function getNextQuestion(sessionId: string) {
  return request<Question | null>(`/sessions/${sessionId}/next-question`);
}

export async function submitAnswer(sessionId: string, questionId: string, answer: string) {
  return request(`/sessions/${sessionId}/answers`, {
    method: "POST",
    body: JSON.stringify({ question_id: questionId, answer }),
  });
}

export async function evaluateAnswer(sessionId: string, questionId: string) {
  return request(`/sessions/${sessionId}/evaluate/${questionId}`, {
    method: "POST",
  });
}

export async function generateLearningPlan(sessionId: string) {
  return request(`/sessions/${sessionId}/learning-plan`, {
    method: "POST",
  });
}

export async function getReport(sessionId: string) {
  return request<Report>(`/sessions/${sessionId}/report`);
}
