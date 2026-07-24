/**
 * TraceVault UI Store (Zustand)
 * Global UI state: sidebar, theme, copilot, notifications, active orbit tier state.
 */
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

type Theme = "light" | "dark" | "system";

interface UIState {
  // Sidebar
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;

  // Active Orbit Tier (persisted across page navigation)
  activeOrbitTierId: string;
  setActiveOrbitTierId: (id: string) => void;

  // Copilot
  copilotOpen: boolean;
  copilotWidth: number;
  setCopilotOpen: (open: boolean) => void;
  toggleCopilot: () => void;
  setCopilotWidth: (width: number) => void;

  // Theme
  theme: Theme;
  setTheme: (theme: Theme) => void;

  // Command Palette
  commandPaletteOpen: boolean;
  setCommandPaletteOpen: (open: boolean) => void;

  // Notifications
  unreadCount: number;
  setUnreadCount: (count: number) => void;

  // Active case context
  activeCaseId: string | null;
  activeRecordingId: string | null;
  setActiveCaseId: (id: string | null) => void;
  setActiveRecordingId: (id: string | null) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

      activeOrbitTierId: "reports",
      setActiveOrbitTierId: (id) => set({ activeOrbitTierId: id }),

      copilotOpen: false,
      copilotWidth: 420,
      setCopilotOpen: (open) => set({ copilotOpen: open }),
      toggleCopilot: () =>
        set((state) => ({ copilotOpen: !state.copilotOpen })),
      setCopilotWidth: (width) => set({ copilotWidth: width }),

      theme: "dark",
      setTheme: (theme) => {
        set({ theme });
        applyTheme(theme);
      },

      commandPaletteOpen: false,
      setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),

      unreadCount: 0,
      setUnreadCount: (count) => set({ unreadCount: count }),

      activeCaseId: null,
      activeRecordingId: null,
      setActiveCaseId: (id) => set({ activeCaseId: id }),
      setActiveRecordingId: (id) => set({ activeRecordingId: id }),
    }),
    {
      name: "tracevault_ui",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        activeOrbitTierId: state.activeOrbitTierId,
        copilotWidth: state.copilotWidth,
        theme: state.theme,
      }),
    }
  )
);

function applyTheme(theme: Theme): void {
  const root = document.documentElement;
  if (theme === "system") {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    root.classList.toggle("dark", prefersDark);
  } else {
    root.classList.toggle("dark", theme === "dark");
  }
}
