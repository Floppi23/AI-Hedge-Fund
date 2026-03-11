"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchRuns } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import Link from "next/link";
import { NewRunForm } from "@/components/runs/new-run-form";

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

export default function RunsPage() {
  const { data: runs, isLoading } = useQuery({
    queryKey: ["runs"],
    queryFn: fetchRuns,
    refetchInterval: 5000,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Research Runs</h2>
        <NewRunForm />
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">Loading...</p>
      ) : runs && runs.length > 0 ? (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Asset</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Mode</TableHead>
              <TableHead>Horizon</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Duration</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {runs.map((run) => (
              <TableRow key={run.id}>
                <TableCell>
                  <Link
                    href={`/runs/${run.id}`}
                    className="font-mono font-bold hover:underline"
                  >
                    {run.asset_id}
                  </Link>
                </TableCell>
                <TableCell>{statusBadge(run.status)}</TableCell>
                <TableCell className="text-sm">{run.analysis_mode}</TableCell>
                <TableCell className="text-sm">{run.time_horizon}</TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {new Date(run.created_at).toLocaleString()}
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {run.started_at && run.finished_at
                    ? `${((new Date(run.finished_at).getTime() - new Date(run.started_at).getTime()) / 1000).toFixed(1)}s`
                    : run.status === "running"
                    ? "..."
                    : "-"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <p className="text-muted-foreground">No runs yet. Click &quot;New Run&quot; to start.</p>
      )}
    </div>
  );
}
