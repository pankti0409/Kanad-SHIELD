/**
 * TraceVault Threat Intelligence & Analytics Dashboard
 */
import React from "react";
import { BarChart3, TrendingUp, ShieldAlert, Brain, Activity, Mic, Users, DollarSign } from "lucide-react";

export function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div className="tv-page-header">
        <div>
          <h1 className="tv-page-title">Threat Intelligence & Analytics</h1>
          <p className="tv-page-subtitle">
            Cross-case risk trends, voice biometrics analytics, and AI model performance metrics.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="tv-card p-5 space-y-2">
          <span className="text-xs text-muted-foreground font-medium">Threat Level Distribution</span>
          <div className="flex items-baseline gap-2">
            <h3 className="text-2xl font-bold text-foreground">18 Critical</h3>
            <span className="text-xs text-red-500 font-medium">+14% this month</span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden flex gap-0.5 mt-2">
            <div className="h-full bg-red-500 w-[45%]" />
            <div className="h-full bg-amber-500 w-[35%]" />
            <div className="h-full bg-emerald-500 w-[20%]" />
          </div>
        </div>

        <div className="tv-card p-5 space-y-2">
          <span className="text-xs text-muted-foreground font-medium">Pipeline Throughput</span>
          <div className="flex items-baseline gap-2">
            <h3 className="text-2xl font-bold text-foreground">4.2 hrs / min</h3>
            <span className="text-xs text-emerald-500 font-medium">GPU Accelerated</span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden mt-2">
            <div className="h-full bg-gradient-to-r from-primary to-accent w-[82%]" />
          </div>
        </div>

        <div className="tv-card p-5 space-y-2">
          <span className="text-xs text-muted-foreground font-medium">Entity Extraction Precision</span>
          <div className="flex items-baseline gap-2">
            <h3 className="text-2xl font-bold text-foreground">98.2%</h3>
            <span className="text-xs text-emerald-500 font-medium">GLiNER Large</span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden mt-2">
            <div className="h-full bg-emerald-500 w-[98%]" />
          </div>
        </div>
      </div>

      <div className="tv-card p-6 space-y-4">
        <h3 className="text-sm font-bold text-foreground">Cross-Case Extortion & Scam Correlations</h3>
        <p className="text-xs text-muted-foreground">
          Voice biometrics match 4 distinct speaker profiles across 12 recordings, indicating a coordinated foreign call center structure.
        </p>
      </div>
    </div>
  );
}
