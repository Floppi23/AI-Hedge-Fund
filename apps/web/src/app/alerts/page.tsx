"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Bell } from "lucide-react";

export default function AlertsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Alerts</h2>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Alert Configuration
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">
            Alert configuration is coming in a future update. You will be able
            to set up notifications for:
          </p>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground list-disc list-inside">
            <li>New signals with specific stance or confidence thresholds</li>
            <li>Blocked signals requiring manual review</li>
            <li>Failed research runs</li>
            <li>Risk override activations</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
