/**
 * TraceVault Type Definitions
 * Complete type system for all domain entities.
 */

// ============================================================
// User & Authentication
// ============================================================

export type UserRole =
  | "system_admin"
  | "supervisor"
  | "senior_investigator"
  | "investigator"
  | "analyst"
  | "legal_officer"
  | "read_only";

export type UserStatus =
  | "active"
  | "inactive"
  | "suspended"
  | "pending_verification"
  | "locked";

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  phone?: string;
  badge_number?: string;
  department?: string;
  designation?: string;
  organization?: string;
  role: UserRole;
  status: UserStatus;
  avatar_url?: string;
  timezone: string;
  language: string;
  last_login_at?: string;
  created_at: string;
  updated_at: string;
}

export interface UserSession {
  id: string;
  device_info?: string;
  user_agent?: string;
  ip_address?: string;
  browser?: string;
  operating_system?: string;
  is_active: boolean;
  last_activity_at?: string;
  expires_at: string;
  created_at: string;
}

export interface LoginCredentials {
  identifier: string;
  password: string;
  remember_me?: boolean;
  device_info?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// ============================================================
// Cases
// ============================================================

export type CaseStatus =
  | "open"
  | "under_investigation"
  | "pending_review"
  | "evidence_processing"
  | "completed"
  | "archived"
  | "closed";

export type CasePriority = "low" | "medium" | "high" | "critical";

export type CaseCategory =
  | "fraud"
  | "cybercrime"
  | "extortion"
  | "drug_trafficking"
  | "human_trafficking"
  | "violence"
  | "financial_crime"
  | "organized_crime"
  | "terrorism"
  | "corruption"
  | "general"
  | "other";

export interface Case {
  id: string;
  case_number: string;
  title: string;
  description?: string;
  status: CaseStatus;
  priority: CasePriority;
  category: CaseCategory;
  tags?: string[];
  risk_score?: number;
  risk_level?: RiskLevel;
  recording_count: number;
  evidence_count: number;
  report_count: number;
  lead_investigator_id?: string;
  created_by: string;
  expected_completion_date?: string;
  created_at: string;
  updated_at: string;
}

export interface CaseMember {
  id: string;
  case_id: string;
  user_id: string;
  user?: User;
  role: "lead" | "member" | "observer";
  can_upload: boolean;
  can_export: boolean;
  can_edit: boolean;
  created_at: string;
}

export interface InvestigatorNote {
  id: string;
  case_id: string;
  recording_id?: string;
  segment_id?: string;
  author_id: string;
  author?: User;
  title?: string;
  content: string;
  is_pinned: boolean;
  is_private: boolean;
  note_type: string;
  timestamp_reference?: number;
  created_at: string;
  updated_at: string;
}

export interface CaseTask {
  id: string;
  case_id: string;
  assigned_to_id?: string;
  assignee?: User;
  created_by: string;
  title: string;
  description?: string;
  status: "pending" | "in_progress" | "completed" | "cancelled";
  priority: "low" | "medium" | "high" | "critical";
  due_date?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

// ============================================================
// Recordings
// ============================================================

export type ProcessingStatus =
  | "queued"
  | "preparing"
  | "enhancing"
  | "reducing_noise"
  | "detecting_speech"
  | "detecting_speakers"
  | "transcribing"
  | "running_ai"
  | "generating_embeddings"
  | "saving_results"
  | "completed"
  | "failed"
  | "cancelled"
  | "retrying";

export type RiskLevel = "very_low" | "low" | "medium" | "high" | "critical";

export interface Recording {
  id: string;
  case_id: string;
  uploaded_by_id: string;
  uploader?: User;
  original_filename: string;
  stored_filename: string;
  sha256_hash: string;
  file_size_bytes: number;
  mime_type: string;
  duration_seconds?: number;
  sample_rate?: number;
  channels?: number;
  processing_status: ProcessingStatus;
  processing_progress: number;
  processing_error?: string;
  detected_language?: string;
  detected_language_confidence?: number;
  is_multilingual: boolean;
  risk_level?: RiskLevel;
  risk_score?: number;
  threat_count: number;
  entity_count: number;
  keyword_count: number;
  speaker_count: number;
  transcription_confidence?: number;
  word_count: number;
  integrity_verified: boolean;
  evidence_version: number;
  created_at: string;
  updated_at: string;
}

// ============================================================
// Transcripts
// ============================================================

export interface Speaker {
  id: string;
  recording_id: string;
  speaker_label: string;
  display_name?: string;
  identified_as?: string;
  speaking_duration_seconds?: number;
  speaking_percentage?: number;
  turn_count: number;
  confidence?: number;
  color_hex?: string;
}

export interface TranscriptWord {
  word: string;
  start: number;
  end: number;
  probability: number;
}

export interface TranscriptSegment {
  id: string;
  transcript_id: string;
  speaker_id?: string;
  speaker_label?: string;
  speaker?: Speaker;
  sequence_number: number;
  start_time: number;
  end_time: number;
  text: string;
  confidence: number;
  language?: string;
  word_count: number;
  character_count?: number;
  has_threat: boolean;
  has_entity: boolean;
  has_keyword: boolean;
  emotion?: EmotionType;
  words?: TranscriptWord[];
}

export interface Transcript {
  id: string;
  recording_id: string;
  full_text: string;
  language: string;
  confidence: number;
  word_count: number;
  character_count: number;
  duration_seconds?: number;
  model_used: string;
  model_version?: string;
  is_verified: boolean;
  segments: TranscriptSegment[];
  created_at: string;
}

// ============================================================
// AI Intelligence
// ============================================================

export type EmotionType =
  | "neutral"
  | "happy"
  | "sad"
  | "angry"
  | "fear"
  | "stress"
  | "calm"
  | "excited"
  | "frustrated"
  | "unknown";

export type ThreatCategory =
  | "violence"
  | "self_harm"
  | "kidnapping"
  | "fraud"
  | "scam"
  | "money_laundering"
  | "drug_activity"
  | "weapon_discussion"
  | "extortion"
  | "cyber_attack"
  | "blackmail"
  | "bribery"
  | "human_trafficking"
  | "illegal_trade"
  | "suspicious_coordination"
  | "other";

export interface Entity {
  id: string;
  recording_id: string;
  entity_type: string;
  entity_value: string;
  normalized_value?: string;
  speaker_label?: string;
  timestamp?: number;
  end_timestamp?: number;
  confidence: number;
  context_sentence?: string;
  is_reviewed: boolean;
  review_status?: string;
}

export interface Keyword {
  id: string;
  recording_id: string;
  keyword_text: string;
  normalized_text?: string;
  category?: string;
  frequency: number;
  importance_score: number;
  speaker_label?: string;
  first_occurrence?: number;
  last_occurrence?: number;
  occurrences?: number[];
}

export interface ThreatIndicator {
  id: string;
  recording_id: string;
  category: ThreatCategory;
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  evidence_text: string;
  speaker_label?: string;
  timestamp?: number;
  end_timestamp?: number;
  confidence: number;
  is_reviewed: boolean;
  review_status?: string;
  model_used?: string;
  reasoning?: string;
}

export interface EmotionAnalysis {
  id: string;
  recording_id: string;
  speaker_label?: string;
  emotion: EmotionType;
  confidence: number;
  start_time: number;
  end_time: number;
  intensity?: number;
  raw_scores?: Record<string, number>;
}

export interface RiskScore {
  recording_id: string;
  risk_level: RiskLevel;
  overall_score: number;
  threat_score: number;
  emotion_score: number;
  entity_score: number;
  topic_score: number;
  keyword_score: number;
  explanation?: string;
  factors?: Record<string, unknown>;
}

export interface ConversationSummary {
  id: string;
  recording_id: string;
  summary_type: "executive" | "legal" | "entity" | "threat" | "speaker" | "full";
  content: string;
  confidence: number;
  model_used: string;
  language: string;
  evidence_references?: string[];
  created_at: string;
}

export interface TimelineEvent {
  id: string;
  recording_id: string;
  event_type: string;
  title: string;
  description?: string;
  timestamp: number;
  end_timestamp?: number;
  speaker_label?: string;
  severity?: string;
  evidence_text?: string;
  entities?: string[];
  confidence?: number;
  is_flagged: boolean;
}

export interface RelationshipNode {
  id: string;
  label: string;
  type: string;
  confidence?: number;
  properties?: Record<string, unknown>;
}

export interface RelationshipEdge {
  id: string;
  source: string;
  target: string;
  relationship_type: string;
  confidence: number;
  evidence_text?: string;
  timestamp?: number;
}

export interface KnowledgeGraph {
  nodes: RelationshipNode[];
  edges: RelationshipEdge[];
  recording_id?: string;
  case_id?: string;
  generated_at: string;
}

// ============================================================
// Evidence & Chain of Custody
// ============================================================

export interface EvidenceFile {
  id: string;
  case_id: string;
  uploaded_by_id: string;
  recording_id?: string;
  evidence_type: string;
  original_filename: string;
  stored_filename: string;
  file_size_bytes: number;
  mime_type: string;
  sha256_hash: string;
  integrity_verified: boolean;
  integrity_last_checked?: string;
  evidence_version: number;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface CustodyEvent {
  id: string;
  evidence_file_id?: string;
  recording_id?: string;
  user_id: string;
  user?: User;
  action: string;
  reason?: string;
  ip_address?: string;
  device_info?: string;
  previous_state?: Record<string, unknown>;
  current_state?: Record<string, unknown>;
  created_at: string;
}

// ============================================================
// Reports
// ============================================================

export type ReportStatus = "draft" | "under_review" | "approved" | "rejected" | "archived";

export interface Report {
  id: string;
  case_id: string;
  recording_id?: string;
  created_by: string;
  creator?: User;
  report_type: string;
  title: string;
  description?: string;
  status: ReportStatus;
  approved_by_id?: string;
  approved_at?: string;
  content?: string;
  confidence?: number;
  model_used?: string;
  generation_time_seconds?: number;
  confidentiality_level: string;
  created_at: string;
  updated_at: string;
}

// ============================================================
// Audit Logs
// ============================================================

export interface AuditLog {
  id: string;
  user_id?: string;
  username?: string;
  user_role?: string;
  action: string;
  action_category: string;
  description?: string;
  severity: "info" | "warning" | "high" | "critical";
  resource_type?: string;
  resource_id?: string;
  resource_name?: string;
  case_id?: string;
  result: "success" | "failure" | "error";
  ip_address?: string;
  created_at: string;
}

// ============================================================
// Notifications
// ============================================================

export interface Notification {
  id: string;
  user_id: string;
  notification_type: string;
  title: string;
  message: string;
  icon?: string;
  severity: "info" | "warning" | "error" | "success";
  is_read: boolean;
  read_at?: string;
  is_archived: boolean;
  resource_type?: string;
  resource_id?: string;
  action_url?: string;
  created_at: string;
}

// ============================================================
// API Utilities
// ============================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ApiError {
  error: string;
  detail?: string;
  code?: string;
  request_id?: string;
}

// ============================================================
// Search
// ============================================================

export interface SearchResult {
  id: string;
  type: "case" | "recording" | "transcript" | "entity" | "threat" | "note";
  title: string;
  description?: string;
  case_id?: string;
  case_number?: string;
  relevance_score?: number;
  timestamp?: number;
  highlights?: string[];
}

// ============================================================
// Analytics
// ============================================================

export interface DashboardMetrics {
  total_cases: number;
  active_cases: number;
  closed_cases: number;
  total_recordings: number;
  total_evidence_files: number;
  pending_processing: number;
  threat_count: number;
  average_confidence: number;
  average_processing_time_seconds: number;
  active_users: number;
  recent_activity: RecentActivity[];
}

export interface RecentActivity {
  id: string;
  action: string;
  user: string;
  resource: string;
  case_id?: string;
  timestamp: string;
}

// ============================================================
// AI Copilot
// ============================================================

export interface CopilotMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  structured_response?: CopilotStructuredResponse;
  timestamp: string;
  model_used?: string;
  confidence?: number;
  evidence_references?: string[];
  status?: "thinking" | "searching" | "analyzing" | "generating" | "complete" | "error";
}

export interface CopilotStructuredResponse {
  summary?: string;
  findings?: CopilotFinding[];
  supporting_evidence?: string[];
  confidence: number;
  transcript_references?: TranscriptReference[];
  suggested_actions?: string[];
  insufficient_evidence?: boolean;
}

export interface CopilotFinding {
  title: string;
  content: string;
  severity?: string;
  confidence?: number;
}

export interface TranscriptReference {
  segment_id: string;
  timestamp: number;
  speaker_label?: string;
  text: string;
}

export interface CopilotContext {
  case_id?: string;
  recording_id?: string;
  transcript_id?: string;
  selected_segment_id?: string;
  selected_entity?: string;
  current_timestamp?: number;
}

// Processing Pipeline Stage
export interface ProcessingStage {
  name: string;
  label: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  duration_seconds?: number;
  confidence?: number;
  model_used?: string;
  error?: string;
}
