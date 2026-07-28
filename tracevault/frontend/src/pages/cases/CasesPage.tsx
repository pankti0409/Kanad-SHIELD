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
  XCircle,
} from "lucide-react";
import { Link } from "react-router-dom";
import { Case, CasePriority, CaseStatus } from "@/types";
import { cn } from "@/lib/utils";
import { api } from "@/api/client";

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

  const [cases, setCases] = useState<ExtendedCase[]>([]);
  const [loading, setLoading] = useState(true);

  // New Case Form State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newCaseTitle, setNewCaseTitle] = useState("");
  const [newCaseDescription, setNewCaseDescription] = useState("");
  const [newCasePriority, setNewCasePriority] = useState("medium");
  const [newCaseCategory, setNewCaseCategory] = useState("general");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const res = await api.get<any>("/cases");
      if (res && res.items && res.items.length > 0) {
        setCases(res.items);
      } else {
        setCases(MOCK_CASES);
      }
    } catch (err) {
      console.error("Failed to fetch cases", err);
      setCases(MOCK_CASES);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchCases();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCaseTitle.trim()) return;
    setIsSubmitting(true);
    try {
      await api.post("/cases", {
        title: newCaseTitle,
        description: newCaseDescription,
        priority: newCasePriority,
        category: newCaseCategory,
      });
      setNewCaseTitle("");
      setNewCaseDescription("");
      setNewCasePriority("medium");
      setNewCaseCategory("general");
      setIsModalOpen(false);
      await fetchCases();
    } catch (err) {
      console.error("Failed to create case", err);
      alert("Error: Failed to create case. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredCases = cases.filter((c) => {
    // Search using search numbers (case_number) only
    const matchesSearch = c.case_number.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === "all" || c.status === selectedStatus;
    const matchesPriority = selectedPriority === "all" || c.priority === selectedPriority;
    return matchesSearch && matchesStatus && matchesPriority;
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
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg text-xs font-semibold shadow-glow-primary transition-all flex items-center gap-2"
        >
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

      {/* New Case Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-card border border-border rounded-xl shadow-2xl w-full max-w-md overflow-hidden"
          >
            <div className="px-5 py-4 border-b border-border flex items-center justify-between bg-muted/20">
              <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                <FolderOpen className="w-4 h-4 text-primary" />
                Create New Case
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-all"
              >
                <XCircle className="w-4 h-4" />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-5 space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">Case Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Operation Golden Ring"
                  value={newCaseTitle}
                  onChange={(e) => setNewCaseTitle(e.target.value)}
                  className="w-full bg-muted/40 border border-border rounded-lg px-3 py-2 text-xs text-foreground placeholder:text-muted-foreground outline-none focus:ring-1 focus:ring-primary"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">Description</label>
                <textarea
                  placeholder="Provide description of the investigation..."
                  value={newCaseDescription}
                  onChange={(e) => setNewCaseDescription(e.target.value)}
                  rows={3}
                  className="w-full bg-muted/40 border border-border rounded-lg px-3 py-2 text-xs text-foreground placeholder:text-muted-foreground outline-none focus:ring-1 focus:ring-primary resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">Priority</label>
                  <select
                    value={newCasePriority}
                    onChange={(e) => setNewCasePriority(e.target.value)}
                    className="w-full bg-muted/40 border border-border rounded-lg px-3 py-2 text-xs text-foreground outline-none focus:ring-1 focus:ring-primary font-medium"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">Category</label>
                  <select
                    value={newCaseCategory}
                    onChange={(e) => setNewCaseCategory(e.target.value)}
                    className="w-full bg-muted/40 border border-border rounded-lg px-3 py-2 text-xs text-foreground outline-none focus:ring-1 focus:ring-primary font-medium"
                  >
                    <option value="general">General</option>
                    <option value="fraud">Fraud</option>
                    <option value="extortion">Extortion</option>
                    <option value="narcotics">Narcotics</option>
                    <option value="cyber">Cyber</option>
                  </select>
                </div>
              </div>

              <div className="pt-2 border-t border-border flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-3 py-1.5 rounded-lg border border-border hover:bg-muted text-xs font-semibold transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !newCaseTitle.trim()}
                  className="px-3 py-1.5 bg-primary text-white hover:bg-primary/90 disabled:opacity-50 rounded-lg text-xs font-semibold shadow-glow-primary transition-all flex items-center gap-1.5"
                >
                  {isSubmitting ? "Creating..." : "Create Case"}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
}
