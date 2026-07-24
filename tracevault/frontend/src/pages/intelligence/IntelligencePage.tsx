/**
 * TraceVault AI Intelligence Page
 * Displays extracted entities, threat indicators, speaker analysis, and emotion analytics.
 */
import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Brain,
  ShieldAlert,
  User2,
  Phone,
  MapPin,
  DollarSign,
  AlertTriangle,
  TrendingUp,
  Filter,
} from "lucide-react";
import { cn } from "@/lib/utils";

const ENTITIES = [
  { type: "PERSON", value: "Ajay Mehta (alias: Blackbird)", confidence: 0.97, case: "TV-8839-FRD", segment: "02:14" },
  { type: "PHONE", value: "+91-98201-XXXXX", confidence: 0.99, case: "TV-8839-FRD", segment: "03:55" },
  { type: "ACCOUNT", value: "Zurich Offshore 8820-X", confidence: 0.94, case: "TV-4012-EXT", segment: "07:32" },
  { type: "LOCATION", value: "Surat, Gujarat — Collection Point", confidence: 0.91, case: "TV-4012-EXT", segment: "11:08" },
  { type: "MONETARY", value: "Rs 4,50,000 (transfer ref: BT-9912)", confidence: 0.96, case: "TV-8839-FRD", segment: "15:22" },
  { type: "PERSON", value: "Priya Desai (suspect 2)", confidence: 0.88, case: "TV-1092-ORG", segment: "04:40" },
  { type: "PHONE", value: "+91-90303-XXXXX (burner)", confidence: 0.99, case: "TV-1092-ORG", segment: "08:19" },
  { type: "ACCOUNT", value: "Dubai IBAN AE-77042-...", confidence: 0.89, case: "TV-8839-FRD", segment: "18:07" },
];

const THREATS = [
  { category: "extortion", severity: "critical", evidence: "Destroy the burner SIM immediately after transfer", case: "TV-4012-EXT", confidence: 0.98, timestamp: "07:44" },
  { category: "financial_fraud", severity: "high", evidence: "Transfer Rs 4.5L to the Zurich account before EOD", case: "TV-8839-FRD", confidence: 0.96, timestamp: "15:28" },
  { category: "coordination", severity: "high", evidence: "Meet at the collection point in Surat, no phones", case: "TV-4012-EXT", confidence: 0.91, timestamp: "11:14" },
  { category: "violence", severity: "medium", evidence: "Yeh kaam kal tak ho jaana chahiye, samjhe?", case: "TV-1092-ORG", confidence: 0.82, timestamp: "06:55" },
];

const SPEAKERS = [
  { label: "Speaker_01", voiceStress: 0.78, emotion: "Agitated", turns: 14, duration: "4m 22s", color: "#6366f1" },
  { label: "Speaker_02", voiceStress: 0.42, emotion: "Calm / Authoritative", turns: 9, duration: "2m 51s", color: "#10b981" },
  { label: "Speaker_03", voiceStress: 0.89, emotion: "Fearful / Urgent", turns: 6, duration: "1m 14s", color: "#f59e0b" },
];

const ENTITY_ICONS: Record<string, React.ElementType> = {
  PERSON: User2,
  PHONE: Phone,
  LOCATION: MapPin,
  MONETARY: DollarSign,
  ACCOUNT: DollarSign,
};

const ENTITY_COLORS: Record<string, string> = {
  PERSON: "bg-indigo-100 text-indigo-700 border-indigo-200 dark:bg-indigo-950/50 dark:text-indigo-400 dark:border-indigo-800",
  PHONE: "bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-400 dark:border-emerald-800",
  LOCATION: "bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-950/50 dark:text-orange-400 dark:border-orange-800",
  MONETARY: "bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-950/50 dark:text-yellow-400 dark:border-yellow-800",
  ACCOUNT: "bg-red-100 text-red-700 border-red-200 dark:bg-red-950/50 dark:text-red-400 dark:border-red-800",
};

const SEVERITY_CLASSES: Record<string, string> = {
  critical: "border-l-red-500 bg-red-50 dark:bg-red-950/20",
  high: "border-l-orange-500 bg-orange-50 dark:bg-orange-950/20",
  medium: "border-l-yellow-500 bg-yellow-50 dark:bg-yellow-950/20",
  low: "border-l-green-500 bg-green-50 dark:bg-green-950/20",
};

const THREAT_BADGE: Record<string, string> = {
  extortion: "tv-badge-critical",
  financial_fraud: "tv-badge-high",
  coordination: "tv-badge-medium",
  violence: "tv-badge-high",
};

type Tab = "entities" | "threats" | "speakers";

export function IntelligencePage() {
  const [activeTab, setActiveTab] = useState<Tab>("entities");
  const [entityFilter, setEntityFilter] = useState("ALL");
  const entityTypes = ["ALL", "PERSON", "PHONE", "ACCOUNT", "LOCATION", "MONETARY"];
  const filteredEntities = entityFilter === "ALL" ? ENTITIES : ENTITIES.filter((e) => e.type === entityFilter);

  return (
    <div className="space-y-6">
      <div className="tv-page-header">
        <div>
          <h1 className="tv-page-title">AI Intelligence Analysis</h1>
          <p className="tv-page-subtitle">Extracted entities, threat indicators, and speaker profiling across all active intercepts.</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20">
            <span className="tv-status-dot-active" />
            <span className="text-xs font-semibold text-red-600 dark:text-red-400">
              {THREATS.filter((t) => t.severity === "critical").length} Critical Alerts
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Entities Extracted", value: String(ENTITIES.length), icon: Brain, color: "text-primary" },
          { label: "Threat Indicators", value: String(THREATS.length), icon: ShieldAlert, color: "text-red-500" },
          { label: "Speaker Profiles", value: String(SPEAKERS.length), icon: User2, color: "text-indigo-500" },
          { label: "Avg Confidence", value: `${Math.round(ENTITIES.reduce((a, e) => a + e.confidence, 0) / ENTITIES.length * 100)}%`, icon: TrendingUp, color: "text-emerald-500" },
        ].map((stat) => (
          <motion.div key={stat.label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="tv-card p-4 flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
              <stat.icon className={cn("w-4 h-4", stat.color)} />
            </div>
            <div>
              <div className="text-xl font-bold text-foreground">{stat.value}</div>
              <div className="text-xs text-muted-foreground">{stat.label}</div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="tv-card overflow-hidden">
        <div className="flex border-b border-border">
          {(["entities", "threats", "speakers"] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                "flex-1 py-3 text-xs font-semibold capitalize tracking-wide transition-colors",
                activeTab === tab ? "text-primary border-b-2 border-primary bg-primary/5" : "text-muted-foreground hover:text-foreground"
              )}
            >
              {tab === "entities" && `Entities (${ENTITIES.length})`}
              {tab === "threats" && `Threats (${THREATS.length})`}
              {tab === "speakers" && `Speakers (${SPEAKERS.length})`}
            </button>
          ))}
        </div>

        <div className="p-5">
          {activeTab === "entities" && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 flex-wrap">
                <Filter className="w-3.5 h-3.5 text-muted-foreground" />
                {entityTypes.map((type) => (
                  <button key={type} onClick={() => setEntityFilter(type)}
                    className={cn("px-2.5 py-1 rounded-md text-xs font-medium border transition-colors",
                      entityFilter === type ? "bg-primary text-white border-primary" : "bg-muted/50 text-muted-foreground border-border hover:border-primary/40")}
                  >{type}</button>
                ))}
              </div>
              <div className="space-y-2">
                {filteredEntities.map((entity, i) => {
                  const Icon = ENTITY_ICONS[entity.type] || Brain;
                  return (
                    <motion.div key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.04 }}
                      className="flex items-center gap-3 p-3 rounded-xl border border-border bg-card/60 hover:bg-muted/30 transition-colors">
                      <div className={cn("w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 border", ENTITY_COLORS[entity.type])}>
                        <Icon className="w-3.5 h-3.5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-semibold text-foreground truncate">{entity.value}</div>
                        <div className="text-xs text-muted-foreground">{entity.case} · Segment {entity.segment}</div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <div className="text-right">
                          <div className="text-xs font-bold text-foreground">{Math.round(entity.confidence * 100)}%</div>
                          <div className="text-[10px] text-muted-foreground">confidence</div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          )}

          {activeTab === "threats" && (
            <div className="space-y-3">
              {THREATS.map((threat, i) => (
                <motion.div key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.06 }}
                  className={cn("tv-card p-4 border-l-4", SEVERITY_CLASSES[threat.severity])}>
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0" />
                      <span className={cn("tv-badge text-[10px]", THREAT_BADGE[threat.category])}>{threat.category.replace("_", " ").toUpperCase()}</span>
                      <span className="text-xs text-muted-foreground">{threat.case} · {threat.timestamp}</span>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <div className="text-sm font-bold text-foreground">{Math.round(threat.confidence * 100)}%</div>
                      <div className="text-[10px] text-muted-foreground">confidence</div>
                    </div>
                  </div>
                  <blockquote className="mt-2 text-sm text-foreground italic border-l-2 border-border pl-3">"{threat.evidence}"</blockquote>
                </motion.div>
              ))}
            </div>
          )}

          {activeTab === "speakers" && (
            <div className="space-y-4">
              {SPEAKERS.map((speaker, i) => (
                <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }} className="tv-card p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold" style={{ backgroundColor: speaker.color }}>
                        {speaker.label.split("_")[1]}
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-foreground">{speaker.label}</div>
                        <div className="text-xs text-muted-foreground">{speaker.turns} turns · {speaker.duration}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-foreground">{speaker.emotion}</div>
                      <div className="text-xs text-muted-foreground">Primary Emotion</div>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Voice Stress Index</span>
                      <span className={cn("font-bold", speaker.voiceStress > 0.75 ? "text-red-500" : speaker.voiceStress > 0.5 ? "text-orange-500" : "text-emerald-500")}>
                        {Math.round(speaker.voiceStress * 100)}%
                      </span>
                    </div>
                    <div className="tv-confidence-bar">
                      <div className={cn("tv-confidence-fill", speaker.voiceStress > 0.75 ? "bg-red-500" : speaker.voiceStress > 0.5 ? "bg-orange-500" : "bg-emerald-500")}
                        style={{ width: `${speaker.voiceStress * 100}%` }} />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
