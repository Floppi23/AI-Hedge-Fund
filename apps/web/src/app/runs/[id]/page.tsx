"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { fetchRun, fetchAgentOutputs, fetchFinalSignal } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";

function statusBadge(status: string) {
  const colors: Record<string, string> = {
    completed: "bg-green-100 text-green-800",
    running: "bg-blue-100 text-blue-800",
    pending: "bg-yellow-100 text-yellow-800",
    blocked: "bg-orange-100 text-orange-800",
    failed: "bg-red-100 text-red-800",
  };
  return <Badge className={colors[status] || ""}>{status}</Badge>;
}

function stanceBadge(stance: string) {
  const colors: Record<string, string> = {
    bullish: "bg-green-100 text-green-800",
    bearish: "bg-red-100 text-red-800",
    neutral: "bg-gray-100 text-gray-800",
  };
  return <Badge className={colors[stance] || ""}>{stance}</Badge>;
}

export default function RunDetailPage() {
  const params = useParams();
  const runId = params.id as string;

  const isTerminal = (status?: string) =>
    status === "completed" || status === "blocked" || status === "failed";

  const { data: run, isLoading: runLoading } = useQuery({
    queryKey: ["run", runId],
    queryFn: () => fetchRun(runId),
    refetchInterval: (query) =>
      isTerminal(query.state.data?.status) ? false : 3000,
  });

  const { data: agents } = useQuery({
    queryKey: ["agents", runId],
    queryFn: () => fetchAgentOutputs(runId),
    enabled: !!run && run.status !== "pending",
    refetchInterval: (query) =>
      isTerminal(run?.status) ? false : 3000,
  });

  const { data: signal } = useQuery({
    queryKey: ["signal", runId],
    queryFn: () => fetchFinalSignal(runId),
    enabled: !!run && isTerminal(run.status),
    retry: 1,
  });

  if (runLoading) {
    return (
      <div className="flex items-center gap-2 text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" />
        Loading run...
      </div>
    );
  }

  if (!run) {
    return <p className="text-muted-foreground">Run not found.</p>;
  }

  const duration =
    run.started_at && run.finished_at
      ? (
          (new Date(run.finished_at).getTime() -
            new Date(run.started_at).getTime()) /
          1000
        ).toFixed(1) + "s"
      : run.status === "running"
      ? "in progress..."
      : "-";

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href="/runs"
          className="text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-3">
            <span className="font-mono">{run.asset_id}</span>
            {statusBadge(run.status)}
            {run.status === "running" && (
              <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
            )}
          </h2>
          <p className="text-sm text-muted-foreground">
            {run.analysis_mode} &middot; {run.time_horizon} &middot; Duration:{" "}
            {duration}
          </p>
        </div>
      </div>

      {run.error_message && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-4">
            <p className="text-sm text-red-800">{run.error_message}</p>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="agents">
        <TabsList>
          <TabsTrigger value="agents">
            Agent Outputs ({agents?.length || 0})
          </TabsTrigger>
          <TabsTrigger value="signal">Final Signal</TabsTrigger>
        </TabsList>

        <TabsContent value="agents" className="space-y-4 mt-4">
          {agents && agents.length > 0 ? (
            agents.map((agent) => (
              <Card key={agent.id}>
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between">
                    <span className="capitalize">
                      {agent.agent_name.replace(/_/g, " ")}
                    </span>
                    <div className="flex items-center gap-2">
                      {agent.stance && stanceBadge(agent.stance)}
                      <Badge
                        variant={agent.is_valid ? "default" : "destructive"}
                      >
                        {agent.is_valid ? "valid" : "invalid"}
                      </Badge>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-4 text-sm mb-3">
                    <div>
                      <span className="text-muted-foreground">Score:</span>{" "}
                      <span className="font-mono font-bold">
                        {agent.score !== null ? agent.score.toFixed(3) : "-"}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Confidence:</span>{" "}
                      <span className="font-mono font-bold">
                        {agent.confidence !== null
                          ? (agent.confidence * 100).toFixed(0) + "%"
                          : "-"}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Model:</span>{" "}
                      <span className="text-xs">
                        {agent.model_version || "-"}
                      </span>
                    </div>
                  </div>
                  {typeof agent.output_json.reasoning === "string" && (
                    <details className="text-sm">
                      <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                        Reasoning
                      </summary>
                      <p className="mt-2 whitespace-pre-wrap text-muted-foreground bg-muted p-3 rounded-md">
                        {agent.output_json.reasoning}
                      </p>
                    </details>
                  )}
                  {agent.validation_errors &&
                    Object.keys(agent.validation_errors).length > 0 && (
                      <div className="mt-2 text-xs text-red-600">
                        Validation errors:{" "}
                        {JSON.stringify(agent.validation_errors)}
                      </div>
                    )}
                </CardContent>
              </Card>
            ))
          ) : run.status === "pending" || run.status === "running" ? (
            <div className="flex items-center gap-2 text-muted-foreground py-8">
              <Loader2 className="h-4 w-4 animate-spin" />
              Agents are processing...
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">
              No agent outputs available.
            </p>
          )}
        </TabsContent>

        <TabsContent value="signal" className="mt-4">
          {signal ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Aggregated Signal</span>
                  <div className="flex items-center gap-2">
                    {stanceBadge(signal.final_stance)}
                    <Badge
                      variant={
                        signal.release_status === "approved"
                          ? "default"
                          : signal.release_status === "blocked"
                          ? "destructive"
                          : "secondary"
                      }
                    >
                      {signal.release_status}
                    </Badge>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground block">Score</span>
                    <span className="text-2xl font-mono font-bold">
                      {signal.final_score.toFixed(3)}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block">
                      Confidence
                    </span>
                    <span className="text-2xl font-mono font-bold">
                      {(signal.final_confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block">
                      Risk Override
                    </span>
                    <span className="text-2xl font-mono font-bold">
                      {signal.risk_override ? "Yes" : "No"}
                    </span>
                  </div>
                </div>

                {signal.summary && (
                  <div>
                    <span className="text-sm text-muted-foreground block mb-1">
                      Summary
                    </span>
                    <p className="text-sm whitespace-pre-wrap bg-muted p-3 rounded-md">
                      {signal.summary}
                    </p>
                  </div>
                )}

                {signal.contributing_agents &&
                  signal.contributing_agents.length > 0 && (
                    <div>
                      <span className="text-sm text-muted-foreground block mb-1">
                        Contributing Agents
                      </span>
                      <div className="flex gap-2 flex-wrap">
                        {signal.contributing_agents.map((name) => (
                          <Badge key={name} variant="secondary">
                            {name.replace(/_/g, " ")}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                {signal.blocked_reasons &&
                  signal.blocked_reasons.length > 0 && (
                    <div>
                      <span className="text-sm text-red-600 block mb-1">
                        Blocked Reasons
                      </span>
                      <ul className="list-disc list-inside text-sm text-red-600">
                        {signal.blocked_reasons.map((reason, i) => (
                          <li key={i}>{reason}</li>
                        ))}
                      </ul>
                    </div>
                  )}
              </CardContent>
            </Card>
          ) : isTerminal(run.status) ? (
            <p className="text-muted-foreground text-sm">
              No final signal available for this run.
            </p>
          ) : (
            <div className="flex items-center gap-2 text-muted-foreground py-8">
              <Loader2 className="h-4 w-4 animate-spin" />
              Waiting for analysis to complete...
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
