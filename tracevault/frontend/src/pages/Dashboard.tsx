/**
 * TraceVault Executive Investigation Dashboard
 * Integrates Call Flow Metrics, Live Recordings Panel, and System Stats.
 */
import React from "react";
import { motion } from "framer-motion";
import {
  FolderOpen,
  Mic,
  ShieldAlert,
  Brain,
  ArrowUpRight,
  CheckCircle2,
  Clock,
  FileText,
  AlertTriangle,
} from "lucide-react";
import { Link } from "react-router-dom";
import { CallMetricsHeader } from "@/components/shared/CallMetricsHeader";
import { useRecordingsStore } from "@/stores/recordingsStore";
import { cn } from "@/lib/utils";

export function Dashboard() {
  const { recordings, analyses, setActiveRecordingId } = useRecordingsStore();

  // Derive stats from store
  const totalRecordings = recordings.length;
  const totalThreats = Object.values(analyses).filter((a) => a?.threatPresent).length;
  const completedRecs = recordings.filter((r) => r.status === "completed").length;

  // Show most recent 3 recordings as "Priority Intercepts"
  const recentRecordings = recordings.slice(0, 3);

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

      {/* Quick Stats Row */}
      {totalRecordings > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            {
              label: "Total Recordings",
              value: totalRecordings,
              icon: Mic,
              color: "text-primary",
              bg: "bg-primary/10 border-primary/20",
            },
            {
              label: "Completed",
              value: completedRecs,
              icon: CheckCircle2,
              color: "text-emerald-400",
              bg: "bg-emerald-500/10 border-emerald-500/20",
            },
            {
              label: "Threats Detected",
              value: totalThreats,
              icon: ShieldAlert,
              color: "text-red-400",
              bg: "bg-red-500/10 border-red-500/20",
            },
            {
              label: "Reports Generated",
              value: completedRecs,
              icon: FileText,
              color: "text-amber-400",
              bg: "bg-amber-500/10 border-amber-500/20",
            },
          ].map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className={`tv-card p-4 border ${stat.bg}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <Icon className={`w-4 h-4 ${stat.color}`} />
                </div>
                <h3 className={`text-2xl font-bold font-mono ${stat.color}`}>{stat.value}</h3>
                <p className="text-xs font-medium text-muted-foreground mt-0.5">{stat.label}</p>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Call Flow & Metrics Header Row */}
      <CallMetricsHeader />



      {/* Main Grid: Recent Recordings / Priority Intercepts */}
      <div className="tv-card p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-foreground">
              {recentRecordings.length > 0 ? "Recent Processed Intercepts" : "Priority Case Intercepts"}
            </h3>
            <p className="text-xs text-muted-foreground">
              {recentRecordings.length > 0
                ? "Most recently processed recordings from the AI pipeline"
                : "Cases requiring active intelligence review"}
            </p>
          </div>
          <Link
            to="/recordings"
            className="text-xs text-primary font-semibold hover:underline flex items-center gap-1"
          >
            View All <ArrowUpRight className="w-3 h-3" />
          </Link>
        </div>

        {recentRecordings.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {recentRecordings.map((rec) => {
              const analysis = analyses[rec.id];
              const hasThreat = analysis?.threatPresent ?? false;
              return (
                <Link
                  key={rec.id}
                  to="/transcripts"
                  onClick={() => setActiveRecordingId(rec.id)}
                  className={cn(
                    "p-4 rounded-xl border bg-card/40 hover:bg-muted/40 transition-all cursor-pointer space-y-3 flex flex-col justify-between",
                    hasThreat ? "border-red-500/30" : "border-border"
                  )}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold text-primary truncate max-w-[120px]">
                        {rec.warrantNumber}
                      </span>
                      <span
                        className={cn(
                          "tv-badge",
                          hasThreat ? "tv-badge-critical" : "tv-badge-medium"
                        )}
                      >
                        {hasThreat ? "THREAT" : "CLEAR"}
                      </span>
                    </div>
                    <h4 className="text-sm font-semibold text-foreground line-clamp-1">{rec.filename}</h4>
                    <p className="text-[11px] text-muted-foreground">{rec.uploadedAt}</p>
                  </div>

                  <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t border-border">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      {rec.duration}
                    </span>
                    {hasThreat ? (
                      <span className="text-red-500 font-medium flex items-center gap-1">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        {analysis?.threatCategory}
                      </span>
                    ) : (
                      <span className="text-emerald-500 font-medium flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Clear
                      </span>
                    )}
                  </div>
                </Link>
              );
            })}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {[
              {
                id: "case-1", case_number: "TV-8839-FRD",
                title: "Operation Iron Vault - Financial Scam Ring",
                priority: "critical", recordings: 14, threats: 6,
              },
              {
                id: "case-2", case_number: "TV-4012-EXT",
                title: "Extortion Investigation - Call Center Cyber Ring",
                priority: "high", recordings: 8, threats: 4,
              },
              {
                id: "case-3", case_number: "TV-1092-ORG",
                title: "Project Blackout - Intercept Analysis",
                priority: "medium", recordings: 22, threats: 2,
              },
            ].map((c) => (
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
        )}
      </div>
    </div>
  );
}
