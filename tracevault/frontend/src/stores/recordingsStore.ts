import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { TranscriptSegment } from "@/types";

export interface RecordingItem {
  id: string;
  filename: string;
  format: string;
  sizeMb: number;
  duration: string;
  duration_seconds?: number;
  language: string;
  caseNumber: string;
  warrantNumber: string;
  sha256Hash: string;
  status: "completed" | "processing" | "queued";
  uploadedAt: string;
  snrBoostDb: number;
  threatCount: number;
}

export interface CallAnalysis {
  transcriptDateTime: string;
  analysisDateTime: string;
  summary: string;
  topicDiscussed?: string;
  threatPresent: boolean;
  threatCategory: string;
  threatDetails: string;
  locationsDiscussed: string[];
  timesDiscussed: string[];
  otherInfo: string;
}

export interface GeneratedReport {
  id: string;
  recordingId: string;
  title: string;
  caseNumber: string;
  reportType: string;
  status: string;
  createdAt: string;
  confidence: number;
  summary: string;
  threatCategory: string;
}

interface RecordingsState {
  recordings: RecordingItem[];
  activeRecordingId: string | null;
  transcripts: Record<string, TranscriptSegment[]>;
  analyses: Record<string, CallAnalysis>;
  reports: GeneratedReport[];

  // Actions
  setActiveRecordingId: (id: string | null) => void;
  addRecording: (recording: RecordingItem, segments: TranscriptSegment[], analysis: CallAnalysis) => void;
  deleteRecording: (id: string) => void;
  clearAllRecordings: () => void;
  addReport: (report: GeneratedReport) => void;
}

export const useRecordingsStore = create<RecordingsState>()(
  persist(
    (set) => ({
      recordings: [],
      activeRecordingId: null,
      transcripts: {},
      analyses: {},
      reports: [],

      setActiveRecordingId: (id) => set({ activeRecordingId: id }),

      addRecording: (recording, segments, analysis) =>
        set((state) => {
          const autoReport: GeneratedReport = {
            id: `rep-${recording.id}`,
            recordingId: recording.id,
            title: `Forensic Intelligence Report - ${recording.filename}`,
            caseNumber: recording.caseNumber,
            reportType: "Whisper Large v3 Call Analysis & Evidence Audit",
            status: "approved",
            createdAt: recording.uploadedAt,
            confidence: 0.98,
            summary: analysis.summary,
            threatCategory: analysis.threatCategory,
          };

          return {
            recordings: [recording, ...state.recordings],
            transcripts: { ...state.transcripts, [recording.id]: segments },
            analyses: { ...state.analyses, [recording.id]: analysis },
            reports: [autoReport, ...state.reports],
            activeRecordingId: state.activeRecordingId || recording.id,
          };
        }),

      deleteRecording: (id) =>
        set((state) => {
          const newRecordings = state.recordings.filter((r) => r.id !== id);
          const newTranscripts = { ...state.transcripts };
          const newAnalyses = { ...state.analyses };
          delete newTranscripts[id];
          delete newAnalyses[id];
          return {
            recordings: newRecordings,
            transcripts: newTranscripts,
            analyses: newAnalyses,
            reports: state.reports.filter((rep) => rep.recordingId !== id),
            activeRecordingId: state.activeRecordingId === id ? (newRecordings[0]?.id || null) : state.activeRecordingId,
          };
        }),

      clearAllRecordings: () =>
        set({
          recordings: [],
          transcripts: {},
          analyses: {},
          reports: [],
          activeRecordingId: null,
        }),

      addReport: (report) =>
        set((state) => ({
          reports: [report, ...state.reports],
        })),
    }),
    {
      name: "tracevault_recordings_store",
      storage: createJSONStorage(() => localStorage),
    }
  )
);

