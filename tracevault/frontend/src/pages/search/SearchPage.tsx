/**
 * TraceVault Search Page
 * Full-text search across cases, recordings, transcripts, and entities.
 */
import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, FolderOpen, Mic, FileText, Brain, X, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

const DEMO_RESULTS = [
  { type: "case", title: "Operation Iron Vault - Financial Scam Ring", subtitle: "TV-8839-FRD · Critical · 14 recordings", href: "/cases" },
  { type: "recording", title: "Intercept_Session_2024_11_22_07h30.wav", subtitle: "TV-8839-FRD · Duration 18:44 · SHA-256 verified", href: "/recordings" },
  { type: "transcript", title: "Transcript: Zurich offshore account transfer instructions", subtitle: "Speaker_01 · Confidence 96% · 15:22", href: "/transcripts" },
  { type: "entity", title: "Ajay Mehta (alias: Blackbird)", subtitle: "PERSON · TV-8839-FRD · Confidence 97%", href: "/intelligence" },
  { type: "case", title: "Extortion Investigation - Call Center Cyber Ring", subtitle: "TV-4012-EXT · High · 8 recordings", href: "/cases" },
  { type: "entity", title: "Zurich Offshore 8820-X", subtitle: "ACCOUNT · TV-4012-EXT · Confidence 94%", href: "/intelligence" },
];

const TYPE_ICON: Record<string, React.ElementType> = {
  case: FolderOpen,
  recording: Mic,
  transcript: FileText,
  entity: Brain,
};

const TYPE_BADGE: Record<string, string> = {
  case: "tv-badge-info",
  recording: "tv-badge-neutral",
  transcript: "tv-badge-medium",
  entity: "tv-badge-processing",
};

const SUGGESTIONS = ["Ajay Mehta", "Zurich offshore", "burner SIM", "extortion", "TV-8839-FRD", "transfer"];

export function SearchPage() {
  const [query, setQuery] = useState("");
  const [searched, setSearched] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const results = searched && query.trim()
    ? DEMO_RESULTS.filter((r) =>
        r.title.toLowerCase().includes(query.toLowerCase()) ||
        r.subtitle.toLowerCase().includes(query.toLowerCase())
      )
    : [];

  const handleSearch = (q: string) => {
    setQuery(q);
    setSearched(true);
  };

  return (
    <div className="space-y-6">
      <div className="tv-page-header">
        <div>
          <h1 className="tv-page-title">Search Intelligence</h1>
          <p className="tv-page-subtitle">Full-text search across cases, recordings, transcripts, and extracted entities.</p>
        </div>
      </div>

      {/* Search Input */}
      <div className="tv-card p-4">
        <div className="flex items-center gap-3">
          <Search className="w-5 h-5 text-muted-foreground flex-shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch(query)}
            placeholder="Search cases, recordings, transcripts, suspects, account numbers..."
            className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
            autoFocus
          />
          {query && (
            <button onClick={() => { setQuery(""); setSearched(false); }} className="text-muted-foreground hover:text-foreground transition-colors">
              <X className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={() => handleSearch(query)}
            className="px-4 py-1.5 bg-primary text-white text-xs font-semibold rounded-lg hover:bg-primary/90 transition-colors"
          >
            Search
          </button>
        </div>

        {/* Quick suggestions */}
        {!searched && (
          <div className="mt-3 pt-3 border-t border-border flex items-center gap-2 flex-wrap">
            <span className="text-xs text-muted-foreground">Try:</span>
            {SUGGESTIONS.map((s) => (
              <button key={s} onClick={() => handleSearch(s)}
                className="px-2.5 py-1 rounded-full bg-muted/60 text-xs text-muted-foreground hover:text-foreground hover:bg-muted transition-colors border border-border">
                {s}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Results */}
      <AnimatePresence>
        {searched && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground font-medium">
                {results.length > 0 ? `${results.length} result${results.length !== 1 ? "s" : ""} for "${query}"` : `No results found for "${query}"`}
              </span>
            </div>

            {results.length === 0 && (
              <div className="tv-empty-state">
                <div className="tv-empty-state-icon"><Search className="w-7 h-7 text-muted-foreground" /></div>
                <div className="tv-empty-state-title">No results found</div>
                <div className="tv-empty-state-description">Try different keywords, a case number, suspect name, or account reference.</div>
              </div>
            )}

            {results.map((result, i) => {
              const Icon = TYPE_ICON[result.type];
              return (
                <motion.div key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}>
                  <Link to={result.href}>
                    <div className="tv-card-hover p-4 flex items-center gap-4 cursor-pointer group">
                      <div className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
                        <Icon className="w-4 h-4 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-semibold text-foreground truncate group-hover:text-primary transition-colors">{result.title}</div>
                        <div className="text-xs text-muted-foreground truncate">{result.subtitle}</div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className={cn("tv-badge text-[10px] capitalize", TYPE_BADGE[result.type])}>{result.type}</span>
                        <ArrowRight className="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary transition-colors" />
                      </div>
                    </div>
                  </Link>
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>

      {!searched && (
        <div className="tv-empty-state">
          <div className="tv-empty-state-icon"><Search className="w-7 h-7 text-muted-foreground" /></div>
          <div className="tv-empty-state-title">Search TraceVault</div>
          <div className="tv-empty-state-description">Enter a search query above to find cases, recordings, transcripts, entities, and persons of interest.</div>
        </div>
      )}
    </div>
  );
}
