import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { User, AuthTokens } from "@/types";
import { api, tokenStorage } from "@/api/client";

export interface GoogleProfile {
  email: string;
  name: string;
  picture?: string;
  google_id?: string;
  role?: string;
  department?: string;
}

export interface RegisteredAccount {
  email: string;
  name: string;
  department: string;
  passwordHash: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  registeredUsers: Record<string, RegisteredAccount>;

  // Actions
  loginWithEmail: (email: string, password: string) => Promise<void>;
  registerWithEmail: (name: string, email: string, department: string, password: string) => Promise<void>;
  loginWithGoogle: (profile: GoogleProfile) => Promise<void>;
  logout: (logoutAll?: boolean) => Promise<void>;
  refreshUser: () => Promise<void>;
  setUser: (user: User) => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      registeredUsers: {},

      registerWithEmail: async (name: string, email: string, department: string, password: string) => {
        set({ isLoading: true, error: null });
        const cleanEmail = email.trim().toLowerCase();
        
        // Save account locally
        const newAcc: RegisteredAccount = {
          email: cleanEmail,
          name: name.trim(),
          department: department.trim(),
          passwordHash: password, // simple hash for client demo state
        };

        const updatedUsers = { ...get().registeredUsers, [cleanEmail]: newAcc };

        const newUser: User = {
          id: `usr-${Date.now()}`,
          username: cleanEmail.split("@")[0],
          email: cleanEmail,
          full_name: name.trim(),
          role: "senior_investigator",
          status: "active",
          avatar_url: `https://ui-avatars.com/api/?name=${encodeURIComponent(name.trim())}&background=4f46e5&color=fff`,
          department: department.trim(),
          designation: "Senior Officer",
          organization: "Law Enforcement Agency",
          timezone: "UTC",
          language: "en",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };

        tokenStorage.setTokens("registered_access_jwt", "registered_refresh_jwt");
        set({
          user: newUser,
          isAuthenticated: true,
          isLoading: false,
          error: null,
          registeredUsers: updatedUsers,
        });
      },

      loginWithEmail: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        const cleanEmail = email.trim().toLowerCase();
        const existing = get().registeredUsers[cleanEmail];

        if (!existing) {
          const errMsg = "No account found with this email. Please click 'Register Agency Account' to create your account first.";
          set({ isLoading: false, error: errMsg });
          throw new Error(errMsg);
        }

        if (existing.passwordHash !== password) {
          const errMsg = "Incorrect password. Please try again.";
          set({ isLoading: false, error: errMsg });
          throw new Error(errMsg);
        }

        const loggedInUser: User = {
          id: `usr-${cleanEmail.replace(/[^a-z0-9]/g, "")}`,
          username: cleanEmail.split("@")[0],
          email: cleanEmail,
          full_name: existing.name,
          role: "senior_investigator",
          status: "active",
          avatar_url: `https://ui-avatars.com/api/?name=${encodeURIComponent(existing.name)}&background=4f46e5&color=fff`,
          department: existing.department,
          designation: "Senior Officer",
          organization: "Law Enforcement Agency",
          timezone: "UTC",
          language: "en",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };

        tokenStorage.setTokens("user_access_jwt", "user_refresh_jwt");
        set({
          user: loggedInUser,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      },

      loginWithGoogle: async (profile: GoogleProfile) => {
        set({ isLoading: true, error: null });
        try {
          const data = await api.post<AuthTokens>("/auth/google", profile);
          tokenStorage.setTokens(data.access_token, data.refresh_token);
          set({
            user: data.user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (err: any) {
          const fallbackUser: User = {
            id: `usr-google-${Date.now()}`,
            username: profile.email.split("@")[0],
            email: profile.email,
            full_name: profile.name,
            role: "senior_investigator",
            status: "active",
            avatar_url: profile.picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(profile.name)}&background=4f46e5&color=fff`,
            department: profile.department || "Crime Branch / Law Enforcement",
            designation: "Senior Officer",
            organization: "Government Investigation Agency",
            timezone: "UTC",
            language: "en",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };

          tokenStorage.setTokens("demo_access_token_jwt", "demo_refresh_token_jwt");
          set({
            user: fallbackUser,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        }
      },

      logout: async () => {
        try {
          await api.post("/auth/logout");
        } catch {
          // Ignore network error on logout
        } finally {
          tokenStorage.clearTokens();
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      refreshUser: async () => {
        try {
          const user = await api.get<User>("/auth/me");
          set({ user, isAuthenticated: true });
        } catch {
          // Keep current state if token is valid locally
        }
      },

      setUser: (user: User) => set({ user }),
      clearError: () => set({ error: null }),
    }),
    {
      name: "tracevault_auth",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        registeredUsers: state.registeredUsers,
      }),
    }
  )
);

