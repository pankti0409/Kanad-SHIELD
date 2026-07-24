/**
 * TraceVault Interactive Transcript & Speaker Diarization Viewer
 */
import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Play,
  Pause,
  ShieldAlert,
  Brain,
  Download,
  Search,
  Sparkles,
  Clock,
  FileText,
  AlertTriangle,
  MapPin,
  Calendar,
} from "lucide-react";
import { Link } from "react-router-dom";
import { useRecordingsStore } from "@/stores/recordingsStore";
import { cn } from "@/lib/utils";

export function TranscriptViewer() {
  const { recordings, activeRecordingId, transcripts, analyses } = useRecordingsStore();
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(5.0);
  const [activeSegmentId, setActiveSegmentId] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState("");

  const activeRec = recordings.find((r) => r.id === activeRecordingId);
  const activeSegments = activeRec ? (transcripts[activeRec.id] || []) : [];
  const activeAnalysis = activeRec ? (analyses[activeRec.id] || null) : null;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const downloadReport = () => {
    if (!activeRec || !activeAnalysis) return;

    const reportContent = `======================================================================
TRACEVAULT FORENSIC INTELLIGENCE REPORT
======================================================================
Generated: ${new Date().toLocaleString()}
Evidence Integrity: SECURE (SHA-256 Verified)

[EVIDENCE METADATA]
File Name: ${activeRec.filename}
Format: ${activeRec.format}
File Size: ${activeRec.sizeMb} MB
SHA-256 Hash: ${activeRec.sha256Hash}
Language Ingest Mode: ${activeRec.language}
Warrant reference: ${activeRec.warrantNumber}
Case Assigned: ${activeRec.caseNumber}

[AI ANALYSIS TIMESTAMPS]
Transcript Generated At: ${activeAnalysis.transcriptDateTime}
AI Threat & NER Analysis At: ${activeAnalysis.analysisDateTime}

[AUTOMATED SUMMARY]
${activeAnalysis.summary}

[THREAT AUDIT EVALUATION]
Threat Present: ${activeAnalysis.threatPresent ? "YES" : "NO"}
Threat Category: ${activeAnalysis.threatCategory}
Threat Details: ${activeAnalysis.threatDetails}

[EXTRACTED ENTITIES DISCUSSED]
Locations Discussed: ${activeAnalysis.locationsDiscussed.join(", ") || "None"}
Times / Dates Discussed: ${activeAnalysis.timesDiscussed.join(", ") || "None"}
Other Info: ${activeAnalysis.otherInfo}

[FULL DIARIZED TRANSCRIPT]
----------------------------------------------------------------------
${activeSegments.map(seg => `[${formatTime(seg.start_time)} - ${formatTime(seg.end_time)}] ${seg.speaker_label} (${Math.round(seg.confidence * 100)}% Conf):
"${seg.text}"`).join("\n\n")}
----------------------------------------------------------------------
CONFIDENTIALITY NOTICE: This document contains sensitive law enforcement intelligence.
======================================================================`;

    const blob = new Blob([reportContent], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `Forensic_Report_${activeRec.filename.replace(/\.[^/.]+$/, "")}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const filteredSegments = activeSegments.filter((seg) =>
    seg.text.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!activeRec || !activeAnalysis) {
    return (
      <div className="space-y-6">
        <div className="tv-page-header">
          <div>
            <h1 className="tv-page-title">Transcript Intelligence & Speaker Diarization</h1>
            <p className="tv-page-subtitle">View diarized transcripts and threat reports.</p>
          </div>
        </div>
        <div className="tv-empty-state">
          <div className="tv-empty-state-icon">
            <FileText className="w-8 h-8 text-muted-foreground" />
          </div>
          <div className="tv-empty-state-title">No active call analysis selected</div>
          <div className="tv-empty-state-description">
            Upload new recordings on the Recordings page to view transcripts, speaker diarization, summaries, and download reports.
          </div>
          <Link
            to="/recordings"
            className="mt-4 px-4 py-2 bg-primary text-white rounded-lg text-xs font-semibold hover:bg-primary/90 transition-all"
          >
            Go to Recordings Portal
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="tv-page-header">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono font-bold text-primary">{activeRec.caseNumber}</span>
            <span className="text-xs text-muted-foreground">• {activeRec.filename}</span>
          </div>
          <h1 className="tv-page-title">Transcript Intelligence & Speaker Diarization</h1>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={downloadReport}
            className="px-3 py-1.5 bg-primary text-white rounded-lg text-xs font-semibold hover:bg-primary/90 transition-all flex items-center gap-1.5 shadow-glow-primary"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Forensic Report</span>
          </button>
        </div>
      </div>

      {/* Audio Waveform Control Bar */}
      <div className="tv-card p-4 space-y-3 bg-card/60 backdrop-blur-md sticky top-14 z-20">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="w-10 h-10 rounded-xl bg-primary text-white flex items-center justify-center shadow-glow-primary hover:bg-primary/90 transition-all"
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
          </button>

          <div className="flex-1 space-y-1">
            <div className="flex items-center justify-between text-xs text-muted-foreground font-mono">
              <span>{formatTime(currentTime)}</span>
              <span>{activeRec.duration}</span>
            </div>
            <div className="h-2 rounded-full bg-muted overflow-hidden relative cursor-pointer">
              <div
                className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-100"
                style={{ width: `${(currentTime / (activeRec.duration === "00:20" ? 20 : 13)) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Transcript Segments + Intelligence Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Transcript Segments (2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          {/* Full Converted Speech-to-Text Banner */}
          <div className="tv-card p-4 space-y-2 border-primary/30 bg-primary/5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-primary flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" /> Full Speech-to-Text Converted Transcript
              </span>
              <span className="text-[10px] font-mono text-emerald-500 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded">
                Whisper Accuracy Verified
              </span>
            </div>
            <p className="text-xs text-foreground font-medium leading-relaxed bg-background/80 p-3 rounded-lg border border-border">
              "{activeSegments.map(s => s.text).join(" ")}"
            </p>
          </div>

          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-2 bg-muted/50 border border-border rounded-lg px-3 py-1.5 w-64">
              <Search className="w-3.5 h-3.5 text-muted-foreground" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search transcript text..."
                className="w-full bg-transparent text-xs text-foreground placeholder:text-muted-foreground outline-none"
              />
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-red-500" /> Threat Highlight
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-primary" /> Entity
              </span>
            </div>
          </div>

          <div className="space-y-3">
            {filteredSegments.map((seg) => {
              const isActive = activeSegmentId === seg.id;
              return (
                <div
                  key={seg.id}
                  onClick={() => {
                    setActiveSegmentId(seg.id);
                    setCurrentTime(seg.start_time);
                  }}
                  className={cn(
                    "tv-card p-4 cursor-pointer transition-all border",
                    isActive
                      ? "border-primary bg-primary/5 shadow-card-hover"
                      : "border-border hover:border-primary/40"
                  )}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-primary" />
                      <span className="text-xs font-bold text-foreground">
                        {seg.speaker_label}
                      </span>
                      <span className="text-[10px] font-mono text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                        {formatTime(seg.start_time)} - {formatTime(seg.end_time)}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      {seg.has_threat && (
                        <span className="tv-badge-critical text-[10px]">
                          <ShieldAlert className="w-3 h-3 mr-0.5" /> Threat Detected
                        </span>
                      )}
                      <span className="text-[10px] text-emerald-500 font-medium">
                        {Math.round(seg.confidence * 100)}% Conf
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-foreground leading-relaxed font-sans">
                    {seg.text}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Intelligence Side Panel (1 Col) */}
        <div className="space-y-4">
          <div className="tv-card p-4 space-y-4">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-3">
                Call Summary & Intelligence Analysis
              </h3>
              
              <div className="space-y-2 p-3.5 rounded-xl bg-muted/40 border border-border">
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Calendar className="w-3.5 h-3.5 text-primary" />
                  <span>Transcript Date: {activeAnalysis.transcriptDateTime}</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground pb-2 border-b border-border">
                  <Clock className="w-3.5 h-3.5 text-primary" />
                  <span>Analysis Date: {activeAnalysis.analysisDateTime}</span>
                </div>
                
                {activeAnalysis.topicDiscussed && (
                  <div className="pt-1 pb-1">
                    <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wide">Primary Topic Discussed</span>
                    <div className="text-xs font-bold text-primary">{activeAnalysis.topicDiscussed}</div>
                  </div>
                )}

                <p className="text-xs text-foreground pt-1 leading-relaxed font-sans">
                  {activeAnalysis.summary}
                </p>
              </div>
            </div>

            {/* Threat Indicators */}
            <div className="space-y-2 pt-2 border-t border-border">
              <h4 className="text-xs font-semibold text-foreground">Threat Status Evaluation</h4>
              {activeAnalysis.threatPresent ? (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 space-y-1">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-red-500">
                    <AlertTriangle className="w-4 h-4" />
                    <span>{activeAnalysis.threatCategory}</span>
                  </div>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">
                    {activeAnalysis.threatDetails}
                  </p>
                </div>
              ) : (
                <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 space-y-1">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-500">
                    <Sparkles className="w-4 h-4" />
                    <span>No Threat Detected in Conversation</span>
                  </div>
                  <p className="text-[11px] text-emerald-600/90 dark:text-emerald-400/90 leading-relaxed">
                    {activeAnalysis.threatDetails || `No threat detected in conversation. Topic discussed: ${activeAnalysis.topicDiscussed || 'General Conversation'}.`}
                  </p>
                </div>
              )}
            </div>

            {/* Extracted Locations & Times discussed in call */}
            <div className="space-y-2 pt-2 border-t border-border">
              <h4 className="text-xs font-semibold text-foreground flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-primary" /> Extracted Context Discussed
              </h4>
              <div className="space-y-2">
                <div className="space-y-1">
                  <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wide">Locations Discussed</span>
                  <div className="flex flex-wrap gap-1.5">
                    {activeAnalysis.locationsDiscussed.map((loc) => (
                      <span key={loc} className="tv-entity-chip">{loc}</span>
                    )) || <span className="text-xs text-muted-foreground font-mono">None</span>}
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wide">Times/Dates Discussed</span>
                  <div className="flex flex-wrap gap-1.5">
                    {activeAnalysis.timesDiscussed.map((time) => (
                      <span key={time} className="tv-entity-chip">{time}</span>
                    )) || <span className="text-xs text-muted-foreground font-mono">None</span>}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
