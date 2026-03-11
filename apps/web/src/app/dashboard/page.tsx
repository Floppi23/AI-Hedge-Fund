"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchRuns, fetchSignals } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

function stanceBadge(stance: string) {
  const colors: Record<string, string> = {
    bullish: "bg-green-100 text-green-800",
    bearish: "bg-red-100 text-red-800",
    neutral: "bg-gray-100 text-gray-800",
  };
  return <Badge className={colors[stance] || ""}>{stance}</Badge>;
}

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

export default function DashboardPage() {
  const { data: runs } = useQuery({ queryKey: ["runs"], queryFn: fetchRuns });
  const { data: signals } = useQuery({
    queryKey: ["signals"],
    queryFn: fetchSignals,
  });

  const totalRuns = runs?.length || 0;
  const completedRuns = runs?.filter((r) => r.status === "completed").length || 0;
  const approvedSignals = signals?.filter((s) => s.release_status === "approved").length || 0;
  const blockedSignals = signals?.filter((s) => s.release_status === "blocked").length || 0;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dashboard</h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Total Runs</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{totalRuns}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-green-600">{completedRuns}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Approved Signals</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-600">{approvedSignals}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Blocked</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-orange-600">{blockedSignals}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Runs</CardTitle>
          </CardHeader>
          <CardContent>
            {runs && runs.length > 0 ? (
              <div className="space-y-2">
                {runs.slice(0, 5).map((run) => (
                  <Link
                    key={run.id}
                    href={`/runs/${run.id}`}
                    className="flex items-center justify-between p-2 rounded hover:bg-muted transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="font-mono font-bold">{run.asset_id}</span>
                      {statusBadge(run.status)}
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(run.created_at).toLocaleString()}
                    </span>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground text-sm">No runs yet. Start one from the Runs page.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Latest Signals</CardTitle>
          </CardHeader>
          <CardContent>
            {signals && signals.length > 0 ? (
              <div className="space-y-2">
                {signals.slice(0, 5).map((signal) => (
                  <div
                    key={signal.id}
                    className="flex items-center justify-between p-2 rounded"
                  >
                    <div className="flex items-center gap-3">
                      {stanceBadge(signal.final_stance)}
                      <span className="text-sm">
                        Score: {signal.final_score.toFixed(3)}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        Conf: {(signal.final_confidence * 100).toFixed(0)}%
                      </span>
                    </div>
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
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground text-sm">No signals yet.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
