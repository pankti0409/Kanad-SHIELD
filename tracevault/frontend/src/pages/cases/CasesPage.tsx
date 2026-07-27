/**
 * TraceVault Case Management List View
 * Searchable, filterable investigation case list with status badges, priority markers, and quick actions.
 */
import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  FolderOpen,
  Plus,
  Search,
  Filter,
  ShieldAlert,
  Mic,
  FileText,
  Calendar,
  User,
  MoreVertical,
  ArrowUpDown,
} from "lucide-react";
import { Link } from "react-router-dom";
import { Case, CasePriority, CaseStatus } from "@/types";
import { cn } from "@/lib/utils";

interface ExtendedCase extends Case {
  minister?: string;
}

const MOCK_CASES: ExtendedCase[] = [
  {
    id: "case-101",
    case_number: "TV-2026-0091",
    title: "Operation Iron Vault - Financial Scam Ring",
    description: "Multi-jurisdictional investigation into organized call center fraud targeting high-net-worth individuals.",
    status: "under_investigation",
    priority: "critical",
    category: "fraud",
    recording_count: 18,
    evidence_count: 42,
    report_count: 3,
    created_by: "usr-01",
    created_at: "2026-07-18T10:00:00Z",
    updated_at: "2026-07-21T08:00:00Z",
    minister: "amit_shah",
  },
  {
    id: "case-102",
    case_number: "TV-2026-0084",
    title: "Extortion Investigation - Call Center Cyber Ring",
    description: "Threat intelligence and intercept analysis of extortion calls originating from foreign VoIP ranges.",
    status: "open",
    priority: "high",
    category: "extortion",
    recording_count: 9,
    evidence_count: 15,
    report_count: 1,
    created_by: "usr-02",
    created_at: "2026-07-15T14:30:00Z",
    updated_at: "2026-07-20T16:20:00Z",
    minister: "nirmala_sitharaman",
  },
  {
    id: "case-103",
    case_number: "TV-2026-0072",
    title: "Project Blackout - Intercept Analysis",
    description: "Wiretap intercept processing and speaker identification for narcotics trafficking ring.",
    status: "pending_review",
    priority: "medium",
    category: "drug_trafficking",
    recording_count: 31,
    evidence_count: 68,
    report_count: 5,
    created_by: "usr-01",
    created_at: "2026-07-02T09:15:00Z",
    updated_at: "2026-07-19T11:45:00Z",
    minister: "rajnath_singh",
  },
];

export function CasesPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");
  const [selectedPriority, setSelectedPriority] = useState<string>("all");
  const [selectedMinister, setSelectedMinister] = useState<string>("all");

  const filteredCases = MOCK_CASES.filter((c) => {
    // Search using search numbers (case_number) only
    const matchesSearch = c.case_number.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === "all" || c.status === selectedStatus;
    const matchesPriority = selectedPriority === "all" || c.priority === selectedPriority;
    const matchesMinister = selectedMinister === "all" || c.minister === selectedMinister;
    return matchesSearch && matchesStatus && matchesPriority && matchesMinister;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="tv-page-header">
        <div>
          <h1 className="tv-page-title">Investigation Cases</h1>
          <p className="tv-page-subtitle">
            Manage investigation cases, digital chain of custody, and team assignments.
          </p>
        </div>
        <button className="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg text-xs font-semibold shadow-glow-primary transition-all flex items-center gap-2">
          <Plus className="w-4 h-4" />
          <span>New Case</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="tv-card p-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2 w-full sm:w-80 bg-muted/50 border border-border rounded-lg px-3 py-1.5 focus-within:ring-1 focus-within:ring-ring">
          <Search className="w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search cases by number only..."
            className="w-full bg-transparent text-xs text-foreground placeholder:text-muted-foreground outline-none"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          {/* Minister Filter */}
          <select
            value={selectedMinister}
            onChange={(e) => setSelectedMinister(e.target.value)}
            className="bg-card border border-border text-xs text-foreground rounded-lg px-3 py-1.5 outline-none"
          >
            <option value="all">All Ministers</option>
            <option value="amit_shah">Hon. Amit Shah (Home Affairs)</option>
            <option value="rajnath_singh">Hon. Rajnath Singh (Defence)</option>
            <option value="nirmala_sitharaman">Hon. Nirmala Sitharaman (Finance)</option>
          </select>

          {/* Status Filter */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="bg-card border border-border text-xs text-foreground rounded-lg px-3 py-1.5 outline-none"
          >
            <option value="all">All Statuses</option>
            <option value="open">Open</option>
            <option value="under_investigation">Under Investigation</option>
            <option value="pending_review">Pending Review</option>
            <option value="completed">Completed</option>
          </select>

          {/* Priority Filter */}
          <select
            value={selectedPriority}
            onChange={(e) => setSelectedPriority(e.target.value)}
            className="bg-card border border-border text-xs text-foreground rounded-lg px-3 py-1.5 outline-none"
          >
            <option value="all">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Case Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredCases.map((c) => (
          <Link key={c.id} to={`/cases/${c.id}`}>
            <motion.div
              whileHover={{ y: -2 }}
              className="tv-card-hover p-5 space-y-4 flex flex-col justify-between h-full"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-primary">{c.case_number}</span>
                  <span
                    className={cn(
                      "tv-badge capitalize",
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
                <h3 className="text-base font-bold text-foreground line-clamp-1">{c.title}</h3>
                <p className="text-xs text-muted-foreground line-clamp-2">{c.description}</p>
              </div>

              <div className="pt-3 border-t border-border flex items-center justify-between text-xs text-muted-foreground">
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <Mic className="w-3.5 h-3.5" />
                    {c.recording_count}
                  </span>
                  <span className="flex items-center gap-1">
                    <FileText className="w-3.5 h-3.5" />
                    {c.evidence_count}
                  </span>
                </div>
                <span className="text-[11px] capitalize font-medium text-foreground">
                  {c.status.replace(/_/g, " ")}
                </span>
              </div>
            </motion.div>
          </Link>
        ))}
      </div>
    </div>
  );
}
