"use client";
import React, { useState, useEffect } from "react";
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ComposedChart, ScatterChart, Scatter
} from 'recharts';

// Color palette for charts
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF7C7C'];

interface Dependency {
  name: string;
  version: string;
  type: "production" | "development" | "peer";
  vulnerable?: boolean;
  outdated?: boolean;
}

interface CommitPattern {
  date: string;
  commits: number;
  additions: number;
  deletions: number;
}

interface Release {
  tag_name: string;
  name: string;
  published_at: string;
  draft: boolean;
  prerelease: boolean;
}

interface SecurityAdvisory {
  severity: string;
  summary: string;
  package_name: string;
}

interface CodeComplexity {
  cyclomatic_complexity: number;
  maintainability_index: number;
  code_smells: string[];
  technical_debt: {
    hours: number;
    rating: string;
  };
  file_complexity: Array<{
    name: string;
    size: number;
    complexity_score: number;
  }>;
  hotspots: Array<{
    file: string;
    risk_level: string;
    recommendation: string;
  }>;
  architecture_score: number;
}

interface ContributorPatterns {
  top_contributors: Array<{
    login: string;
    commits: number;
    tenure_days: number;
    activity_score: number;
    first_commit: string;
    last_commit: string;
  }>;
  activity_patterns: {
    by_hour: Record<string, number>;
    by_day: Record<string, number>;
    by_month: Record<string, number>;
  };
  contributor_retention: {
    new_contributors: number;
    returning_contributors: number;
    churned_contributors: number;
  };
}

interface TrendAnalysis {
  growth_trajectory: {
    stars_velocity: number;
    forks_velocity: number;
    contributors_velocity: number;
    commits_velocity: number;
  };
  popularity_score: number;
  momentum_indicators: {
    recent_activity_score: number;
    community_engagement: number;
    maintenance_health: number;
  };
  predictions: {
    stars_6_months: number;
    contributors_6_months: number;
    maintenance_risk: string;
  };
  lifecycle_stage: string;
}

interface AdvancedInsights {
  executive_summary: string;
  key_strengths: string;
  areas_for_improvement: string;
  technical_assessment: string;
  security_analysis: string;
  performance_insights: string;
  community_collaboration: string;
  strategic_recommendations: string;
  competitive_positioning: string;
  risk_assessment: string;
}

interface RepoAnalysis {
  repo_info: {
    name: string;
    full_name: string;
    description: string;
    url: string;
    created_at: string;
    updated_at: string;
    homepage?: string;
    topics: string[];
    default_branch: string;
    archived: boolean;
    disabled: boolean;
    private: boolean;
  };
  metrics: {
    stars: number;
    forks: number;
    watchers: number;
    open_issues: number;
    size: number;
    network_count: number;
    subscribers_count: number;
  };
  tech_stack: {
    languages: Record<string, number>;
    primary_language: string;
    total_languages: number;
  };
  dependencies: {
    total_count: number;
    production: Dependency[];
    development: Dependency[];
    vulnerable_count: number;
    outdated_count: number;
    dependency_tree: Record<string, string[]>;
  };
  commits: {
    total_count: number;
    recent_count: number;
    patterns: CommitPattern[];
    avg_per_week: number;
    top_committers: Array<{
      login: string;
      commits: number;
      avatar_url: string;
    }>;
    commit_frequency: Record<string, number>;
  };
  issues_prs: {
    total_issues: number;
    open_issues: number;
    avg_resolution_time: number;
    total_prs: number;
    open_prs: number;
    avg_merge_time: number;
    labels: Array<{ name: string; count: number; color: string }>;
  };
  releases: {
    total_count: number;
    latest: Release | null;
    recent_releases: Release[];
    release_frequency: number;
  };
  security: {
    has_security_policy: boolean;
    has_vulnerability_alerts: boolean;
    advisories: SecurityAdvisory[];
    branch_protection: boolean;
    signed_commits: boolean;
  };
  code_analysis: {
    total_files: number;
    total_lines: number;
    large_files: Array<{ name: string; size: number }>;
    file_types: Record<string, number>;
    test_coverage: number | null;
    documentation_score: number;
  };
  community: {
    has_readme: boolean;
    has_license: boolean;
    has_contributing: boolean;
    has_code_of_conduct: boolean;
    community_score: number;
  };
  performance: {
    health_score: number;
    activity_score: number;
    maintenance_score: number;
    recent_commits: number;
  };
  insights: string[];
  code_complexity: CodeComplexity;
  contributor_patterns: ContributorPatterns;
  trend_analysis: TrendAnalysis;
  advanced_insights: AdvancedInsights;
}

const RepoAnalyzer = () => {
  const [repoUrl, setRepoUrl] = useState("");
  const [analysis, setAnalysis] = useState<RepoAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState("");
  const [clientId, setClientId] = useState<string | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  const backendUrl = "http://localhost:8000";

  const startAnalysis = async () => {
    if (!repoUrl.trim()) return;

    setLoading(true);
    setProgress(0);
    setProgressMessage("Starting analysis...");
    setAnalysis(null);

    try {
      const response = await fetch(`${backendUrl}/api/analyze-repository`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repoUrl.trim(),
          experience_level: "advanced",
          focus_areas: []
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const newClientId = data.client_id;
      setClientId(newClientId);

      // Connect to WebSocket for progress updates
      const wsUrl = `ws://localhost:8000/ws/${newClientId}`;
      const websocket = new WebSocket(wsUrl);
      setWs(websocket);

      websocket.onmessage = (event) => {
        const progressData = JSON.parse(event.data);
        setProgress(progressData.progress);
        setProgressMessage(progressData.message);
      };

      websocket.onclose = () => {
        fetchResults(newClientId);
      };

    } catch (error) {
      console.error("Analysis failed:", error);
      setLoading(false);
      setProgress(0);
      setProgressMessage("Analysis failed. Please try again.");
    }
  };

  const fetchResults = async (id: string) => {
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const response = await fetch(`${backendUrl}/api/analysis/${id}`);
      if (response.ok) {
        const data = await response.json();
        setAnalysis(data);
      }
    } catch (error) {
      console.error("Failed to fetch results:", error);
    } finally {
      setLoading(false);
      setProgress(0);
      setProgressMessage("");
    }
  };

  // Format data for charts
  const getLanguageData = () => {
    if (!analysis?.tech_stack.languages) return [];
    return Object.entries(analysis.tech_stack.languages)
      .map(([name, percentage]) => ({ name, value: percentage }))
      .sort((a, b) => b.value - a.value);
  };

  const getCommitTrendData = () => {
    if (!analysis?.contributor_patterns.activity_patterns.by_month) return [];
    return Object.entries(analysis.contributor_patterns.activity_patterns.by_month)
      .map(([month, commits]) => ({ month, commits }))
      .sort((a, b) => a.month.localeCompare(b.month));
  };

  const getContributorData = () => {
    if (!analysis?.contributor_patterns.top_contributors) return [];
    return analysis.contributor_patterns.top_contributors.slice(0, 10)
      .map(contributor => ({
        name: contributor.login,
        commits: contributor.commits,
        activity_score: Math.round(contributor.activity_score)
      }));
  };

  const getComplexityData = () => {
    if (!analysis?.code_complexity.file_complexity) return [];
    return analysis.code_complexity.file_complexity.slice(0, 8)
      .map(file => ({
        name: file.name.length > 20 ? '...' + file.name.slice(-20) : file.name,
        complexity: file.complexity_score,
        size: file.size
      }));
  };

  const getPerformanceRadarData = () => {
    if (!analysis) return [];
    return [
      {
        metric: 'Health',
        value: analysis.performance.health_score || 0,
        fullMark: 100
      },
      {
        metric: 'Activity', 
        value: analysis.performance.activity_score || 0,
        fullMark: 100
      },
      {
        metric: 'Maintenance',
        value: analysis.performance.maintenance_score || 0,
        fullMark: 100
      },
      {
        metric: 'Code Quality',
        value: analysis.code_complexity.maintainability_index || 0,
        fullMark: 100
      },
      {
        metric: 'Architecture',
        value: analysis.code_complexity.architecture_score || 0,
        fullMark: 100
      },
      {
        metric: 'Community',
        value: analysis.community.community_score || 0,
        fullMark: 100
      }
    ];
  };

  // Empty state with theme colors
  if (!analysis) {
    return (
      <div className="p-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-block p-6 rounded-full bg-gradient-to-r from-primary/20 to-accent/20 backdrop-blur-sm mb-6">
              <div className="text-6xl">🔍</div>
            </div>
            <h1 className="text-5xl font-bold text-gradient mb-4">
              Repository Analyzer
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Unleash the power of AI-driven analysis for comprehensive repository insights, security assessment, and performance metrics
            </p>
          </div>

          <div className="glass-card rounded-3xl p-8 hover-lift">
            <div className="space-y-8">
              <div>
                <label className="block text-foreground text-lg font-medium mb-4">
                  GitHub Repository URL
                </label>
                <div className="relative">
                  <input
                    type="url"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="https://github.com/owner/repository"
                    className="w-full px-6 py-4 bg-input border border-border rounded-2xl text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent backdrop-blur-sm text-lg"
                  />
                </div>
              </div>

              <button
                onClick={startAnalysis}
                disabled={loading || !repoUrl.trim()}
                className="w-full bg-gradient-to-r from-primary to-accent text-primary-foreground font-semibold py-4 px-8 rounded-2xl hover:opacity-90 transform hover:scale-[1.02] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-xl text-lg"
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-3">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-foreground"></div>
                    <span>Analyzing Repository...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center space-x-3">
                    <span>🚀</span>
                    <span>Start Deep Analysis</span>
                  </div>
                )}
              </button>

              {loading && (
                <div className="space-y-6">
                  <div className="glass-card rounded-2xl p-6">
                    <div className="flex justify-between text-foreground text-sm mb-3">
                      <span className="font-medium">{progressMessage}</span>
                      <span className="font-bold">{progress}%</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-primary to-accent h-3 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Analysis results - simplified for now
  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header Section */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold text-gradient mb-6">
            {analysis.repo_info.name}
          </h1>
          <p className="text-2xl text-muted-foreground max-w-4xl mx-auto leading-relaxed mb-8">
            {analysis.repo_info.description}
          </p>
          
          {/* Key Metrics */}
          <div className="flex justify-center items-center space-x-12 mt-12">
            <div className="text-center">
              <div className="text-4xl font-bold text-chart-4 mb-2">
                ⭐ {analysis.metrics.stars.toLocaleString()}
              </div>
              <div className="text-muted-foreground text-lg">Stars</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-primary mb-2">
                🍴 {analysis.metrics.forks.toLocaleString()}
              </div>
              <div className="text-muted-foreground text-lg">Forks</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-chart-2 mb-2">
                📝 {analysis.commits.total_count.toLocaleString()}
              </div>
              <div className="text-muted-foreground text-lg">Commits</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-accent mb-2">
                👥 {analysis.contributor_patterns.top_contributors.length}
              </div>
              <div className="text-muted-foreground text-lg">Contributors</div>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="text-center">
          <button
            onClick={() => {
              setAnalysis(null);
              setRepoUrl("");
            }}
            className="bg-gradient-to-r from-primary to-accent text-primary-foreground font-semibold py-4 px-12 rounded-2xl hover:opacity-90 transform hover:scale-[1.02] transition-all duration-300 shadow-xl text-lg"
          >
            <div className="flex items-center space-x-3">
              <span>🔍</span>
              <span>Analyze Another Repository</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default RepoAnalyzer; 