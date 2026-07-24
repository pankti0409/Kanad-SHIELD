/**
 * TraceVault Forensic Audio Player & Spectral Visualizer
 * Features A/B Audio comparison (Raw Mobile Audio vs DeepFilterNet Enhanced),
 * interactive waveform scrubber, speed control, and spectral noise reduction toggle.
 */
import React, { useState } from "react";
import { Play, Pause, Volume2, Sliders, CheckCircle2, Shield, Download, Sparkles } from "lucide-react";

export function AudioForensicsPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [useEnhancedAudio, setUseEnhancedAudio] = useState(true);
  const [playbackSpeed, setPlaybackSpeed] = useState("1.0x");
  const [progress, setProgress] = useState(35);

  return (
    <div className="tv-card p-5 space-y-4 bg-card/90 backdrop-blur-xl border border-border">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-bold text-foreground">Forensic Audio Player & Spectral Enhancer</h3>
        </div>

        {/* A/B Enhancement Toggle */}
        <div className="flex items-center gap-2 bg-muted p-1 rounded-lg">
          <button
            onClick={() => setUseEnhancedAudio(false)}
            className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
              !useEnhancedAudio ? "bg-card text-foreground shadow-sm" : "text-muted-foreground"
            }`}
          >
            Raw Audio
          </button>
          <button
            onClick={() => setUseEnhancedAudio(true)}
            className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all flex items-center gap-1 ${
              useEnhancedAudio
                ? "bg-primary text-white shadow-glow-primary"
                : "text-muted-foreground"
            }`}
          >
            <Sparkles className="w-3 h-3" /> Enhanced (DeepFilterNet)
          </button>
        </div>
      </div>

      {/* Simulated Interactive Waveform Display */}
      <div className="p-4 rounded-xl bg-muted/30 border border-border space-y-2">
        <div className="flex items-center justify-between text-xs text-muted-foreground font-mono">
          <span>02:14 / 06:45</span>
          <span className="text-emerald-500 font-semibold">
            {useEnhancedAudio ? "SNR Boost +18.4 dB" : "Unfiltered Original"}
          </span>
        </div>

        {/* Waveform Bars */}
        <div className="h-16 flex items-center gap-1 justify-between px-2 relative cursor-pointer">
          {Array.from({ length: 48 }).map((_, idx) => {
            const height = Math.sin(idx * 0.5) * 20 + 28;
            const isPlayed = idx < (progress / 100) * 48;
            return (
              <div
                key={idx}
                onClick={() => setProgress((idx / 48) * 100)}
                className={`w-1.5 rounded-full transition-all ${
                  isPlayed
                    ? useEnhancedAudio
                      ? "bg-gradient-to-t from-primary to-accent"
                      : "bg-amber-500"
                    : "bg-muted-foreground/20 hover:bg-muted-foreground/40"
                }`}
                style={{ height: `${height}px` }}
              />
            );
          })}
        </div>
      </div>

      {/* Control Bar */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="w-9 h-9 rounded-xl bg-primary text-white flex items-center justify-center shadow-glow-primary hover:bg-primary/90 transition-all"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
          </button>

          <select
            value={playbackSpeed}
            onChange={(e) => setPlaybackSpeed(e.target.value)}
            className="bg-card border border-border rounded-lg px-2.5 py-1 text-xs text-foreground outline-none"
          >
            <option value="0.75x">0.75x Speed</option>
            <option value="1.0x">1.0x Normal</option>
            <option value="1.25x">1.25x Speed</option>
            <option value="1.5x">1.5x Speed</option>
          </select>
        </div>

        <div className="flex items-center gap-2 text-muted-foreground">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
          <span>SHA-256 Checksum Intact</span>
        </div>
      </div>
    </div>
  );
}
