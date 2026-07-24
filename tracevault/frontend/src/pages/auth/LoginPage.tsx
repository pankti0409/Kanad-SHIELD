/**
 * TraceVault Authentication & Registration Portal
 * Supports user registration, password authentication, and Google SSO.
 */
import React, { useState } from "react";
import { motion } from "framer-motion";
import { Shield, AlertCircle, ArrowRight, Lock, User, Key, Building } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";

export function LoginPage() {
  const [mode, setMode] = useState<"signin" | "register">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { loginWithEmail, registerWithEmail, loginWithGoogle } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      if (mode === "register") {
        if (!name.trim() || !email.trim() || !department.trim() || !password.trim()) {
          setError("All fields are mandatory for registration.");
          setIsLoading(false);
          return;
        }
        await registerWithEmail(name, email, department, password);
      } else {
        if (!email.trim() || !password.trim()) {
          setError("Please enter both email address and password.");
          setIsLoading(false);
          return;
        }
        await loginWithEmail(email, password);
      }
      navigate("/");
    } catch (err: any) {
      setError(err?.message || "Authentication failed. Please check your credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    if (!email.trim()) {
      setError("Please enter your email address to continue with Google SSO.");
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      await loginWithGoogle({
        email: email.trim(),
        name: name.trim() || email.trim().split("@")[0],
        department: department.trim() || "Law Enforcement & Intelligence",
      });
      navigate("/");
    } catch (err: any) {
      setError("Google authentication failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Pastel Aura */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[550px] bg-primary/10 rounded-full blur-[140px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.25 }}
        className="w-full max-w-md tv-card p-8 shadow-card-lg relative z-10 border-border/80 backdrop-blur-xl space-y-6"
      >
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-primary via-indigo-600 to-accent text-white shadow-glow-primary mb-2">
            <Shield className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-extrabold text-foreground tracking-tight">TraceVault</h1>
          <p className="text-xs text-muted-foreground font-medium">
            Government & Law Enforcement Intelligence Portal
          </p>
        </div>

        {/* Auth Mode Toggle Tabs */}
        <div className="flex bg-muted/60 p-1 rounded-xl border border-border">
          <button
            type="button"
            onClick={() => {
              setMode("signin");
              setError(null);
            }}
            className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all ${
              mode === "signin"
                ? "bg-card text-foreground shadow-card"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setMode("register");
              setError(null);
            }}
            className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all ${
              mode === "register"
                ? "bg-card text-foreground shadow-card"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Register Agency Account
          </button>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-500 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Authentication Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-3">
            {mode === "register" && (
              <>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5 text-primary" /> Full Name *
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Pankti Patel"
                    required
                    className="w-full px-3.5 py-2.5 bg-muted/50 border border-border rounded-xl text-xs text-foreground outline-none focus:border-primary placeholder:text-muted-foreground transition-all"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                    <Building className="w-3.5 h-3.5 text-primary" /> Department / Agency *
                  </label>
                  <input
                    type="text"
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    placeholder="e.g. Cyber Crime Branch / Special Cell"
                    required
                    className="w-full px-3.5 py-2.5 bg-muted/50 border border-border rounded-xl text-xs text-foreground outline-none focus:border-primary placeholder:text-muted-foreground transition-all"
                  />
                </div>
              </>
            )}

            <div className="space-y-1">
              <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                <User className="w-3.5 h-3.5 text-primary" /> Email Address *
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="e.g. user@gmail.com or officer@agency.gov.in"
                required
                className="w-full px-3.5 py-2.5 bg-muted/50 border border-border rounded-xl text-xs text-foreground outline-none focus:border-primary placeholder:text-muted-foreground transition-all"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-primary" /> Password *
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                required
                className="w-full px-3.5 py-2.5 bg-muted/50 border border-border rounded-xl text-xs text-foreground outline-none focus:border-primary placeholder:text-muted-foreground transition-all"
              />
            </div>
          </div>

          {/* Action Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-4 bg-primary hover:bg-primary/90 text-white font-semibold text-xs rounded-xl shadow-glow-primary transition-all flex items-center justify-center gap-2 group relative overflow-hidden mt-2"
          >
            <span>
              {isLoading
                ? "Processing..."
                : mode === "register"
                ? "Register & Access Platform"
                : "Sign In to Dashboard"}
            </span>
            <ArrowRight className="w-4 h-4 text-white/80 group-hover:translate-x-1 transition-transform ml-auto" />
          </button>
        </form>

        <div className="text-center text-xs text-muted-foreground pt-1">
          {mode === "signin" ? (
            <span>
              Don't have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setMode("register");
                  setError(null);
                }}
                className="text-primary font-bold hover:underline"
              >
                Register here
              </button>
            </span>
          ) : (
            <span>
              Already registered?{" "}
              <button
                type="button"
                onClick={() => {
                  setMode("signin");
                  setError(null);
                }}
                className="text-primary font-bold hover:underline"
              >
                Sign In
              </button>
            </span>
          )}
        </div>

        {/* Google SSO Alternative Button */}
        <div className="space-y-2 pt-2 border-t border-border">
          <button
            type="button"
            onClick={handleGoogleSignIn}
            disabled={isLoading}
            className="w-full py-2.5 px-4 bg-card hover:bg-muted/80 text-foreground border border-border rounded-xl font-semibold text-xs shadow-card hover:shadow-card-hover transition-all flex items-center justify-center gap-3"
          >
            <svg className="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            <span>Continue with Google SSO</span>
          </button>
        </div>

        {/* Footer Security Badges */}
        <div className="pt-4 border-t border-border/60 text-center text-[11px] text-muted-foreground flex items-center justify-between">
          <span className="flex items-center gap-1">
            <Lock className="w-3 h-3 text-emerald-500" />
            256-Bit SSL • OAuth 2.0
          </span>
          <span className="font-mono text-[10px]">TraceVault v1.0</span>
        </div>
      </motion.div>
    </div>
  );
}


