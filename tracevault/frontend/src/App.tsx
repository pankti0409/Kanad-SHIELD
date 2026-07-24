/**
 * TraceVault Master Application Component
 * Configures React Router 6, layout wrappers, and protected route guards.
 */
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { MainLayout } from "@/components/layout/MainLayout";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { LoginPage } from "@/pages/auth/LoginPage";
import { Dashboard } from "@/pages/Dashboard";
import { CasesPage } from "@/pages/cases/CasesPage";
import { TranscriptViewer } from "@/pages/transcripts/TranscriptViewer";
import { KnowledgeGraphPage } from "@/pages/intelligence/KnowledgeGraphPage";
import { IntelligencePage } from "@/pages/intelligence/IntelligencePage";
import { ReportsPage } from "@/pages/reports/ReportsPage";
import { AuditLogPage } from "@/pages/audit/AuditLogPage";
import { AnalyticsPage } from "@/pages/analytics/AnalyticsPage";
import { RecordingsPage } from "@/pages/recordings/RecordingsPage";
import { SettingsPage } from "@/pages/settings/SettingsPage";
import { SearchPage } from "@/pages/search/SearchPage";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Login Route */}
        <Route path="/login" element={<LoginPage />} />

        {/* Protected Application Routes Wrapped in Main Layout */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <MainLayout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/cases" element={<CasesPage />} />
                  <Route path="/cases/:id" element={<CasesPage />} />
                  <Route path="/search" element={<SearchPage />} />
                  <Route path="/recordings" element={<RecordingsPage />} />
                  <Route path="/transcripts" element={<TranscriptViewer />} />
                  <Route path="/intelligence" element={<IntelligencePage />} />
                  <Route path="/knowledge-graph" element={<KnowledgeGraphPage />} />
                  <Route path="/reports" element={<ReportsPage />} />
                  <Route path="/analytics" element={<AnalyticsPage />} />
                  <Route path="/audit" element={<AuditLogPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </MainLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
