/**
 * TraceVault Executive Investigation Dashboard
 * Integrates Call Flow Metrics, Evaluation Orbits Navigation, Live Audio Intercept Simulator,
 * and Forensic Audio Player.
 */
import React from "react";
import { motion } from "framer-motion";
import {
  FolderOpen,
  Mic,
  ShieldAlert,
  Brain,
  TrendingUp,
  Activity,
  ArrowUpRight,
  CheckCircle2,
} from "lucide-react";
import { Link } from "react-router-dom";
import { CallMetricsHeader } from "@/components/shared/CallMetricsHeader";
import { EvaluationOrbits } from "@/components/shared/EvaluationOrbits";
import { LiveInterceptSimulator } from "@/components/shared/LiveInterceptSimulator";
import { AudioForensicsPlayer } from "@/components/shared/AudioForensicsPlayer";
import { cn } from "@/lib/utils";

const RECENT_CASES = [
  {
    id: "case-1",
    case_number: "TV-8839-FRD",
    title: "Operation Iron Vault - Financial Scam Ring",
    category: "Financial Crime",
    priority: "critical",
    recordings: 14,
    threats: 6,
    updated: "12 mins ago",
  },
  {
    id: "case-2",
    case_number: "TV-4012-EXT",
    title: "Extortion Investigation - Call Center Cyber Ring",
    category: "Extortion",
    priority: "high",
    recordings: 8,
    threats: 4,
    updated: "45 mins ago",
  },
  {
    id: "case-3",
    case_number: "TV-1092-ORG",
    title: "Project Blackout - Intercept Analysis",
    category: "Organized Crime",
    priority: "medium",
    recordings: 22,
    threats: 2,
    updated: "2 hours ago",
  },
];

export function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="tv-page-header">
        <div>
          <h1 className="tv-page-title">Operational Intelligence Dashboard</h1>
          <p className="tv-page-subtitle">
            Multilingual call intelligence analytics, evaluation orbits navigation, and evidence processing.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/cases"
            className="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg text-xs font-semibold shadow-glow-primary transition-all flex items-center gap-2"
          >
            <FolderOpen className="w-4 h-4" />
            <span>New Case</span>
          </Link>
          <Link
            to="/recordings"
            className="px-4 py-2 bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded-lg text-xs font-semibold border border-border transition-all flex items-center gap-2"
          >
            <Mic className="w-4 h-4" />
            <span>Upload Audio</span>
          </Link>
        </div>
      </div>

      {/* Call Flow & Metrics Header Row */}
      <CallMetricsHeader />

      {/* Evaluation Orbits Interactive Tier Navigation */}
      <EvaluationOrbits />

      {/* Creative Interactive Widgets: Live Intercept Stream & Forensic Audio Player */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LiveInterceptSimulator />
        <AudioForensicsPlayer />
      </div>

      {/* Main Grid: Priority Cases */}
      <div className="tv-card p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-foreground">Priority Case Intercepts</h3>
            <p className="text-xs text-muted-foreground">Cases requiring active intelligence review</p>
          </div>
          <Link
            to="/cases"
            className="text-xs text-primary font-semibold hover:underline flex items-center gap-1"
          >
            View All Cases <ArrowUpRight className="w-3 h-3" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {RECENT_CASES.map((c) => (
            <div
              key={c.id}
              className="p-4 rounded-xl border border-border bg-card/40 hover:bg-muted/40 transition-all cursor-pointer space-y-3 flex flex-col justify-between"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-primary">{c.case_number}</span>
                  <span
                    className={cn(
                      "tv-badge",
                      c.priority === "critical"
                        ? "tv-badge-critical"
                        : c.priority === "high"
                        ? "tv-badge-high"
                        : "tv-badge-medium"
                    )}
                  >
                    {c.priority}
                  </span>
                </div>
                <h4 className="text-sm font-semibold text-foreground line-clamp-1">{c.title}</h4>
              </div>

              <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t border-border">
                <span className="flex items-center gap-1">
                  <Mic className="w-3.5 h-3.5" />
                  {c.recordings} calls
                </span>
                <span className="text-red-500 font-medium flex items-center gap-1">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  {c.threats} threats
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
