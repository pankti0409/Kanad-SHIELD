/**
 * TraceVault Immutable Security Audit Log View
 * Forensics-grade immutable activity log tracking every authentication event, evidence download, and AI inference query.
 */
import React, { useState } from "react";
import { Shield, Search, Lock, Filter, CheckCircle2, AlertTriangle, FileText, User } from "lucide-react";
import { AuditLog } from "@/types";

const MOCK_AUDITS: AuditLog[] = [
  {
    id: "aud-01",
    user_id: "usr-01",
    username: "investigator_vance",
    user_role: "senior_investigator",
    action: "evidence.download",
    action_category: "evidence",
    description: "Exported SHA-256 verified evidence file #EF-8812.",
    severity: "info",
    resource_type: "evidence",
    resource_id: "ef-8812",
    resource_name: "INTERCEPT_CALL_042.wav",
    result: "success",
    ip_address: "192.168.10.44",
    created_at: "2026-07-21T08:14:22Z",
  },
  {
    id: "aud-02",
    user_id: "usr-02",
    username: "analyst_sarah",
    user_role: "analyst",
    action: "ai.copilot_query",
    action_category: "ai",
    description: "Queried Copilot regarding suspect Zurich accounts.",
    severity: "info",
    result: "success",
    ip_address: "192.168.10.12",
    created_at: "2026-07-21T07:45:10Z",
  },
  {
    id: "aud-03",
    user_id: "usr-03",
    username: "unknown_attempt",
    user_role: "unauthenticated",
    action: "auth.login_failed",
    action_category: "security",
    description: "Failed password verification attempt (Attempt 1/5).",
    severity: "warning",
    result: "failure",
    ip_address: "203.0.113.88",
    created_at: "2026-07-21T06:12:00Z",
  },
];

export function AuditLogPage() {
  const [logs] = useState<AuditLog[]>(MOCK_AUDITS);
  const [searchTerm, setSearchTerm] = useState("");

  return (
    <div className="space-y-6">
      <div className="tv-page-header">
        <div>
          <h1 className="tv-page-title">Security & Forensic Audit Log</h1>
          <p className="tv-page-subtitle">
            Cryptographically verifiable activity trail documenting all access, exports, and AI queries.
          </p>
        </div>
      </div>

      <div className="tv-card overflow-hidden">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2 bg-muted/50 border border-border rounded-lg px-3 py-1.5 w-80">
            <Search className="w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter audit entries by action or user..."
              className="w-full bg-transparent text-xs text-foreground placeholder:text-muted-foreground outline-none"
            />
          </div>
          <span className="text-xs text-emerald-500 font-medium flex items-center gap-1">
            <Shield className="w-3.5 h-3.5" /> Append-Only Immutable Storage Active
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border bg-muted/30 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
                <th className="p-3.5">Timestamp</th>
                <th className="p-3.5">User</th>
                <th className="p-3.5">Action</th>
                <th className="p-3.5">Description</th>
                <th className="p-3.5">IP Address</th>
                <th className="p-3.5">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border text-xs">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-muted/20 transition-colors">
                  <td className="p-3.5 font-mono text-muted-foreground">{log.created_at}</td>
                  <td className="p-3.5 font-semibold text-foreground">{log.username}</td>
                  <td className="p-3.5">
                    <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-muted">
                      {log.action}
                    </span>
                  </td>
                  <td className="p-3.5 text-muted-foreground max-w-xs truncate">{log.description}</td>
                  <td className="p-3.5 font-mono text-muted-foreground">{log.ip_address}</td>
                  <td className="p-3.5">
                    <span
                      className={`tv-badge ${
                        log.result === "success" ? "tv-badge-completed" : "tv-badge-critical"
                      }`}
                    >
                      {log.result}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
