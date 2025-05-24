"use client";

import React, { useState } from "react";
import RoleBasedDashboard from "@/components/dashboard/role-based-dashboard";

const roles = [
  { id: 'developer', name: 'Developer', icon: '🧑‍💻' },
  { id: 'em', name: 'Engineering Manager', icon: '👨‍💼' },
  { id: 'tpm', name: 'Technical Program Manager', icon: '🧑‍💼' },
  { id: 'pm', name: 'Product Manager', icon: '📋' },
  { id: 'qa', name: 'QA Manager', icon: '🧪' },
  { id: 'scrum', name: 'Scrum Master', icon: '🧑‍🏫' },
  { id: 'ux', name: 'UX Designer', icon: '🧑‍🎨' },
  { id: 'executive', name: 'Executive/Director', icon: '💼' }
];

const DashboardPage = () => {
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [repoUrl, setRepoUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisData, setAnalysisData] = useState<any>(null);

  const startAnalysis = async () => {
    if (!repoUrl || !selectedRole) return;

    setIsAnalyzing(true);
    setAnalysisData(null);

    try {
      const response = await fetch(`http://localhost:8000/api/analyze-repository`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repoUrl,
          role: selectedRole
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setAnalysisData(data);
    } catch (error) {
      console.error('Analysis failed:', error);
      // Set mock data for development
      setAnalysisData({
        success: true,
        analysis_id: 'mock-analysis',
        role: selectedRole,
        repository: repoUrl
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setAnalysisData(null);
    setRepoUrl('');
    setSelectedRole(null);
  };

  if (analysisData) {
    return (
      <main className="py-8">
        <div className="mb-6 flex justify-between items-center">
          <h1 className="text-4xl font-bold text-gradient">
            {roles.find(r => r.id === selectedRole)?.icon} {roles.find(r => r.id === selectedRole)?.name} Dashboard
          </h1>
          <button
            onClick={resetAnalysis}
            className="px-6 py-2 bg-muted hover:bg-muted/80 rounded-lg transition-colors"
          >
            New Analysis
          </button>
        </div>
        <RoleBasedDashboard role={selectedRole} analysisData={analysisData} />
      </main>
    );
  }

  return (
    <main className="py-8">
      {/* Hero Section */}
      <div className="relative mb-12">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-indigo-600/20 rounded-3xl blur-xl" />
        <div className="relative glass-card rounded-3xl p-8 hover-lift">
          <h2 className="text-5xl font-bold tracking-tight mb-4 text-gradient">
            Repository Intelligence Platform
          </h2>
          <p className="text-xl text-muted-foreground">
            Get role-specific insights from GitHub repositories powered by AI analysis
          </p>
          <div className="mt-6 flex items-center gap-4">
            <div className="h-1 w-20 bg-gradient-to-r from-primary to-accent rounded-full" />
            <div className="h-1 w-12 bg-gradient-to-r from-accent to-chart-2 rounded-full" />
            <div className="h-1 w-8 bg-gradient-to-r from-chart-2 to-chart-3 rounded-full" />
          </div>
        </div>
      </div>

      {/* Role Selection */}
      <div className="mb-8">
        <div className="glass-card rounded-2xl p-6 hover-lift glow-blue">
          <h3 className="text-2xl font-bold text-gradient mb-6">Select Your Role</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {roles.map((role) => (
              <button
                key={role.id}
                onClick={() => setSelectedRole(role.id)}
                className={`group relative p-4 rounded-xl border transition-all duration-300 hover-lift ${
                  selectedRole === role.id
                    ? 'border-primary bg-primary/10 glow-accent'
                    : 'border-white/10 bg-gradient-to-r from-muted/10 to-accent/5 hover:border-primary/30'
                }`}
              >
                <div className="flex flex-col items-center gap-2">
                  <div className="text-2xl">{role.icon}</div>
                  <span className="text-sm font-medium text-center">{role.name}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Repository Input */}
      <div className="mb-8">
        <div className="glass-card rounded-2xl p-6 hover-lift glow-accent">
          <h3 className="text-2xl font-bold text-gradient mb-6">Repository Analysis</h3>
          <div className="space-y-4">
            <div>
              <label htmlFor="repo-url" className="block text-sm font-medium mb-2">
                GitHub Repository URL
              </label>
              <input
                id="repo-url"
                type="url"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/username/repository"
                className="w-full px-4 py-3 bg-background/50 border border-white/10 rounded-lg focus:border-primary/50 focus:outline-none transition-colors"
              />
            </div>
            <button
              onClick={startAnalysis}
              disabled={!repoUrl || !selectedRole || isAnalyzing}
              className={`w-full py-3 px-6 rounded-lg font-medium transition-all duration-300 ${
                !repoUrl || !selectedRole || isAnalyzing
                  ? 'bg-muted text-muted-foreground cursor-not-allowed'
                  : 'bg-gradient-to-r from-primary to-accent text-primary-foreground hover:shadow-lg hover:shadow-primary/25 hover-lift'
              }`}
            >
              {isAnalyzing ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  Analyzing Repository...
                </div>
              ) : (
                'Analyze Repository'
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="glass-card rounded-2xl p-6 hover-lift">
        <h3 className="text-xl font-bold text-gradient mb-4">How It Works</h3>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-2xl">1️⃣</span>
            </div>
            <h4 className="font-semibold mb-2">Choose Your Role</h4>
            <p className="text-sm text-muted-foreground">
              Select your role to get personalized insights tailored to your responsibilities
            </p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-accent/20 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-2xl">2️⃣</span>
            </div>
            <h4 className="font-semibold mb-2">Add Repository</h4>
            <p className="text-sm text-muted-foreground">
              Paste the GitHub repository URL you want to analyze
            </p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-chart-2/20 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-2xl">3️⃣</span>
            </div>
            <h4 className="font-semibold mb-2">Get AI Insights</h4>
            <p className="text-sm text-muted-foreground">
              Receive comprehensive analysis with graphs, metrics, and actionable insights
            </p>
          </div>
        </div>
      </div>

      {/* Enhanced AI Agent Button */}
      <div className="fixed bottom-8 right-8 z-40">
        <button
          aria-label="Chat with AI Agent"
          className="group relative flex items-center justify-center gap-3 h-16 px-8 bg-gradient-to-r from-primary to-accent text-primary-foreground rounded-2xl shadow-2xl hover:shadow-primary/25 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background focus:ring-primary transition-all duration-300 animate-pulse-glow hover-lift"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-primary/80 to-accent/80 rounded-2xl blur-sm group-hover:blur-md transition-all duration-300" />
          <div className="relative flex items-center gap-3">
            <svg
              className="h-7 w-7 transform group-hover:rotate-12 group-hover:scale-110 transition-transform duration-300"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-3.862 8.25-8.625 8.25S3.75 16.556 3.75 12 7.612 3.75 12.375 3.75 21 7.444 21 12z"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span className="text-lg font-bold tracking-wide">AI Agent</span>
          </div>
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-accent rounded-full animate-ping" />
          <div
            className="absolute -bottom-1 -left-1 w-2 h-2 bg-primary rounded-full animate-ping"
            style={{ animationDelay: "1s" }}
          />
        </button>
      </div>
    </main>
  );
};

export default DashboardPage;