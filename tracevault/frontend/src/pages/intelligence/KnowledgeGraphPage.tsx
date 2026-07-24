/**
 * TraceVault Entity Knowledge Graph & Network Visualizer
 * Interactive network graph connecting suspects, phone numbers, offshore accounts, aliases, and evidence calls.
 */
import React, { useState } from "react";
import { motion } from "framer-motion";
import { Network, Search, Filter, ShieldAlert, User, Phone, DollarSign, MapPin, ZoomIn, ZoomOut, RefreshCw, ExternalLink } from "lucide-react";

interface Node {
  id: string;
  label: string;
  type: "person" | "phone" | "account" | "location" | "call";
  x: number;
  y: number;
  threatLevel?: "critical" | "high" | "medium";
}

interface Edge {
  source: string;
  target: string;
  relationship: string;
}

const NODES: Node[] = [
  { id: "n1", label: "Suspect Alpha (Blackbird)", type: "person", x: 250, y: 150, threatLevel: "critical" },
  { id: "n2", label: "+1-555-0192 (VoIP)", type: "phone", x: 450, y: 120, threatLevel: "high" },
  { id: "n3", label: "Zurich Account 8820-X", type: "account", x: 220, y: 320, threatLevel: "critical" },
  { id: "n4", label: "Co-conspirator (Bravo)", type: "person", x: 550, y: 300, threatLevel: "high" },
  { id: "n5", label: "INTERCEPT_CALL_042.wav", type: "call", x: 380, y: 220, threatLevel: "medium" },
  { id: "n6", label: "Panama Shell Corp", type: "account", x: 620, y: 180, threatLevel: "high" },
];

const EDGES: Edge[] = [
  { source: "n1", target: "n2", relationship: "Used Phone" },
  { source: "n1", target: "n5", relationship: "Speaker in Call" },
  { source: "n2", target: "n5", relationship: "Originating Line" },
  { source: "n4", target: "n5", relationship: "Receiving Speaker" },
  { source: "n1", target: "n3", relationship: "Beneficiary" },
  { source: "n4", target: "n6", relationship: "Director" },
];

export function KnowledgeGraphPage() {
  const [selectedNode, setSelectedNode] = useState<Node | null>(NODES[0]);
  const [searchTerm, setSearchTerm] = useState("");

  const getNodeIcon = (type: Node["type"]) => {
    switch (type) {
      case "person": return <User className="w-4 h-4 text-indigo-400" />;
      case "phone": return <Phone className="w-4 h-4 text-emerald-400" />;
      case "account": return <DollarSign className="w-4 h-4 text-amber-400" />;
      case "call": return <Network className="w-4 h-4 text-sky-400" />;
      default: return <MapPin className="w-4 h-4 text-purple-400" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="tv-page-header">
        <div>
          <h1 className="tv-page-title">Entity Knowledge Graph</h1>
          <p className="tv-page-subtitle">
            Interactive multi-layered relationship network mapping suspects, communication channels, and financial entities.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded-lg text-xs font-semibold border border-border flex items-center gap-1.5">
            <RefreshCw className="w-3.5 h-3.5" /> Re-layout Graph
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Canvas Area (3 Cols) */}
        <div className="lg:col-span-3 tv-card p-4 h-[520px] relative overflow-hidden bg-card/60 backdrop-blur-md flex flex-col justify-between">
          <div className="flex items-center justify-between z-10">
            <div className="flex items-center gap-2 bg-muted/60 border border-border rounded-lg px-3 py-1.5 w-72">
              <Search className="w-3.5 h-3.5 text-muted-foreground" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search entities or relationships..."
                className="w-full bg-transparent text-xs text-foreground placeholder:text-muted-foreground outline-none"
              />
            </div>
            <div className="flex items-center gap-1 bg-muted/60 border border-border rounded-lg p-1">
              <button className="p-1.5 hover:bg-muted rounded text-muted-foreground hover:text-foreground">
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
              <button className="p-1.5 hover:bg-muted rounded text-muted-foreground hover:text-foreground">
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* SVG Canvas Network Rendering */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {EDGES.map((edge, idx) => {
              const srcNode = NODES.find((n) => n.id === edge.source);
              const tgtNode = NODES.find((n) => n.id === edge.target);
              if (!srcNode || !tgtNode) return null;
              return (
                <g key={idx}>
                  <line
                    x1={srcNode.x}
                    y1={srcNode.y}
                    x2={tgtNode.x}
                    y2={tgtNode.y}
                    stroke="currentColor"
                    className="text-border"
                    strokeWidth="1.5"
                    strokeDasharray="4 2"
                  />
                  <text
                    x={(srcNode.x + tgtNode.x) / 2}
                    y={(srcNode.y + tgtNode.y) / 2 - 5}
                    fill="currentColor"
                    className="text-[9px] text-muted-foreground font-mono"
                    textAnchor="middle"
                  >
                    {edge.relationship}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Interactive Nodes */}
          <div className="relative w-full h-full">
            {NODES.map((node) => {
              const isSelected = selectedNode?.id === node.id;
              return (
                <motion.div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  style={{ left: node.x - 60, top: node.y - 20 }}
                  whileHover={{ scale: 1.05 }}
                  className={`absolute px-3 py-2 rounded-xl border cursor-pointer transition-all flex items-center gap-2 shadow-md ${
                    isSelected
                      ? "bg-primary text-white border-primary shadow-glow-primary z-20"
                      : "bg-card border-border hover:border-primary/40 z-10"
                  }`}
                >
                  {getNodeIcon(node.type)}
                  <span className="text-xs font-semibold truncate max-w-[120px]">{node.label}</span>
                </motion.div>
              );
            })}
          </div>

          <div className="flex items-center gap-4 text-[11px] text-muted-foreground z-10 pt-2 border-t border-border">
            <span className="flex items-center gap-1"><User className="w-3 h-3 text-indigo-400" /> Suspect</span>
            <span className="flex items-center gap-1"><Phone className="w-3 h-3 text-emerald-400" /> Phone</span>
            <span className="flex items-center gap-1"><DollarSign className="w-3 h-3 text-amber-400" /> Account</span>
            <span className="flex items-center gap-1"><Network className="w-3 h-3 text-sky-400" /> Intercept</span>
          </div>
        </div>

        {/* Selected Entity Intelligence Breakdown (1 Col) */}
        <div className="space-y-4">
          {selectedNode ? (
            <div className="tv-card p-5 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-border">
                <div className="flex items-center gap-2">
                  {getNodeIcon(selectedNode.type)}
                  <div>
                    <h3 className="text-sm font-bold text-foreground">{selectedNode.label}</h3>
                    <span className="text-[10px] text-muted-foreground capitalize">{selectedNode.type} Entity</span>
                  </div>
                </div>
                {selectedNode.threatLevel && (
                  <span className="tv-badge-critical uppercase text-[10px]">{selectedNode.threatLevel}</span>
                )}
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-border/40">
                  <span className="text-muted-foreground">Entity ID</span>
                  <span className="font-mono text-foreground">{selectedNode.id}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-border/40">
                  <span className="text-muted-foreground">Connected Degree</span>
                  <span className="font-semibold text-foreground">
                    {EDGES.filter((e) => e.source === selectedNode.id || e.target === selectedNode.id).length} edges
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-border/40">
                  <span className="text-muted-foreground">Vector Confidence</span>
                  <span className="text-emerald-500 font-semibold">97.8%</span>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-primary/10 border border-primary/20 space-y-1">
                <h4 className="text-xs font-semibold text-primary">Cross-Case Intelligence</h4>
                <p className="text-[11px] text-muted-foreground">
                  Identified in 3 distinct intercept recordings across Case #TV-2026-0091 and Case #TV-2026-0084.
                </p>
              </div>
            </div>
          ) : (
            <div className="tv-card p-5 text-center text-xs text-muted-foreground">
              Select a node to inspect entity intelligence details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
