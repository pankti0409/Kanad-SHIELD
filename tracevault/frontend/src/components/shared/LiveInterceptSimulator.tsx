/**
 * TraceVault Live Audio Stream Intercept Simulator
 * Real-time streaming transcription, emotion meter, and instant threat alert triggers.
 */
import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Activity, Mic, ShieldAlert, Sparkles, Volume2, Pause, Play, Download, Clock } from "lucide-react";

export function LiveInterceptSimulator() {
  const [isLive, setIsLive] = useState(true);
  const [streamIndex, setStreamIndex] = useState(0);

  const STREAM_EVENTS = [
    { time: "00:02", text: "Phone line connected. Language detected: Hindi / English.", speaker: "System", type: "info" },
    { time: "00:05", text: "Speaker_01: 'हां, कल शाम 8 बजे डिलीवरी पक्की है।' (Yes, delivery is confirmed for 8 PM tomorrow.)", speaker: "Speaker 1", type: "normal" },
    { time: "00:12", text: "Speaker_02: 'खाते में 45 लाख रुपये ट्रांसफर हो गए हैं।' (45 Lakh Rupees transferred to Zurich account 8820-X.)", speaker: "Speaker 2", type: "threat" },
    { time: "00:18", text: "Speaker_01: 'बर्नर सिम तुरंत नष्ट कर देना।' (Destroy the burner SIM immediately after verification.)", speaker: "Speaker 1", type: "critical" },
  ];

  useEffect(() => {
    if (!isLive) return;
    const interval = setInterval(() => {
      setStreamIndex((prev) => (prev < STREAM_EVENTS.length - 1 ? prev + 1 : prev));
    }, 3000);
    return () => clearInterval(interval);
  }, [isLive]);

  return (
    <div className="tv-card p-5 space-y-4 bg-card/90 backdrop-blur-xl border border-border">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />
          <h3 className="text-sm font-bold text-foreground">Live Call Intercept Stream</h3>
          <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-primary/10 text-primary">
            LINE #INT-8812
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsLive(!isLive)}
            className="px-2.5 py-1 bg-muted hover:bg-muted/80 text-foreground rounded-md text-xs font-semibold flex items-center gap-1.5"
          >
            {isLive ? <Pause className="w-3 h-3 text-amber-500" /> : <Play className="w-3 h-3 text-emerald-500" />}
            <span>{isLive ? "Pause Stream" : "Resume Stream"}</span>
          </button>
        </div>
      </div>

      {/* Simulated Equalizer Wave Animation */}
      <div className="p-3 rounded-xl bg-muted/40 border border-border flex items-center justify-between gap-2">
        <div className="flex items-center gap-1 h-6">
          <span className="tv-wave-bar h-4" />
          <span className="tv-wave-bar h-6" />
          <span className="tv-wave-bar h-3" />
          <span className="tv-wave-bar h-5" />
          <span className="tv-wave-bar h-6" />
          <span className="tv-wave-bar h-4" />
          <span className="tv-wave-bar h-2" />
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="text-emerald-500 font-semibold">98.4% STT Accuracy</span>
          <span className="text-muted-foreground">DeepFilterNet Enhanced</span>
          <span className="text-indigo-400 font-bold">Hindi • English</span>
        </div>
      </div>

      {/* Real-time Streaming Transcript Feed */}
      <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
        {STREAM_EVENTS.slice(0, streamIndex + 1).map((ev, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className={`p-2.5 rounded-lg text-xs flex items-start gap-2 border ${
              ev.type === "critical"
                ? "bg-red-500/10 border-red-500/20 text-foreground"
                : ev.type === "threat"
                ? "bg-amber-500/10 border-amber-500/20 text-foreground"
                : "bg-muted/30 border-border text-foreground"
            }`}
          >
            <span className="font-mono text-[10px] text-muted-foreground mt-0.5">{ev.time}</span>
            <div className="flex-1">
              <span className="font-bold text-primary mr-1.5">{ev.speaker}:</span>
              <span>{ev.text}</span>
            </div>
            {ev.type === "critical" && (
              <span className="tv-badge-critical text-[9px] flex items-center gap-0.5">
                <ShieldAlert className="w-2.5 h-2.5" /> Threat Trigger
              </span>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
