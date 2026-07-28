/**
 * TraceVault Top Header Bar
 * Search bar, active case selector, AI Copilot toggle, system status, notifications.
 */
import React from "react";
import { motion } from "framer-motion";
import {
  Search,
  Sparkles,
  Bell,
  Sun,
  Moon,
  Command,
  ShieldAlert,
  ChevronDown,
} from "lucide-react";
import { useUIStore } from "@/stores/uiStore";
import { useAuthStore } from "@/stores/authStore";
import { cn } from "@/lib/utils";

export function Header() {
  const {
    sidebarCollapsed,
    copilotOpen,
    toggleCopilot,
    theme,
    setTheme,
    setCommandPaletteOpen,
    unreadCount,
    activeCaseId,
  } = useUIStore();
  const { user } = useAuthStore();

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  return (
    <header
      className={cn(
        "h-14 border-b border-border bg-card/80 backdrop-blur-md sticky top-0 z-header flex items-center justify-between px-4 transition-all duration-200"
      )}
    >
      {/* Search & Active Case Context */}
      <div className="flex items-center gap-3 flex-1 max-w-xl">
        {/* Quick Search Button / Command Palette Trigger */}
        <button
          onClick={() => setCommandPaletteOpen(true)}
          className={cn(
            "flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs",
            "bg-muted/60 text-muted-foreground border border-border/60",
            "hover:bg-muted hover:text-foreground hover:border-border transition-all duration-150 flex-1 max-w-md"
          )}
        >
          <Search className="w-3.5 h-3.5 flex-shrink-0" />
          <span className="truncate">Search cases, transcripts, entities, threats...</span>
          <kbd className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] font-mono bg-background border border-border rounded text-muted-foreground ml-auto">
            <Command className="w-2.5 h-2.5" />K
          </kbd>
        </button>

        {activeCaseId && (
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 bg-primary/10 border border-primary/20 rounded-md text-xs font-medium text-primary">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
            <span className="truncate max-w-[120px]">Case: {activeCaseId.slice(0, 8)}</span>
          </div>
        )}
      </div>

      {/* Action Controls */}
      <div className="flex items-center gap-2">

        {/* AI Copilot Toggle */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={toggleCopilot}
          className={cn(
            "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150",
            copilotOpen
              ? "bg-gradient-to-r from-primary to-accent text-white shadow-glow-primary"
              : "bg-primary/10 text-primary hover:bg-primary/20 border border-primary/20"
          )}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">AI Copilot</span>
        </motion.button>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors duration-150"
          title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
        >
          {theme === "dark" ? (
            <Sun className="w-4 h-4" />
          ) : (
            <Moon className="w-4 h-4" />
          )}
        </button>

        {/* User Role Badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 bg-muted rounded-md text-xs font-medium text-muted-foreground">
          <span className="w-1.5 h-1.5 rounded-full bg-primary" />
          <span className="capitalize">{user?.role?.replace(/_/g, " ") || "Investigator"}</span>
        </div>
      </div>
    </header>
  );
}
