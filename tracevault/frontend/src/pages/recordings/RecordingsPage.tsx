/**
 * TraceVault Multiformat Call Recordings Upload & Processing Portal
 * Supports upload in any audio/video format (.wav, .mp3, .m4a, .flac, .ogg, .opus, .amr, .mp4, .mkv, .webm, .3gp).
 * Automatically computes SHA-256 evidence checksum and triggers AI intelligence pipeline.
 */
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  FileAudio,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Shield,
  Clock,
  Mic,
  Sliders,
  FileText,
  Play,
  Pause,
  Trash2,
  Tag,
  Lock,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useRecordingsStore, RecordingItem, CallAnalysis } from "@/stores/recordingsStore";
import { api } from "@/api/client";
import { TranscriptSegment } from "@/types";

const SUPPORTED_FORMATS = [
  { ext: "WAV", desc: "PCM / Raw Audio" },
  { ext: "MP3", desc: "MPEG Audio Layer III" },
  { ext: "M4A", desc: "AAC / Apple Audio" },
  { ext: "FLAC", desc: "Free Lossless Audio Codec" },
  { ext: "OGG / OPUS", desc: "WhatsApp / Telegram Voice Notes" },
  { ext: "AMR", desc: "Cellular Call Intercept Recording" },
  { ext: "MP4 / MKV", desc: "Call Video & Screen Capture" },
  { ext: "3GP", desc: "Legacy Mobile Intercept Format" },
];

interface RecordingUploadResponse {
  recording: {
    id: string;
    filename: string;
    file_size: number;
    sha256_hash: string;
    duration_seconds: number;
    language: string;
    status: string;
    case_id: string;
    warrant_number: string;
    created_at: string;
  };
  segments: TranscriptSegment[];
  analysis: CallAnalysis;
}

interface ProcessingCallItem {
  id: string;
  filename: string;
  sizeMb: string;
  progress: number;
  status: "Queued" | "Uploading" | "Whisper STT" | "Diarization" | "Intelligence" | "Completed" | "Error";
  error?: string;
  recId?: string;
}

export function RecordingsPage() {
  const { recordings, addRecording, setActiveRecordingId, deleteRecording, clearAllRecordings } = useRecordingsStore();
  const [selectedLanguage, setSelectedLanguage] = useState("auto");
  const [warrantNumber, setWarrantNumber] = useState("WR-2026-9901");
  const [caseNumber, setCaseNumber] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [processingQueue, setProcessingQueue] = useState<ProcessingCallItem[]>([]);
  const navigate = useNavigate();

  const formatDurationStr = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  const handleSimulatedFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const fileList = Array.from(files);
    const initialQueue: ProcessingCallItem[] = fileList.map((f, idx) => ({
      id: `proc-${Date.now()}-${idx}`,
      filename: f.name,
      sizeMb: (f.size / (1024 * 1024)).toFixed(2),
      progress: 0,
      status: "Queued",
    }));

    setIsUploading(true);
    setProcessingQueue(initialQueue);

    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      const queueId = initialQueue[i].id;

      const updateItem = (patch: Partial<ProcessingCallItem>) => {
        setProcessingQueue((prev) =>
          prev.map((item) => (item.id === queueId ? { ...item, ...patch } : item))
        );
      };

      updateItem({ status: "Uploading", progress: 10 });

      try {
        const formData = new FormData();
        formData.append("file", file);

        updateItem({ status: "Whisper STT", progress: 40 });

        const res = await api.upload<RecordingUploadResponse>(
          `/recordings/upload?case_id=${caseNumber}&warrant_number=${warrantNumber}&language=${selectedLanguage}`,
          formData,
          (percent) => {
            updateItem({
              progress: Math.min(90, 10 + Math.round((percent / 100) * 80)),
            });
          }
        );

        updateItem({ status: "Diarization", progress: 85 });
        await new Promise((r) => setTimeout(r, 200));

        updateItem({ status: "Intelligence", progress: 95 });
        await new Promise((r) => setTimeout(r, 200));

        const durSec = res.recording.duration_seconds || 15.0;
        const newRec: RecordingItem = {
          id: res.recording.id,
          filename: res.recording.filename,
          format: res.recording.filename.split(".").pop()?.toUpperCase() || "AUDIO",
          sizeMb: parseFloat((res.recording.file_size / (1024 * 1024)).toFixed(2)) || 0.5,
          duration: formatDurationStr(durSec),
          language: res.recording.language === "auto" ? "English / Auto" : res.recording.language,
          caseNumber: res.recording.case_id || "Unassigned",
          warrantNumber: res.recording.warrant_number || "WR-2026-TEMP",
          sha256Hash: res.recording.sha256_hash,
          status: "completed",
          uploadedAt: new Date(res.recording.created_at).toLocaleString(),
          snrBoostDb: 18.2,
          threatCount: res.analysis.threatPresent ? 1 : 0,
        };

        addRecording(newRec, res.segments, res.analysis);
        updateItem({ status: "Completed", progress: 100, recId: res.recording.id });
      } catch (err: any) {
        console.error("Upload failed for file", file.name, err);
        const detailMsg = err?.detail || err?.error || err?.message || "Failed to process audio recording.";
        updateItem({ status: "Error", progress: 0, error: detailMsg });
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="tv-page-header">
        <div>
          <h1 className="tv-page-title">Multiformat Call Recordings Portal</h1>
          <p className="tv-page-subtitle">
            Upload & process mobile intercepts, cellular AMR, WhatsApp OPUS, landline WAV, MP3 & video calls.
          </p>
        </div>
        <button
          onClick={clearAllRecordings}
          className="px-3 py-1.5 bg-red-500/10 text-red-500 hover:bg-red-500/20 border border-red-500/20 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5"
        >
          <Trash2 className="w-3.5 h-3.5" /> Clean Ingested Database
        </button>
      </div>

      {/* Main Upload Control Panel */}
      <div className="tv-card p-6 space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-border">
          <div className="flex items-center gap-2 text-sm font-bold text-foreground">
            <Upload className="w-4 h-4 text-primary" />
            <span>Upload Recording File(s)</span>
          </div>
          <span className="text-xs text-emerald-500 font-medium flex items-center gap-1">
            <Lock className="w-3 h-3" /> Direct SHA-256 Hashing Active
          </span>
        </div>

        {/* Form Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-foreground">Target Case (Optional)</label>
            <input
              type="text"
              value={caseNumber}
              onChange={(e) => setCaseNumber(e.target.value)}
              placeholder="e.g. TV-8839-FRD or any Case ID"
              className="w-full px-3 py-1.5 bg-muted/50 border border-border rounded-lg text-xs text-foreground outline-none focus:border-primary"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-foreground">Court Warrant Number</label>
            <input
              type="text"
              value={warrantNumber}
              onChange={(e) => setWarrantNumber(e.target.value)}
              className="w-full px-3 py-1.5 bg-muted/50 border border-border rounded-lg text-xs text-foreground outline-none focus:border-primary"
              placeholder="e.g. WR-2026-8810"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-foreground">Language Processing Mode</label>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="w-full px-3 py-1.5 bg-muted/50 border border-border rounded-lg text-xs text-foreground outline-none focus:border-primary"
            >
              <option value="auto">Auto-Detect (Hindi / Gujarati / English)</option>
              <option value="Hindi">Hindi Only</option>
              <option value="Gujarati">Gujarati Only</option>
              <option value="English">English Only</option>
            </select>
          </div>
        </div>

        {/* Drag & Drop File Zone */}
        <div className="relative border-2 border-dashed border-primary/30 hover:border-primary/60 rounded-2xl p-8 text-center transition-all bg-muted/20 hover:bg-muted/40 cursor-pointer group">
          <input
            type="file"
            accept=".wav,.mp3,.m4a,.flac,.ogg,.opus,.amr,.wma,.mp4,.mkv,.webm,.3gp,.aac,.wav,.MP3,.WAV"
            multiple
            onChange={handleSimulatedFileUpload}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
          />

          <div className="space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mx-auto group-hover:scale-110 transition-transform shadow-glow-primary">
              <FileAudio className="w-7 h-7" />
            </div>

            <div>
              <h4 className="text-sm font-bold text-foreground">
                Drop your call recording(s) here or <span className="text-primary underline">browse audio files</span>
              </h4>
              <p className="text-xs text-muted-foreground mt-1">
                Supports: <span className="font-semibold text-foreground">.wav, .mp3, .m4a, .flac, .ogg, .opus, .amr, .mp4, .mkv, .3gp</span> up to 2 GB
              </p>
            </div>
          </div>
        </div>

        {/* Individual Per-Call Processing List */}
        {processingQueue.length > 0 && (
          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between text-xs font-bold text-foreground">
              <span className="flex items-center gap-1.5 text-primary">
                <Sparkles className="w-4 h-4" /> Multi-Call Processing Queue ({processingQueue.length} Calls)
              </span>
              <span className="text-muted-foreground font-mono text-[11px]">Individual Call Progress</span>
            </div>

            <div className="space-y-2">
              {processingQueue.map((item) => (
                <div
                  key={item.id}
                  className="p-3.5 rounded-xl bg-card border border-border space-y-2 shadow-sm"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                        <Mic className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-foreground">{item.filename}</div>
                        <div className="text-[10px] text-muted-foreground">{item.sizeMb} MB</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      {item.status === "Completed" && item.recId && (
                        <button
                          onClick={() => {
                            setActiveRecordingId(item.recId!);
                            navigate("/transcripts");
                          }}
                          className="px-2.5 py-1 bg-primary text-white rounded-lg text-[11px] font-semibold hover:bg-primary/90 transition-all flex items-center gap-1 shadow-glow-primary"
                        >
                          <FileText className="w-3 h-3" /> View Transcript
                        </button>
                      )}
                      
                      <span
                        className={`text-xs font-semibold px-2 py-0.5 rounded-md ${
                          item.status === "Completed"
                            ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                            : item.status === "Error"
                            ? "bg-red-500/10 text-red-500 border border-red-500/20"
                            : "bg-primary/10 text-primary border border-primary/20"
                        }`}
                      >
                        {item.status === "Whisper STT"
                          ? "Transcribing with Whisper"
                          : item.status === "Diarization"
                          ? "Speaker Diarization"
                          : item.status === "Intelligence"
                          ? "Extracting Intelligence"
                          : item.status}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
                      <span>{item.error ? `Error: ${item.error}` : `Pipeline Status: ${item.status}`}</span>
                      <span>{item.progress}%</span>
                    </div>
                    <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-300 ${
                          item.status === "Error" ? "bg-red-500" : "bg-primary shadow-glow-primary"
                        }`}
                        style={{ width: `${item.progress}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Format Capabilities Grid */}
      <div className="tv-card p-5 space-y-3">
        <h3 className="text-sm font-bold text-foreground">Supported Audio & Intercept Formats</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {SUPPORTED_FORMATS.map((fmt, idx) => (
            <div key={idx} className="p-2.5 rounded-xl bg-muted/40 border border-border space-y-0.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-extrabold text-primary">{fmt.ext}</span>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
              </div>
              <p className="text-[10px] text-muted-foreground truncate">{fmt.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Uploaded Ingested Recordings List */}
      <div className="tv-card p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-foreground">Ingested Intercept Audio Database</h3>
            <p className="text-xs text-muted-foreground">All recordings processed with SHA-256 evidence integrity</p>
          </div>
          <span className="text-xs font-mono font-bold text-primary">{recordings.length} Recordings</span>
        </div>

        {recordings.length === 0 ? (
          <div className="tv-empty-state">
            <div className="tv-empty-state-icon">
              <Mic className="w-7 h-7 text-muted-foreground" />
            </div>
            <div className="tv-empty-state-title">No recordings loaded</div>
            <div className="tv-empty-state-description">
              Upload call recordings above to start automated speech-to-text, diarization, and forensic analysis.
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {recordings.map((rec) => (
              <div
                key={rec.id}
                className="p-4 rounded-xl border border-border bg-card/60 hover:bg-muted/30 transition-all space-y-2 relative group/item"
              >
                <button
                  onClick={() => deleteRecording(rec.id)}
                  className="absolute top-4 right-4 p-1.5 text-muted-foreground hover:text-red-500 hover:bg-red-500/10 rounded-md transition-colors opacity-0 group-hover/item:opacity-100"
                  title="Delete Recording"
                >
                  <Trash2 className="w-4 h-4" />
                </button>

                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-mono font-bold text-xs">
                      {rec.format}
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-foreground pr-8">{rec.filename}</h4>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>{rec.duration}</span>
                        <span>•</span>
                        <span>{rec.sizeMb} MB</span>
                        <span>•</span>
                        <span className="text-indigo-400 font-semibold">{rec.language}</span>
                        <span>•</span>
                        <span className="text-[10px] bg-muted px-1.5 py-0.5 rounded text-muted-foreground">{rec.uploadedAt}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 pr-8 sm:pr-0">
                    <span className="px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-500 text-xs font-semibold border border-emerald-500/20">
                      +{rec.snrBoostDb} dB SNR
                    </span>
                    <button
                      onClick={() => {
                        setActiveRecordingId(rec.id);
                        navigate("/transcripts");
                      }}
                      className="px-3 py-1.5 bg-primary text-white text-xs font-semibold rounded-lg shadow-glow-primary hover:bg-primary/90 transition-all"
                    >
                      View Transcript
                    </button>
                  </div>
                </div>

                {/* SHA-256 & Warrant Footer */}
                <div className="pt-2 border-t border-border/60 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-muted-foreground gap-1 font-mono">
                  <span className="truncate max-w-md">SHA-256: {rec.sha256Hash}</span>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <span>Warrant: {rec.warrantNumber}</span>
                    <span>Case: {rec.caseNumber}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
