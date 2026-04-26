export type Skill = {
  skill_id: string;
  name: string;
  category: string;
  importance: string;
  source: string;
  evidence: string;
  assessment_required: boolean;
};

export type SkillExtractionResult = {
  required_skills: Skill[];
  resume_skills: Skill[];
  overlap_skills: Skill[];
  assessment_targets: Skill[];
};

export type Question = {
  question_id: string;
  skill_id: string;
  skill_name: string;
  question: string;
  type: string;
  difficulty: string;
  expected_signals: string[];
  follow_up_allowed: boolean;
  answered: boolean;
};

export type Evaluation = {
  skill_id: string;
  skill_name: string;
  concept_score: number;
  application_score: number;
  final_score: number;
  confidence: string;
  justification: string;
  evidence: string[];
};

export type Gap = {
  skill: string;
  severity: string;
  gap_type: string;
  reason: string;
  role_criticality: string;
};

export type AdjacentSkill = {
  skill: string;
  rationale: string;
  acquisition_difficulty: string;
  estimated_weeks: number;
  why_adjacent: string;
};

export type Resource = {
  title: string;
  url: string;
  resource_type: string;
  free: boolean;
};

export type LearningStep = {
  step: number;
  focus: string;
  skill_gap: string;
  time_estimate: string;
  weekly_hours: number;
  resources: Resource[];
  outcome: string;
  is_adjacent_skill: boolean;
};

export type Report = {
  readiness_percent: number;
  summary: string;
  skill_evaluation: Evaluation[];
  key_gaps: Gap[];
  adjacent_skills: AdjacentSkill[];
  learning_plan: LearningStep[];
  total_weeks_to_readiness: number | null;
  final_recommendation: string;
  ai_status?: Record<string, string>;
  llm_config?: {
    gemini_api_key_configured: boolean;
    gemini_model: string;
  };
};

export type SessionSummary = {
  session_id: string;
  title: string;
  readiness_percent: number | null;
  last_updated: string;
  status: "completed" | "in_progress";
};

export type SessionState = {
  session_id: string;
  job_description: string;
  resume: string;
  extracted_skills: SkillExtractionResult | null;
  questions: Question[];
  answers: Array<{ question_id: string }>;
  final_report: Record<string, unknown>;
};
