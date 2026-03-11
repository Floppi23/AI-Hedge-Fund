import type { RunResponse, AgentOutput, FinalSignal } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function fetchRuns(): Promise<RunResponse[]> {
  return apiFetch("/research/runs");
}

export async function fetchRun(id: string): Promise<RunResponse> {
  return apiFetch(`/research/runs/${id}`);
}

export async function fetchAgentOutputs(runId: string): Promise<AgentOutput[]> {
  return apiFetch(`/research/runs/${runId}/agents`);
}

export async function fetchFinalSignal(runId: string): Promise<FinalSignal> {
  return apiFetch(`/research/runs/${runId}/final-signal`);
}

export async function fetchSignals(): Promise<FinalSignal[]> {
  return apiFetch("/signals");
}

export async function createRun(body: {
  asset_id: string;
  analysis_mode?: string;
  time_horizon?: string;
}): Promise<RunResponse> {
  return apiFetch("/research/runs", {
    method: "POST",
    body: JSON.stringify(body),
  });
}
