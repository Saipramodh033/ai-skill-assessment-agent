import type { Question, Report, SkillExtractionResult } from "../types/api";

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
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail ?? "Request failed");
  }

  return response.json() as Promise<T>;
}

export async function createSession(jobDescription: string, resume: string) {
  return request<{ session_id: string }>("/sessions", {
    method: "POST",
    body: JSON.stringify({ job_description: jobDescription, resume }),
  });
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
