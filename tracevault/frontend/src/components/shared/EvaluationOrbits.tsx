/**
 * TraceVault Evaluation Orbits Component
 * Features:
 * - Soft pastel base ring colors
 * - Hover state: Ring highlights with vibrant soft pastel color pop
 * - Click state: Ring darkens, navigates, and STAYS DARKENED when returning to dashboard until another ring is clicked
 * - Curved text along SVG <textPath>
 */
import React, { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  Shield,
  FileText,
  Mic,
  Activity,
  AlertTriangle,
  Database,
  Users,
  Brain,
} from "lucide-react";
import { useUIStore } from "@/stores/uiStore";

export interface OrbitTier {
  id: string;
  label: string;
  subtitle: string;
  colorBase: string; // Subtle soft pastel
  colorHover: string; // Vibrant soft pastel highlight on hover
  colorActive: string; // Darkened persisted shade on click
  textColorDefault: string;
  textColorHover: string;
  textColorActive: string;
  radius: number; // arc radius in SVG units
  strokeWidth: number;
  icon: React.ElementType;
  route: string;
}

const ORBIT_TIERS: OrbitTier[] = [
  {
    id: "reports",
    label: "LEGAL REPORTS & FORENSIC AUDIT",
    subtitle: "Court-ready PDF exports & SHA-256 chain of custody",
    colorBase: "#dcfce7",
    colorHover: "#86efac",
    colorActive: "#15803d",
    textColorDefault: "#166534",
    textColorHover: "#052e16",
    textColorActive: "#ffffff",
    radius: 280,
    strokeWidth: 34,
    icon: FileText,
    route: "/reports",
  },
  {
    id: "transcription",
    label: "MULTILINGUAL SPEECH-TO-TEXT",
    subtitle: "Faster Whisper for Hindi, Gujarati & English calls",
    colorBase: "#e0f2fe",
    colorHover: "#7dd3fc",
    colorActive: "#0369a1",
    textColorDefault: "#075985",
    textColorHover: "#0c4a6e",
    textColorActive: "#ffffff",
    radius: 242,
    strokeWidth: 34,
    icon: Mic,
    route: "/transcripts",
  },
  {
    id: "noise_vad",
    label: "NOISE REDUCTION & VAD",
    subtitle: "DeepFilterNet enhancement & Silero VAD detection",
    colorBase: "#cff4fc",
    colorHover: "#67e8f9",
    colorActive: "#0891b2",
    textColorDefault: "#155e75",
    textColorHover: "#164e63",
    textColorActive: "#ffffff",
    radius: 204,
    strokeWidth: 34,
    icon: Activity,
    route: "/recordings",
  },
  {
    id: "threat_intel",
    label: "THREAT & SCAM INTELLIGENCE",
    subtitle: "Extortion, scam, fraud & violence detection",
    colorBase: "#f3e8ff",
    colorHover: "#d8b4fe",
    colorActive: "#7e22ce",
    textColorDefault: "#6b21a8",
    textColorHover: "#4c1d95",
    textColorActive: "#ffffff",
    radius: 166,
    strokeWidth: 34,
    icon: AlertTriangle,
    route: "/intelligence",
  },
  {
    id: "entity_ner",
    label: "NAMED ENTITY EXTRACTION",
    subtitle: "GLiNER for names, phones, bank accounts & locations",
    colorBase: "#fce7f3",
    colorHover: "#f9a8d4",
    colorActive: "#be185d",
    textColorDefault: "#9d174d",
    textColorHover: "#831843",
    textColorActive: "#ffffff",
    radius: 128,
    strokeWidth: 34,
    icon: Database,
    route: "/knowledge-graph",
  },
  {
    id: "diarization",
    label: "SPEAKER DIARIZATION",
    subtitle: "Pyannote voice attribution ('who said what')",
    colorBase: "#ffedd5",
    colorHover: "#fed7aa",
    colorActive: "#c2410c",
    textColorDefault: "#9a3412",
    textColorHover: "#7c2d12",
    textColorActive: "#ffffff",
    radius: 90,
    strokeWidth: 34,
    icon: Users,
    route: "/transcripts",
  },
  {
    id: "emotion_analytics",
    label: "VOICE STRESS & EMOTION",
    subtitle: "Anger, urgency & stress level analytics",
    colorBase: "#ffedd5",
    colorHover: "#f97316",
    colorActive: "#9a3412",
    textColorDefault: "#9a3412",
    textColorHover: "#ffffff",
    textColorActive: "#ffffff",
    radius: 52,
    strokeWidth: 34,
    icon: Brain,
    route: "/analytics",
  },
];

interface EvaluationOrbitsProps {
  onSelectTier?: (tier: OrbitTier) => void;
}

export function EvaluationOrbits({ onSelectTier }: EvaluationOrbitsProps) {
  const { activeOrbitTierId, setActiveOrbitTierId } = useUIStore();
  const [hoveredTierId, setHoveredTierId] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleTierClick = (tier: OrbitTier) => {
    // Persist darkened active ring state
    setActiveOrbitTierId(tier.id);
    if (onSelectTier) onSelectTier(tier);
    navigate(tier.route);
  };

  return (
    <div className="tv-card p-6 flex flex-col items-center justify-center relative overflow-hidden bg-card/90 backdrop-blur-xl">
      {/* Header */}
      <div className="text-center mb-4 max-w-md">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold mb-1">
          <Shield className="w-3.5 h-3.5" />
          <span>Interactive Navigation Orbits</span>
        </div>
        <h2 className="text-xl font-extrabold text-foreground tracking-tight">TraceVault Intelligence Orbits</h2>
        <p className="text-xs text-muted-foreground mt-0.5">
          Hover for soft pastel highlights • Click to navigate (clicked ring stays darkened)
        </p>
      </div>

      {/* SVG Arc Container with Curved TextPaths */}
      <div className="relative w-[640px] h-[350px] flex items-end justify-center overflow-hidden my-2">
        <svg viewBox="0 0 640 350" className="w-full h-full select-none">
          <defs>
            {ORBIT_TIERS.map((tier) => {
              const r = tier.radius;
              return (
                <path
                  key={`path-${tier.id}`}
                  id={`arc-${tier.id}`}
                  d={`M ${320 - r} 320 A ${r} ${r} 0 0 1 ${320 + r} 320`}
                />
              );
            })}
          </defs>

          {/* Render Arc Rings */}
          {ORBIT_TIERS.map((tier) => {
            const isHovered = hoveredTierId === tier.id;
            const isActive = activeOrbitTierId === tier.id;

            // Color selection logic:
            // Active/Clicked -> Darkened shade (persisted)
            // Hovered -> Soft Pastel highlight pop
            // Default -> Base soft pastel
            let strokeColor = tier.colorBase;
            if (isActive) strokeColor = tier.colorActive;
            else if (isHovered) strokeColor = tier.colorHover;

            let textColor = tier.textColorDefault;
            if (isActive) textColor = tier.textColorActive;
            else if (isHovered) textColor = tier.textColorHover;

            return (
              <g
                key={tier.id}
                onMouseEnter={() => setHoveredTierId(tier.id)}
                onMouseLeave={() => setHoveredTierId(null)}
                onClick={() => handleTierClick(tier)}
                className="cursor-pointer transition-all duration-200"
              >
                {/* Thick Arc Band */}
                <motion.path
                  d={`M ${320 - tier.radius} 320 A ${tier.radius} ${tier.radius} 0 0 1 ${320 + tier.radius} 320`}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={tier.strokeWidth}
                  strokeLinecap="butt"
                  animate={{
                    strokeWidth: isHovered ? tier.strokeWidth + 4 : tier.strokeWidth,
                  }}
                  transition={{ duration: 0.15 }}
                  className="filter drop-shadow-sm"
                />

                {/* Curved Text Following the Arc */}
                <text
                  fill={textColor}
                  fontSize={tier.radius < 70 ? "9" : "10"}
                  fontWeight="800"
                  className="tracking-wider uppercase font-sans pointer-events-none"
                  dy={tier.radius < 70 ? "3" : "4"}
                >
                  <textPath
                    href={`#arc-${tier.id}`}
                    startOffset="50%"
                    textAnchor="middle"
                  >
                    {tier.label}
                  </textPath>
                </text>
              </g>
            );
          })}

          {/* Central White TRACEVAULT AI Sphere */}
          <g transform="translate(320, 318)" className="cursor-pointer">
            <circle r="28" fill="#ffffff" stroke="#e2e8f0" strokeWidth="3" className="shadow-lg" />
            <text
              y="4"
              fill="#0f172a"
              fontSize="9"
              fontWeight="900"
              textAnchor="middle"
              className="select-none font-sans tracking-tight"
            >
              TRACEVAULT
            </text>
          </g>
        </svg>
      </div>

      {/* Tier Grid Legend Bar */}
      <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 w-full max-w-4xl">
        {ORBIT_TIERS.map((tier) => {
          const isActive = activeOrbitTierId === tier.id;
          const isHovered = hoveredTierId === tier.id;
          return (
            <button
              key={tier.id}
              onMouseEnter={() => setHoveredTierId(tier.id)}
              onMouseLeave={() => setHoveredTierId(null)}
              onClick={() => handleTierClick(tier)}
              className={`p-2.5 rounded-xl text-left border transition-all ${
                isActive
                  ? "bg-primary text-white border-primary shadow-glow-primary scale-105"
                  : isHovered
                  ? "bg-muted border-primary/40 text-foreground scale-102"
                  : "bg-muted/40 border-border text-foreground hover:bg-muted/70"
              }`}
            >
              <div className="flex items-center gap-1.5">
                <tier.icon className={`w-3.5 h-3.5 ${isActive ? "text-white" : "text-primary"}`} />
                <span className="text-[11px] font-bold truncate">{tier.label.split(" ")[0]}</span>
              </div>
              <p className={`text-[9px] truncate mt-0.5 ${isActive ? "text-white/80" : "text-muted-foreground"}`}>
                {tier.subtitle}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
