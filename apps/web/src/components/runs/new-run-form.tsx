"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { createRun } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import { Plus } from "lucide-react";

export function NewRunForm() {
  const [open, setOpen] = useState(false);
  const [ticker, setTicker] = useState("");
  const [analysisMode, setAnalysisMode] = useState("full");
  const [timeHorizon, setTimeHorizon] = useState("medium_term");
  const router = useRouter();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createRun,
    onSuccess: (run) => {
      queryClient.invalidateQueries({ queryKey: ["runs"] });
      setOpen(false);
      setTicker("");
      router.push(`/runs/${run.id}`);
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const assetId = ticker.trim().toUpperCase();
    if (!assetId || !/^[A-Z]{1,10}$/.test(assetId)) return;
    mutation.mutate({
      asset_id: assetId,
      analysis_mode: analysisMode,
      time_horizon: timeHorizon,
    });
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button />}>
        <Plus className="h-4 w-4 mr-2" />
        New Run
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Start Research Run</DialogTitle>
          <DialogDescription>
            Enter a ticker symbol to analyze with the AI agent ensemble.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="ticker">
              Ticker Symbol
            </label>
            <Input
              id="ticker"
              placeholder="e.g. AAPL"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              maxLength={10}
              required
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="mode">
              Analysis Mode
            </label>
            <select
              id="mode"
              value={analysisMode}
              onChange={(e) => setAnalysisMode(e.target.value)}
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="full">Full Analysis</option>
              <option value="quick">Quick Scan</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="horizon">
              Time Horizon
            </label>
            <select
              id="horizon"
              value={timeHorizon}
              onChange={(e) => setTimeHorizon(e.target.value)}
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="short_term">Short Term (1-4 weeks)</option>
              <option value="medium_term">Medium Term (1-6 months)</option>
              <option value="long_term">Long Term (6-24 months)</option>
            </select>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Starting..." : "Start Analysis"}
            </Button>
          </DialogFooter>
          {mutation.isError && (
            <p className="text-sm text-red-600">
              Failed to start run. Is the API server running?
            </p>
          )}
        </form>
      </DialogContent>
    </Dialog>
  );
}
