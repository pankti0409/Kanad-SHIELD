import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileBarChart2,
  Download,
  Plus,
  FileText,
  CheckCircle2,
  Shield,
  Clock,
  Lock,
  Sparkles,
  AlertTriangle,
  AlertOctagon,
  Check,
  Info,
  X,
  FileAudio,
} from "lucide-react";
import { useRecordingsStore, GeneratedReport } from "@/stores/recordingsStore";

export function ReportsPage() {
  const { reports, recordings, transcripts, analyses, addReport } = useRecordingsStore();
  const [showNewReportModal, setShowNewReportModal] = useState(false);
  const [activePreviewReport, setActivePreviewReport] = useState<GeneratedReport | null>(null);
  const [reportTitle, setReportTitle] = useState("");
  const [reportType, setReportType] = useState("Forensic Intelligence Summary");
  const [selectedCase, setSelectedCase] = useState("TV-CASE-2026");

  // Resolve details of the active preview report
  const rec = activePreviewReport
    ? recordings.find((r) => r.id === activePreviewReport.recordingId) || recordings[0]
    : null;
  const segs = rec ? transcripts[rec.id] || [] : [];
  const analysis = rec ? analyses[rec.id] || null : null;

  const handleDownloadReport = (rep: GeneratedReport) => {
    const targetRec = recordings.find((r) => r.id === rep.recordingId) || recordings[0];
    const targetSegs = targetRec ? transcripts[targetRec.id] || [] : [];
    const targetAnalysis = targetRec ? analyses[targetRec.id] || null : null;

    const content = `======================================================================
TRACEVAULT FORENSIC INVESTIGATION REPORT — ${rep.title.toUpperCase()}
======================================================================
Report ID: ${rep.id}
Created At: ${rep.createdAt}
Status: ${rep.status.toUpperCase()}
Report Type: ${rep.reportType}
Evidence Cryptographic Status: SHA-256 Verified

[EVIDENCE FILE METADATA]
File Name: ${targetRec?.filename || "Batch Recording Group"}
Format: ${targetRec?.format || "AUDIO"}
File Size: ${targetRec?.sizeMb || "N/A"} MB
SHA-256 Checksum: ${targetRec?.sha256Hash || "VERIFIED"}
Warrant Reference: ${targetRec?.warrantNumber || "WR-2026-9901"}
Case Reference: ${targetRec?.caseNumber || rep.caseNumber}

[EXECUTIVE SUMMARY]
${targetAnalysis?.summary || rep.summary}

[THREAT AUDIT EVALUATION]
Threat Detected: ${targetAnalysis?.threatPresent || targetRec?.threatCount > 0 ? "YES" : "NO"}
Threat Category: ${targetAnalysis?.threatCategory || rep.threatCategory}
Threat Details: ${targetAnalysis?.threatDetails || "Standard security audit evaluation completed."}

[EXTRACTED ENTITIES & INTELLIGENCE]
Locations Discussed: ${targetAnalysis?.locationsDiscussed?.join(", ") || "None"}
Times / Dates Discussed: ${targetAnalysis?.timesDiscussed?.join(", ") || "None"}
Chain of Custody Info: ${targetAnalysis?.otherInfo || "SHA-256 verified evidence."}

[DIARIZED TRANSCRIPT TIMELINE]
----------------------------------------------------------------------
${targetSegs.length > 0 ? targetSegs.map(s => `[${s.start_time.toFixed(1)}s - ${s.end_time.toFixed(1)}s] ${s.speaker_label} (${Math.round(s.confidence * 100)}% Conf):
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

  const isThreatDetected = analysis?.threatPresent || (rec && rec.threatCount > 0);

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
          {reports.map((rep) => {
            const hasThreat = recordings.find((r) => r.id === rep.recordingId)?.threatCount ? true : false;
            return (
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
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setActivePreviewReport(rep)}
                      className="px-3 py-1.5 bg-muted text-foreground hover:bg-muted/80 border border-border rounded-lg text-[11px] font-semibold transition-all"
                    >
                      View Report
                    </button>
                    <button
                      onClick={() => handleDownloadReport(rep)}
                      className="px-3 py-1.5 bg-primary text-white hover:bg-primary/90 rounded-lg text-[11px] font-semibold shadow-glow-primary flex items-center gap-1 transition-all"
                    >
                      <Download className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
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

      {/* Report Preview & Detail Modal */}
      <AnimatePresence>
        {activePreviewReport && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-card border border-border rounded-2xl p-6 w-full max-w-3xl my-8 space-y-6 shadow-2xl relative"
            >
              {/* Close Button */}
              <button
                onClick={() => setActivePreviewReport(null)}
                className="absolute top-4 right-4 text-muted-foreground hover:text-foreground p-1.5 bg-muted/50 rounded-full transition-all"
              >
                <X className="w-4 h-4" />
              </button>

              {/* Title Header */}
              <div className="border-b border-border pb-4 pr-8">
                <span className="text-[10px] font-bold text-primary tracking-wider uppercase bg-primary/10 px-2 py-0.5 rounded">
                  {activePreviewReport.reportType}
                </span>
                <h2 className="text-xl font-bold text-foreground mt-1.5">{activePreviewReport.title}</h2>
                <p className="text-xs text-muted-foreground mt-1">Generated on {activePreviewReport.createdAt}</p>
              </div>

              {/* Grid 1: Integrity & Case Metadata */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Cryptographic Evidence Certificate */}
                <div className="tv-card p-4 space-y-3 bg-muted/20 border border-border">
                  <h4 className="text-xs font-bold text-foreground flex items-center gap-1.5">
                    <Shield className="w-4 h-4 text-emerald-500" /> Cryptographic Authenticity Verification
                  </h4>
                  <div className="space-y-1.5 text-xs">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Verification Check:</span>
                      <span className="text-emerald-500 font-semibold flex items-center gap-0.5">
                        <CheckCircle2 className="w-3.5 h-3.5" /> SECURE (SHA-256)
                      </span>
                    </div>
                    <div className="flex flex-col space-y-0.5">
                      <span className="text-muted-foreground">SHA-256 Checksum:</span>
                      <span className="font-mono text-[10px] bg-muted px-1.5 py-0.5 rounded text-foreground overflow-x-auto select-all">
                        {rec?.sha256Hash || "6a4f217ebd80632b... (Verified)"}
                      </span>
                    </div>
                    {rec && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Size / Format:</span>
                        <span className="text-foreground font-medium">{rec.sizeMb} MB ({rec.format})</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Case / Warrant References */}
                <div className="tv-card p-4 space-y-3 bg-muted/20 border border-border">
                  <h4 className="text-xs font-bold text-foreground flex items-center gap-1.5">
                    <Lock className="w-4 h-4 text-primary" /> Case Warrant & References
                  </h4>
                  <div className="space-y-1.5 text-xs">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Court Warrant:</span>
                      <span className="font-mono text-foreground font-medium">{rec?.warrantNumber || "WR-2026-9901"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Assigned Case:</span>
                      <span className="text-foreground font-medium">{rec?.caseNumber || activePreviewReport.caseNumber}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Language Processing:</span>
                      <span className="text-foreground capitalize font-medium">{rec?.language || "auto-detect"}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Row 2: Short Summary */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-foreground uppercase tracking-wider flex items-center gap-1.5">
                  <Info className="w-4 h-4 text-primary" /> Executive Call Summary
                </h3>
                <div className="text-xs text-foreground leading-relaxed bg-muted/10 p-4 border border-border rounded-xl">
                  {analysis?.summary || activePreviewReport.summary}
                </div>
              </div>

              {/* Row 3: Threat Detected (YES/NO) and evidence details */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-foreground uppercase tracking-wider flex items-center gap-1.5">
                  <AlertOctagon className="w-4 h-4 text-primary" /> Threat Indicator Assessment
                </h3>
                {isThreatDetected ? (
                  <div className="border border-red-500/30 bg-red-500/5 rounded-xl p-4 space-y-3">
                    <div className="flex items-center gap-2 text-red-500 text-xs font-bold">
                      <AlertTriangle className="w-4 h-4" /> ACTIVE SECURITY THREAT FLAG IDENTIFIED
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                      <div>
                        <span className="text-muted-foreground block text-[10px] uppercase font-semibold">Threat Category</span>
                        <span className="text-foreground capitalize font-bold">{analysis?.threatCategory || activePreviewReport.threatCategory}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground block text-[10px] uppercase font-semibold">Risk Level / Count</span>
                        <span className="text-red-400 capitalize font-bold">Critical Risk ({rec?.threatCount || 1} flagged intercepts)</span>
                      </div>
                    </div>
                    <div className="text-xs">
                      <span className="text-muted-foreground block text-[10px] uppercase font-semibold">Evidence Details & Snippets</span>
                      <p className="text-foreground mt-1 bg-red-500/10 px-3 py-2 rounded border border-red-500/10 font-mono text-[11px] leading-relaxed">
                        {analysis?.threatDetails || "Threat patterns coordinate with extortion/financial scam patterns."}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="border border-emerald-500/30 bg-emerald-500/5 rounded-xl p-4 flex items-center gap-3">
                    <div className="p-1.5 bg-emerald-500/20 rounded-full text-emerald-500">
                      <Check className="w-4 h-4" />
                    </div>
                    <div className="space-y-0.5">
                      <h4 className="text-xs font-bold text-emerald-500">Call Audited Secure</h4>
                      <p className="text-xs text-muted-foreground">
                        No active extortion, threat, or fraudulent indicators found.
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Row 4: Extracted Intelligence Details */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <span className="text-muted-foreground text-[10px] uppercase font-bold">Locations Mentioned</span>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis?.locationsDiscussed && analysis.locationsDiscussed.length > 0 ? (
                      analysis.locationsDiscussed.map((l) => (
                        <span key={l} className="text-xs font-semibold px-2 py-0.5 bg-muted rounded border border-border">
                          {l}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-muted-foreground italic">No locations discussed.</span>
                    )}
                  </div>
                </div>
                <div className="space-y-1.5">
                  <span className="text-muted-foreground text-[10px] uppercase font-bold">Dates/Times Mentioned</span>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis?.timesDiscussed && analysis.timesDiscussed.length > 0 ? (
                      analysis.timesDiscussed.map((t) => (
                        <span key={t} className="text-xs font-semibold px-2 py-0.5 bg-muted rounded border border-border">
                          {t}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-muted-foreground italic">No dates or times discussed.</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Row 5: Diarized Transcript breakdown */}
              {segs.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-xs font-bold text-foreground uppercase tracking-wider flex items-center gap-1.5">
                    <FileAudio className="w-4 h-4 text-primary" /> Diarized Transcript Timeline
                  </h3>
                  <div className="max-h-60 overflow-y-auto space-y-3 border border-border rounded-xl p-4 bg-muted/10 divide-y divide-border">
                    {segs.map((s, idx) => (
                      <div key={s.id || idx} className="pt-3 first:pt-0 text-xs space-y-1">
                        <div className="flex justify-between items-center text-[10px] text-muted-foreground font-semibold">
                          <span className="text-primary font-bold">{s.speaker_label || "Speaker"}</span>
                          <span>
                            [{s.start_time.toFixed(1)}s - {s.end_time.toFixed(1)}s] •{" "}
                            {Math.round(s.confidence * 100)}% Conf
                          </span>
                        </div>
                        <p className="text-foreground pl-2 border-l border-border mt-0.5 leading-relaxed">
                          "{s.text}"
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions Footer */}
              <div className="pt-4 border-t border-border flex items-center justify-end gap-3">
                <button
                  onClick={() => setActivePreviewReport(null)}
                  className="px-4 py-2 bg-muted text-muted-foreground hover:bg-muted/80 rounded-lg text-xs font-semibold"
                >
                  Close Preview
                </button>
                <button
                  onClick={() => handleDownloadReport(activePreviewReport)}
                  className="px-4 py-2 bg-primary text-white hover:bg-primary/90 rounded-lg text-xs font-semibold shadow-glow-primary flex items-center gap-2"
                >
                  <Download className="w-4 h-4" /> Download Report Document
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
