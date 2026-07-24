/**
 * TraceVault Main Layout Wrapper
 * Controls sidebar collapse width, header sticky placement, copilot drawer overlay, and page rendering.
 */
import React from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { CopilotDrawer } from "@/components/copilot/CopilotDrawer";
import { useUIStore } from "@/stores/uiStore";
import { cn } from "@/lib/utils";

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const { sidebarCollapsed, copilotOpen, copilotWidth } = useUIStore();

  return (
    <div className="tv-main-layout">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div
        className={cn(
          "flex-1 flex flex-col min-w-0 transition-all duration-250 ease-in-out",
          sidebarCollapsed ? "ml-[60px]" : "ml-[260px]"
        )}
        style={{
          marginRight: copilotOpen ? copilotWidth : 0,
        }}
      >
        {/* Top Header */}
        <Header />

        {/* Dynamic Page Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-background">
          <div className="max-w-7xl mx-auto space-y-6">{children}</div>
        </main>
      </div>

      {/* AI Copilot Side Drawer */}
      <CopilotDrawer />
    </div>
  );
}
