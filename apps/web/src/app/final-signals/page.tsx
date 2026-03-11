"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchSignals } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function stanceBadge(stance: string) {
  const colors: Record<string, string> = {
    bullish: "bg-green-100 text-green-800",
    bearish: "bg-red-100 text-red-800",
    neutral: "bg-gray-100 text-gray-800",
  };
  return <Badge className={colors[stance] || ""}>{stance}</Badge>;
}

export default function FinalSignalsPage() {
  const { data: signals, isLoading } = useQuery({
    queryKey: ["signals"],
    queryFn: fetchSignals,
    refetchInterval: 10000,
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Final Signals</h2>

      {isLoading ? (
        <p className="text-muted-foreground">Loading...</p>
      ) : signals && signals.length > 0 ? (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Stance</TableHead>
              <TableHead>Score</TableHead>
              <TableHead>Confidence</TableHead>
              <TableHead>Risk Override</TableHead>
              <TableHead>Release Status</TableHead>
              <TableHead>Agents</TableHead>
              <TableHead>Created</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {signals.map((signal) => (
              <TableRow key={signal.id}>
                <TableCell>{stanceBadge(signal.final_stance)}</TableCell>
                <TableCell className="font-mono">
                  {signal.final_score.toFixed(3)}
                </TableCell>
                <TableCell className="font-mono">
                  {(signal.final_confidence * 100).toFixed(0)}%
                </TableCell>
                <TableCell>
                  {signal.risk_override ? (
                    <Badge variant="destructive">Yes</Badge>
                  ) : (
                    <span className="text-muted-foreground">No</span>
                  )}
                </TableCell>
                <TableCell>
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
                </TableCell>
                <TableCell className="text-xs text-muted-foreground">
                  {signal.contributing_agents?.join(", ") || "-"}
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {new Date(signal.created_at).toLocaleString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <p className="text-muted-foreground text-sm">
          No signals yet. Complete a research run to generate signals.
        </p>
      )}
    </div>
  );
}
