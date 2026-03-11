export interface RunResponse {
  id: string;
  org_id: string | null;
  asset_id: string;
  status: "pending" | "running" | "completed" | "blocked" | "failed";
  analysis_mode: string;
  time_horizon: string;
  model_bundle_version: string | null;
  started_at: string | null;
  finished_at: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface AgentOutput {
  id: string;
  run_id: string;
  agent_name: string;
  prompt_version: string | null;
  model_version: string | null;
  stance: "bullish" | "bearish" | "neutral" | null;
  score: number | null;
  confidence: number | null;
  is_valid: boolean;
  validation_errors: Record<string, unknown> | null;
  output_json: Record<string, unknown>;
  created_at: string;
}

export interface FinalSignal {
  id: string;
  run_id: string;
  final_stance: "bullish" | "bearish" | "neutral";
  final_score: number;
  final_confidence: number;
  risk_override: boolean;
  release_status: "approved" | "blocked" | "needs_review";
  summary: string | null;
  contributing_agents: string[] | null;
  blocked_reasons: string[] | null;
  created_at: string;
}
