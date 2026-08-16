export type ModelStatus = "running" | "loading" | "available" | "unavailable";

export interface WorkspaceModel {
  id: string;
  name: string;
  params: string;
  quant: string;
  sizeGb: number;
  ctxMax: number;
  status: ModelStatus;
}

export interface RagSource {
  source: string;
  score: number;
  chunk: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  time: string;
  text: string;
  ragSources?: RagSource[];
  tokensGenerated?: number;
  tookMs?: number;
  isError?: boolean;
}

export interface Session {
  id: string;
  title: string;
  preview: string;
  time: string;
  messages: ChatMessage[];
}

export interface CurrentUser {
  id: string;
  email: string;
  display_name: string;
}

export interface HealthSnapshot {
  cpuPercent?: number;
  ramPercent?: number;
  gpuPercent?: number;
  ramTotalGb?: number;
  ramUsedGb?: number;
  modelLoaded?: boolean;
  reachable: boolean;
}

export interface TtftStats {
  p50Ms: number | null;
  samples: number;
}
