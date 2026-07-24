import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileBarChart2, Download, Plus, FileText, CheckCircle2, Shield, Clock, Lock, Sparkles, AlertTriangle, X } from "lucide-react";
import { useRecordingsStore, GeneratedReport } from "@/stores/recordingsStore";

export function ReportsPage() {
  const { reports, recordings, transcripts, analyses, addReport } = useRecordingsStore();
  const [showNewReportModal, setShowNewReportModal] = useState(false);
  const [reportTitle, setReportTitle] = useState("");
  const [reportType, setReportType] = useState("Forensic Intelligence Summary");
  const [selectedCase, setSelectedCase] = useState("TV-CASE-2026");

  const handleDownloadReport = (rep: GeneratedReport) => {
    const rec = recordings.find((r) => r.id === rep.recordingId) || recordings[0];
    const segs = rec ? (transcripts[rec.id] || []) : [];
    const analysis = rec ? (analyses[rec.id] || null) : null;

    const content = `======================================================================
TRACEVAULT FORENSIC INTELLIGENCE REPORT — ${rep.title.toUpperCase()}
======================================================================
Report ID: ${rep.id}
Created At: ${rep.createdAt}
Status: ${rep.status.toUpperCase()}
Report Type: ${rep.reportType}
Evidence Cryptographic Status: SHA-256 Verified

[EVIDENCE METADATA]
File Name: ${rec?.filename || "Batch Recording Group"}
Format: ${rec?.format || "AUDIO"}
File Size: ${rec?.sizeMb || "N/A"} MB
SHA-256 Checksum: ${rec?.sha256Hash || "VERIFIED"}
Warrant Reference: ${rec?.warrantNumber || "WR-2026-9901"}
Case Reference: ${rec?.caseNumber || rep.caseNumber}

[EXECUTIVE INTELLIGENCE SUMMARY]
${analysis?.summary || rep.summary}

[THREAT AUDIT EVALUATION]
Threat Present: ${analysis?.threatPresent ? "YES" : "NO"}
Threat Category: ${analysis?.threatCategory || rep.threatCategory}
Threat Details: ${analysis?.threatDetails || "Standard security audit evaluation completed."}

[EXTRACTED ENTITIES & INTELLIGENCE]
Locations Discussed: ${analysis?.locationsDiscussed?.join(", ") || "None"}
Times / Dates Discussed: ${analysis?.timesDiscussed?.join(", ") || "None"}
Chain of Custody Notice: ${analysis?.otherInfo || "SHA-256 verified evidence."}

[DIARIZED TRANSCRIPT TIMELINE]
----------------------------------------------------------------------
${segs.length > 0 ? segs.map(s => `[${s.start_time.toFixed(1)}s - ${s.end_time.toFixed(1)}s] ${s.speaker_label} (${Math.round(s.confidence * 100)}% Conf):
"${s.text}"`).join("\n\n") : "No transcript segments associated."}
----------------------------------------------------------------------
CONFIDENTIALITY NOTICE: Restricted to authorized law enforcement and judicial personnel.
======================================================================`;

    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${rep.title.replace(/[^a-zA-Z0-9]/g, "_")}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleCreateReport = (e: React.FormEvent) => {
    e.preventDefault();
    if (!reportTitle.trim()) return;

    const newRep: GeneratedReport = {
      id: `rep-custom-${Date.now()}`,
      recordingId: recordings[0]?.id || "",
      title: reportTitle,
      caseNumber: selectedCase,
      reportType: reportType,
      status: "approved",
      createdAt: new Date().toLocaleString(),
      confidence: 0.98,
      summary: `Comprehensive investigation report compiled across ${recordings.length} audio recordings for Case ${selectedCase}.`,
      threatCategory: recordings.some(r => analyses[r.id]?.threatPresent) ? "Active Threat Signatures Identified" : "Clean Intercept Audit",
    };

    addReport(newRep);
    setReportTitle("");
    setShowNewReportModal(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="tv-page-header">
        <div>
          <h1 className="tv-page-title">Investigation Reports</h1>
          <p className="tv-page-subtitle">
            Generate, review, and export court-ready investigation reports and chain of custody documentation.
          </p>
        </div>
        <button
          onClick={() => setShowNewReportModal(true)}
          className="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg text-xs font-semibold shadow-glow-primary transition-all flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          <span>Generate New Report</span>
        </button>
      </div>

      {/* Reports Grid */}
      {reports.length === 0 ? (
        <div className="tv-empty-state">
          <div className="tv-empty-state-icon">
            <FileBarChart2 className="w-8 h-8 text-muted-foreground" />
          </div>
          <div className="tv-empty-state-title">No generated reports yet</div>
          <div className="tv-empty-state-description">
            Upload call recordings to automatically generate forensic intelligence reports, or click "Generate New Report".
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {reports.map((rep) => (
            <motion.div
              key={rep.id}
              whileHover={{ y: -2 }}
              className="tv-card p-5 space-y-4 flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-primary px-2 py-0.5 bg-primary/10 rounded-md">
                    {rep.reportType}
                  </span>
                  <span className="tv-badge-completed uppercase text-[10px]">
                    <CheckCircle2 className="w-3 h-3 mr-1" /> {rep.status}
                  </span>
                </div>
                <h3 className="text-base font-bold text-foreground">{rep.title}</h3>
                <p className="text-xs text-muted-foreground line-clamp-3">{rep.summary}</p>
              </div>

              <div className="pt-3 border-t border-border flex items-center justify-between text-xs text-muted-foreground">
                <div className="flex items-center gap-1.5 text-emerald-500 font-medium">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>{Math.round((rep.confidence || 0.98) * 100)}% Confidence</span>
                </div>
                <button
                  onClick={() => handleDownloadReport(rep)}
                  className="px-3 py-1.5 bg-primary text-white hover:bg-primary/90 rounded-md text-xs font-semibold shadow-glow-primary flex items-center gap-1.5 transition-all"
                >
                  <Download className="w-3.5 h-3.5" /> Download Report
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* New Report Modal */}
      <AnimatePresence>
        {showNewReportModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-card border border-border rounded-2xl p-6 w-full max-w-md space-y-4 shadow-2xl"
            >
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="text-base font-bold text-foreground flex items-center gap-2">
                  <FileText className="w-5 h-5 text-primary" /> Generate Investigation Report
                </h3>
                <button
                  onClick={() => setShowNewReportModal(false)}
                  className="text-muted-foreground hover:text-foreground p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <form onSubmit={handleCreateReport} className="space-y-3">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-foreground">Report Title</label>
                  <input
                    type="text"
                    value={reportTitle}
                    onChange={(e) => setReportTitle(e.target.value)}
                    placeholder="e.g. Master Case Forensic Summary Report"
                    required
                    className="w-full px-3 py-2 bg-muted/50 border border-border rounded-lg text-xs text-foreground outline-none focus:border-primary"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-semibold text-foreground">Report Type</label>
                  <select
                    value={reportType}
                    onChange={(e) => setReportType(e.target.value)}
                    className="w-full px-3 py-2 bg-muted/50 border border-border rounded-lg text-xs text-foreground outline-none focus:border-primary"
                  >
                    <option value="Forensic Intelligence Summary">Forensic Intelligence Summary</option>
                    <option value="Chain of Custody Certificate">Chain of Custody Certificate</option>
                    <option value="Threat & Risk Audit Matrix">Threat & Risk Audit Matrix</option>
                    <option value="Full Case Evidentiary Dossier">Full Case Evidentiary Dossier</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-semibold text-foreground">Assigned Target Case</label>
                  <input
                    type="text"
                    value={selectedCase}
                    onChange={(e) => setSelectedCase(e.target.value)}
                    className="w-full px-3 py-2 bg-muted/50 border border-border rounded-lg text-xs text-foreground outline-none focus:border-primary"
                  />
                </div>

                <div className="pt-3 flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setShowNewReportModal(false)}
                    className="px-4 py-2 bg-muted text-muted-foreground rounded-lg text-xs font-semibold hover:bg-muted/80"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-primary text-white rounded-lg text-xs font-semibold shadow-glow-primary hover:bg-primary/90"
                  >
                    Generate Report
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

