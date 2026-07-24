/**
 * TraceVault Settings Page
 * User profile, preferences, API configuration, security settings, and Log Out.
 */
import React, { useState } from "react";
import { motion } from "framer-motion";
import { User2, Bell, Shield, Key, Globe, Moon, Sun, Monitor, Save, CheckCircle2, LogOut, Sliders, Database, Cpu } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { useUIStore } from "@/stores/uiStore";
import { cn } from "@/lib/utils";

type Section = "profile" | "appearance" | "ai_pipeline" | "notifications" | "security";

export function SettingsPage() {
  const { user, logout } = useAuthStore();
  const { theme, setTheme } = useUIStore();
  const [activeSection, setActiveSection] = useState<Section>("profile");
  const [saved, setSaved] = useState(false);
  const navigate = useNavigate();

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const SECTIONS: { key: Section; label: string; icon: React.ElementType }[] = [
    { key: "profile", label: "Profile", icon: User2 },
    { key: "appearance", label: "Appearance", icon: Monitor },
    { key: "ai_pipeline", label: "AI & Whisper Model", icon: Cpu },
    { key: "notifications", label: "Notifications", icon: Bell },
    { key: "security", label: "Security & Evidence", icon: Shield },
  ];

  return (
    <div className="space-y-6">
      <div className="tv-page-header">
        <div>
          <h1 className="tv-page-title">Platform Settings</h1>
          <p className="tv-page-subtitle">Manage your agency profile, preferences, AI pipeline, and security configuration.</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleSave}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all",
              saved ? "bg-emerald-500 text-white" : "bg-primary text-white hover:bg-primary/90 shadow-glow-primary"
            )}
          >
            {saved ? <CheckCircle2 className="w-4 h-4" /> : <Save className="w-4 h-4" />}
            {saved ? "Saved!" : "Save Changes"}
          </button>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-red-500/10 text-red-500 hover:bg-red-500/20 border border-red-500/20 transition-all"
          >
            <LogOut className="w-4 h-4" />
            <span>Log Out</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar nav */}
        <div className="tv-card p-2 h-fit space-y-1">
          {SECTIONS.map((sec) => (
            <button
              key={sec.key}
              onClick={() => setActiveSection(sec.key)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors text-left",
                activeSection === sec.key
                  ? "bg-primary/10 text-primary font-bold"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
              )}
            >
              <sec.icon className="w-4 h-4 flex-shrink-0" />
              {sec.label}
            </button>
          ))}

          <div className="pt-3 mt-3 border-t border-border">
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-semibold text-red-500 hover:bg-red-500/10 transition-colors text-left"
            >
              <LogOut className="w-4 h-4 flex-shrink-0 text-red-500" />
              <span>Log Out Account</span>
            </button>
          </div>
        </div>

        {/* Main content */}
        <div className="lg:col-span-3">
          <motion.div key={activeSection} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="tv-card p-6 space-y-5">
            {activeSection === "profile" && (
              <>
                <h2 className="text-base font-semibold text-foreground">Officer & Agency Profile</h2>
                <div className="flex items-center gap-4 pb-4 border-b border-border">
                  <div className="w-14 h-14 bg-primary/20 rounded-full flex items-center justify-center text-xl font-bold text-primary">
                    {user?.full_name?.charAt(0)?.toUpperCase() || "U"}
                  </div>
                  <div className="space-y-0.5">
                    <div className="text-sm font-bold text-foreground">{user?.full_name || "Officer"}</div>
                    <div className="text-xs text-muted-foreground">{user?.email}</div>
                    <div className="inline-block tv-badge tv-badge-info capitalize text-[10px] mt-1">{user?.role?.replace(/_/g, " ")}</div>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { label: "Full Name", value: user?.full_name || "Pankti Patel" },
                    { label: "Email Address", value: user?.email || "investigator@agency.gov" },
                    { label: "Department / Agency", value: user?.department || "Law Enforcement & Intelligence" },
                    { label: "Designation", value: user?.designation || "Senior Officer" },
                    { label: "Organization", value: user?.organization || "Government Investigation Agency" },
                    { label: "Timezone", value: user?.timezone || "UTC (+05:30 IST)" },
                  ].map((field) => (
                    <div key={field.label} className="space-y-1">
                      <label className="text-xs font-semibold text-foreground">{field.label}</label>
                      <input defaultValue={field.value} className="tv-input" />
                    </div>
                  ))}
                </div>
              </>
            )}

            {activeSection === "appearance" && (
              <>
                <h2 className="text-base font-semibold text-foreground">Appearance Preferences</h2>
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-foreground">Interface Theme</label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { value: "light" as const, label: "Light", icon: Sun },
                      { value: "dark" as const, label: "Dark", icon: Moon },
                      { value: "system" as const, label: "System", icon: Monitor },
                    ].map((opt) => (
                      <button
                        key={opt.value}
                        onClick={() => setTheme(opt.value)}
                        className={cn(
                          "flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all",
                          theme === opt.value ? "border-primary bg-primary/5 shadow-glow-primary" : "border-border hover:border-primary/30"
                        )}
                      >
                        <opt.icon className={cn("w-5 h-5", theme === opt.value ? "text-primary" : "text-muted-foreground")} />
                        <span className={cn("text-xs font-medium", theme === opt.value ? "text-primary" : "text-muted-foreground")}>{opt.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-foreground">Primary Language</label>
                  <select className="tv-input">
                    <option>English (US / UK)</option>
                    <option>Hindi (हिंदी)</option>
                    <option>Gujarati (ગુજરાતી)</option>
                  </select>
                </div>
              </>
            )}

            {activeSection === "ai_pipeline" && (
              <>
                <h2 className="text-base font-semibold text-foreground">Speech & Intelligence Model Pipeline</h2>
                <div className="space-y-4">
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-foreground">Speech-to-Text Model Engine</label>
                    <select className="tv-input">
                      <option>Whisper Large v3 (Multilingual High Precision - Recommended)</option>
                      <option>Faster-Whisper Large v3 (GPU Accelerated)</option>
                      <option>Whisper Medium (Fast Batch Ingest)</option>
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-foreground">Auto-Diarization Sensitivity</label>
                    <select className="tv-input">
                      <option>High Precision (2-5 Speakers Auto-Segmented)</option>
                      <option>Standard Diarization</option>
                      <option>Single Speaker Mode</option>
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-foreground">Threat Classification Confidence Threshold</label>
                    <input type="range" min="50" max="95" defaultValue="80" className="w-full accent-primary" />
                    <div className="flex justify-between text-[11px] text-muted-foreground">
                      <span>50% (High Sensitivity)</span>
                      <span>80% (Recommended)</span>
                      <span>95% (Strict Evidence Only)</span>
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeSection === "notifications" && (
              <>
                <h2 className="text-base font-semibold text-foreground">Notification Preferences</h2>
                <div className="space-y-3">
                  {[
                    { label: "Critical threat alerts", description: "Immediately notify on critical threats detected in uploaded audios", enabled: true },
                    { label: "Case status updates", description: "When a case status or warrant changes", enabled: true },
                    { label: "Processing completed", description: "When Speech-to-Text and Diarization finishes", enabled: true },
                    { label: "Forensic report generated", description: "When a new PDF/Text investigation report is created", enabled: true },
                  ].map((notif) => (
                    <div key={notif.label} className="flex items-center justify-between p-3 rounded-xl border border-border bg-card/50">
                      <div>
                        <div className="text-sm font-medium text-foreground">{notif.label}</div>
                        <div className="text-xs text-muted-foreground">{notif.description}</div>
                      </div>
                      <div className={cn("w-10 h-5 rounded-full transition-colors cursor-pointer relative", notif.enabled ? "bg-primary" : "bg-muted")}>
                        <div className={cn("absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all", notif.enabled ? "left-5" : "left-0.5")} />
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}

            {activeSection === "security" && (
              <>
                <h2 className="text-base font-semibold text-foreground">Security & Evidence Integrity</h2>
                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800 flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 flex-shrink-0" />
                    <div>
                      <div className="text-sm font-semibold text-emerald-700 dark:text-emerald-400">Cryptographic Chain of Custody Active</div>
                      <div className="text-xs text-emerald-600/80 dark:text-emerald-500/80">Every uploaded recording is verified with direct SHA-256 evidence hashing.</div>
                    </div>
                  </div>
                  {[
                    { icon: Key, label: "Two-Factor Authentication (2FA)", description: "Enhance account security with TOTP / SMS 2FA", status: "Configured" },
                    { icon: Globe, label: "Active Sessions", description: "View and terminate active sessions", status: "1 active session" },
                    { icon: Shield, label: "Forensic Audit Log", description: "All evidence access events are immutably logged", status: "Audit active" },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between p-4 rounded-xl border border-border">
                      <div className="flex items-center gap-3">
                        <item.icon className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                        <div>
                          <div className="text-sm font-medium text-foreground">{item.label}</div>
                          <div className="text-xs text-muted-foreground">{item.description}</div>
                        </div>
                      </div>
                      <span className="text-xs font-semibold text-primary">{item.status}</span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}

