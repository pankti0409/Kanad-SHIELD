import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  FolderOpen,
  Mic,
  FileText,
  Brain,
  Network,
  Search,
  FileBarChart2,
  BarChart3,
  Settings,
  Bell,
  ChevronLeft,
  ChevronRight,
  Lock,
  Shield,
  User,
  LogOut,
} from "lucide-react";
import { useUIStore } from "@/stores/uiStore";
import { useAuthStore } from "@/stores/authStore";
import { cn } from "@/lib/utils";

// ============================================================
// Navigation Configuration
// ============================================================

const NAV_SECTIONS = [
  {
    title: "Workspace",
    items: [
      { icon: LayoutDashboard, label: "Dashboard", href: "/" },
      { icon: FolderOpen, label: "Cases", href: "/cases" },
      { icon: Search, label: "Search", href: "/search" },
    ],
  },
  {
    title: "Evidence",
    items: [
      { icon: Mic, label: "Recordings", href: "/recordings" },
      { icon: FileText, label: "Transcripts", href: "/transcripts" },
    ],
  },
  {
    title: "Intelligence",
    items: [
      { icon: Brain, label: "AI Analysis", href: "/intelligence" },
      { icon: Network, label: "Knowledge Graph", href: "/knowledge-graph" },
    ],
  },
  {
    title: "Reports",
    items: [
      { icon: FileBarChart2, label: "Reports", href: "/reports" },
      { icon: BarChart3, label: "Analytics", href: "/analytics" },
    ],
  },
  {
    title: "System",
    items: [
      { icon: Lock, label: "Audit Log", href: "/audit" },
      { icon: Settings, label: "Settings", href: "/settings" },
    ],
  },
];


// ============================================================
// Sidebar Component
// ============================================================

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useUIStore();
  const { user, logout } = useAuthStore();
  const location = useLocation();
  const navigate = useNavigate();
  const [notifCount] = React.useState(3);

  const isActive = (href: string) => {
    if (href === "/") return location.pathname === "/";
    return location.pathname.startsWith(href);
  };

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <motion.aside
      className="fixed left-0 top-0 h-screen bg-sidebar border-r border-sidebar-border flex flex-col overflow-hidden z-sidebar"
      animate={{ width: sidebarCollapsed ? 60 : 260 }}
      transition={{ duration: 0.25, ease: "easeInOut" }}
    >
      {/* Header */}
      <div className="flex items-center px-3 h-14 border-b border-sidebar-border flex-shrink-0">
        <AnimatePresence mode="wait">
          {!sidebarCollapsed ? (
            <motion.div
              key="logo-full"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="flex items-center gap-2.5 flex-1 overflow-hidden"
            >
              <div className="w-7 h-7 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center flex-shrink-0">
                <Shield className="w-4 h-4 text-white" />
              </div>
              <div className="overflow-hidden">
                <div className="text-sm font-bold text-sidebar-foreground tracking-tight leading-none">
                  TraceVault
                </div>
                <div className="text-[10px] text-sidebar-foreground/40 font-medium tracking-wide mt-0.5">
                  INVESTIGATION PLATFORM
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="logo-compact"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center justify-center w-full"
            >
              <div className="w-7 h-7 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
                <Shield className="w-4 h-4 text-white" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <button
          onClick={toggleSidebar}
          className={cn(
            "flex-shrink-0 w-6 h-6 rounded-md flex items-center justify-center",
            "text-sidebar-foreground/40 hover:text-sidebar-foreground hover:bg-sidebar-border/50",
            "transition-colors duration-150",
            sidebarCollapsed && "absolute right-2"
          )}
        >
          {sidebarCollapsed ? (
            <ChevronRight className="w-3.5 h-3.5" />
          ) : (
            <ChevronLeft className="w-3.5 h-3.5" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto py-2 scrollbar-hide">
        {NAV_SECTIONS.map((section) => (
          <div key={section.title} className="mb-1">
            {!sidebarCollapsed && (
              <div className="tv-sidebar-section">
                <span className="tv-sidebar-section-title">{section.title}</span>
              </div>
            )}

            {section.items.map((item) => {
              const active = isActive(item.href);
              return (
                <Link key={item.href} to={item.href}>
                  <motion.div
                    className={cn(
                      "tv-nav-item mx-1.5 my-0.5 relative",
                      active && "tv-nav-item-active",
                      sidebarCollapsed && "justify-center px-2"
                    )}
                    whileHover={{ x: sidebarCollapsed ? 0 : 2 }}
                    transition={{ duration: 0.1 }}
                  >
                    <item.icon
                      className={cn(
                        "w-4 h-4 flex-shrink-0",
                        active
                          ? "text-sidebar-accent-foreground"
                          : "text-sidebar-foreground/60"
                      )}
                    />
                    <AnimatePresence>
                      {!sidebarCollapsed && (
                        <motion.span
                          initial={{ opacity: 0, width: 0 }}
                          animate={{ opacity: 1, width: "auto" }}
                          exit={{ opacity: 0, width: 0 }}
                          className="text-sm font-medium overflow-hidden whitespace-nowrap"
                        >
                          {item.label}
                        </motion.span>
                      )}
                    </AnimatePresence>

                    {/* Active indicator */}
                    {active && (
                      <motion.div
                        layoutId="nav-active"
                        className="absolute inset-0 bg-sidebar-accent rounded-lg -z-10"
                        transition={{ type: "spring", bounce: 0.15, duration: 0.3 }}
                      />
                    )}
                  </motion.div>
                </Link>
              );
            })}

            {sidebarCollapsed && (
              <div className="my-1 mx-3 h-px bg-sidebar-border/40" />
            )}
          </div>
        ))}
      </div>

      {/* Bottom Section */}
      <div className="border-t border-sidebar-border p-2 space-y-0.5 flex-shrink-0">
        {/* Notifications */}
        <Link to="/notifications">
          <div
            className={cn(
              "tv-nav-item relative",
              sidebarCollapsed && "justify-center px-2"
            )}
          >
            <div className="relative">
              <Bell className="w-4 h-4 text-sidebar-foreground/60" />
              {notifCount > 0 && (
                <span className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-red-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center">
                  {notifCount > 9 ? "9+" : notifCount}
                </span>
              )}
            </div>
            <AnimatePresence>
              {!sidebarCollapsed && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-sm font-medium"
                >
                  Notifications
                </motion.span>
              )}
            </AnimatePresence>
          </div>
        </Link>

        {/* User Profile & Log Out */}
        <div className={cn(
          "flex items-center justify-between gap-2 px-2 py-2 rounded-lg",
          "hover:bg-sidebar-border/50 transition-colors duration-150",
          sidebarCollapsed && "justify-center"
        )}>
          <div className="flex items-center gap-2.5 min-w-0 flex-1">
            <div className="w-6 h-6 bg-primary/20 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-[10px] font-bold text-primary">
                {user?.full_name?.charAt(0)?.toUpperCase() || "U"}
              </span>
            </div>
            <AnimatePresence>
              {!sidebarCollapsed && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex-1 min-w-0"
                >
                  <div className="text-xs font-semibold text-sidebar-foreground truncate">
                    {user?.full_name || "Officer"}
                  </div>
                  <div className="text-[10px] text-sidebar-foreground/40 capitalize truncate">
                    {user?.email || "Signed In"}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <button
            onClick={handleLogout}
            title="Log Out"
            className="p-1 text-muted-foreground hover:text-red-500 hover:bg-red-500/10 rounded-md transition-colors flex-shrink-0"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.aside>
  );
}

