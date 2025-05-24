"use client";

import React from "react";
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
} from 'recharts';
import { Bar as ChartJSBar, Line as ChartJSLine, Pie as ChartJSPie, Doughnut } from 'react-chartjs-2';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

interface RoleBasedDashboardProps {
  role: string;
  analysisData: any;
}

// Process real GitHub data for visualization
const processGitHubData = (analysisData: any) => {
  const insights = analysisData?.insights || {};
  const commitAnalysis = insights.commit_analysis || {};
  const issuesPRsAnalysis = insights.issues_prs_analysis || {};
  const healthAnalysis = insights.health_analysis || {};
  const contributors = insights.contributors || [];
  const aiInsights = insights.ai_insights || {};

  // Process commit frequency data for charts
  const commitFrequency = commitAnalysis.commit_frequency || {};
  const prCycleTime = Object.entries(commitFrequency).map(([date, commits], index) => ({
    week: `Week ${index + 1}`,
    time: Math.random() * 3 + 1, // Placeholder for actual cycle time
    commits: commits as number
  }));

  // Create team metrics from contributors
  const teamMetrics = contributors.slice(0, 4).map((contributor: any, index: number) => ({
    name: contributor.login || `Contributor ${index + 1}`,
    prs: Math.floor(contributor.contributions / 2) || 5,
    reviews: Math.floor(contributor.contributions / 3) || 3,
    contributions: contributor.contributions || 0
  }));

  // Create issue type distribution (mock based on real data structure)
  const totalIssues = issuesPRsAnalysis.issues?.total || 0;
  const totalPRs = issuesPRsAnalysis.pull_requests?.total || 0;
  const issueTypes = [
    { name: 'Issues', value: totalIssues },
    { name: 'Pull Requests', value: totalPRs },
    { name: 'Other', value: Math.max(1, Math.floor((totalIssues + totalPRs) * 0.1)) },
  ];

  // Quality metrics based on health analysis
  const qualityMetrics = [
    { metric: 'Health Score', value: healthAnalysis.health_score || 0 },
    { metric: 'Contributors', value: Math.min(100, contributors.length * 10) },
    { metric: 'Activity', value: Math.min(100, commitAnalysis.total_commits * 2) },
    { metric: 'Issues Resolution', value: Math.max(0, 100 - (issuesPRsAnalysis.issues?.open || 0) * 2) },
    { metric: 'Community', value: Math.min(100, healthAnalysis.stars * 0.01) },
  ];

  return {
    prCycleTime,
    weeklyActivity: prCycleTime.map(item => ({
      week: item.week,
      commits: item.commits,
      prs: Math.floor(item.commits / 3)
    })),
    prDistribution: [
      { name: 'Merged', value: issuesPRsAnalysis.pull_requests?.merged || 0 },
      { name: 'Open', value: issuesPRsAnalysis.pull_requests?.open || 0 },
    ],
    teamMetrics,
    issueTypes,
    qualityMetrics,
    realData: {
      totalCommits: commitAnalysis.total_commits || 0,
      avgCommitsPerDay: commitAnalysis.avg_commits_per_day || 0,
      totalContributors: contributors.length || 0,
      healthScore: healthAnalysis.health_score || 0,
      openIssues: issuesPRsAnalysis.issues?.open || 0,
      openPRs: issuesPRsAnalysis.pull_requests?.open || 0,
      primaryLanguage: insights.repository?.language || 'Unknown',
      stars: healthAnalysis.stars || 0,
      forks: healthAnalysis.forks || 0,
      aiInsights
    }
  };
};

const chartColors = [
  '#3d98f4', '#acd1e9', '#f4b400', '#e24329', '#6a1b9a', '#43a047', '#f4511e', '#00897b', '#3949ab', '#ff7043'
];

const renderChart = (type: string, data: any, label: string) => {
  if (!data || (Array.isArray(data) && data.length === 0) || (typeof data === 'object' && Object.keys(data).length === 0)) {
    return <div className="text-[#90adcb] text-sm">No data</div>;
  }
  if (type === 'bar') {
    return <ChartJSBar data={data} options={{ plugins: { legend: { display: false } } }} />;
  }
  if (type === 'line') {
    return <ChartJSLine data={data} options={{ plugins: { legend: { display: false } } }} />;
  }
  if (type === 'pie' || type === 'donut') {
    return <Doughnut data={data} options={{ plugins: { legend: { display: true } } }} />;
  }
  // Fallback: table
  if (Array.isArray(data)) {
    return (
      <table className="min-w-full text-xs text-[#acd1e9] mt-2">
        <tbody>
          {data.map((row, i) => (
            <tr key={i}>{Object.values(row).map((v, j) => <td key={j} className="px-2 py-1">{String(v)}</td>)}</tr>
          ))}
        </tbody>
      </table>
    );
  }
  if (typeof data === 'object') {
    return (
      <table className="min-w-full text-xs text-[#acd1e9] mt-2">
        <tbody>
          {Object.entries(data).map(([k, v], i) => (
            <tr key={i}><td className="font-bold pr-2">{k}</td><td>{String(v)}</td></tr>
          ))}
        </tbody>
      </table>
    );
  }
  return <div className="text-[#acd1e9]">{String(data)}</div>;
};

const DeveloperDashboard = ({ data, analysisData }: { data: any; analysisData?: any }) => {
  const aiInsights = data.realData?.aiInsights || {};
  
  return (
    <div className="space-y-8">
      {/* AI Summary */}
      {analysisData?.summary && (
        <div className="glass-card rounded-2xl p-6 mb-4">
          <h3 className="text-2xl font-bold text-gradient mb-2">🧠 Summary</h3>
          <div className="text-[#acd1e9] text-lg">{analysisData.summary}</div>
        </div>
      )}
      {/* Key Insights */}
      <div className="glass-card rounded-2xl p-6 mb-4">
        <h3 className="text-xl font-bold text-gradient mb-4">🔍 Key Insights</h3>
        <ul className="list-disc pl-6 space-y-2">
          {Object.entries(aiInsights.key_insights || {}).map(([k, v], i) => (
            <li key={i} className="text-[#acd1e9]">
              <span className="font-semibold text-white mr-2">{k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
              {typeof v === 'object' ? renderChart('table', v, k) : <span>{String(v)}</span>}
            </li>
          ))}
        </ul>
      </div>
      {/* Graphs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.entries(analysisData?.graphs_data || {}).map(([k, v], i) => (
          <div key={i} className="glass-card rounded-2xl p-6">
            <h4 className="text-lg font-bold text-gradient mb-2">{k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
            {/* Heuristic: choose chart type based on key */}
            {k.includes('bar') || k.includes('distribution') ? renderChart('bar', v, k) :
             k.includes('line') || k.includes('trend') ? renderChart('line', v, k) :
             k.includes('pie') || k.includes('donut') ? renderChart('pie', v, k) :
             k.includes('heatmap') ? renderChart('table', v, k) :
             renderChart('table', v, k)}
          </div>
        ))}
      </div>
    </div>
  );
};

const ManagerDashboard = ({ data, analysisData }: { data: any; analysisData?: any }) => {
  const aiInsights = data.realData?.aiInsights || {};
  return (
    <div className="space-y-8">
      {/* AI Summary */}
      {analysisData?.summary && (
        <div className="glass-card rounded-2xl p-6 mb-4">
          <h3 className="text-2xl font-bold text-gradient mb-2">🧠 Summary</h3>
          <div className="text-[#acd1e9] text-lg">{analysisData.summary}</div>
        </div>
      )}
      {/* Key Insights */}
      <div className="glass-card rounded-2xl p-6 mb-4">
        <h3 className="text-xl font-bold text-gradient mb-4">🔍 Key Insights</h3>
        <ul className="list-disc pl-6 space-y-2">
          {Object.entries(aiInsights.key_insights || {}).map(([k, v], i) => (
            <li key={i} className="text-[#acd1e9]">
              <span className="font-semibold text-white mr-2">{k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
              {typeof v === 'object' ? renderChart('table', v, k) : <span>{String(v)}</span>}
            </li>
          ))}
        </ul>
      </div>
      {/* Graphs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.entries(analysisData?.graphs_data || {}).map(([k, v], i) => (
          <div key={i} className="glass-card rounded-2xl p-6">
            <h4 className="text-lg font-bold text-gradient mb-2">{k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
            {/* Heuristic: choose chart type based on key */}
            {k.includes('bar') || k.includes('distribution') ? renderChart('bar', v, k) :
             k.includes('line') || k.includes('trend') ? renderChart('line', v, k) :
             k.includes('pie') || k.includes('donut') ? renderChart('pie', v, k) :
             k.includes('heatmap') ? renderChart('table', v, k) :
             renderChart('table', v, k)}
          </div>
        ))}
      </div>
    </div>
  );
};

const ProductManagerDashboard = ({ data, analysisData }: { data: any; analysisData?: any }) => {
  const aiInsights = data.realData?.aiInsights || {};
  return (
    <div className="space-y-8">
      {/* AI Summary */}
      {analysisData?.summary && (
        <div className="glass-card rounded-2xl p-6 mb-4">
          <h3 className="text-2xl font-bold text-gradient mb-2">🧠 Summary</h3>
          <div className="text-[#acd1e9] text-lg">{analysisData.summary}</div>
        </div>
      )}
      {/* Key Insights */}
      <div className="glass-card rounded-2xl p-6 mb-4">
        <h3 className="text-xl font-bold text-gradient mb-4">🔍 Key Insights</h3>
        <ul className="list-disc pl-6 space-y-2">
          {Object.entries(aiInsights.key_insights || {}).map(([k, v], i) => (
            <li key={i} className="text-[#acd1e9]">
              <span className="font-semibold text-white mr-2">{k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
              {typeof v === 'object' ? renderChart('table', v, k) : <span>{String(v)}</span>}
            </li>
          ))}
        </ul>
      </div>
      {/* Graphs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.entries(analysisData?.graphs_data || {}).map(([k, v], i) => (
          <div key={i} className="glass-card rounded-2xl p-6">
            <h4 className="text-lg font-bold text-gradient mb-2">{k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
            {/* Heuristic: choose chart type based on key */}
            {k.includes('bar') || k.includes('distribution') ? renderChart('bar', v, k) :
             k.includes('line') || k.includes('trend') ? renderChart('line', v, k) :
             k.includes('pie') || k.includes('donut') ? renderChart('pie', v, k) :
             k.includes('heatmap') ? renderChart('table', v, k) :
             renderChart('table', v, k)}
          </div>
        ))}
      </div>
    </div>
  );
};

const QAManagerDashboard = ({ data, analysisData }: { data: any; analysisData?: any }) => {
  const aiInsights = data.realData?.aiInsights || {};
  return (
    <div className="space-y-8">
      {/* AI Summary */}
      {analysisData?.summary && (
        <div className="glass-card rounded-2xl p-6 mb-4">
          <h3 className="text-2xl font-bold text-gradient mb-2">🧠 Summary</h3>
          <div className="text-[#acd1e9] text-lg">{analysisData.summary}</div>
        </div>
      )}
      {/* Key Insights */}
      <div className="glass-card rounded-2xl p-6 mb-4">
        <h3 className="text-xl font-bold text-gradient mb-4">🔍 Key Insights</h3>
        <ul className="list-disc pl-6 space-y-2">
          {Object.entries(aiInsights.key_insights || {}).map(([k, v], i) => (
            <li key={i} className="text-[#acd1e9]">
              <span className="font-semibold text-white mr-2">{k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
              {typeof v === 'object' ? renderChart('table', v, k) : <span>{String(v)}</span>}
            </li>
          ))}
        </ul>
      </div>
      {/* Graphs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.entries(analysisData?.graphs_data || {}).map(([k, v], i) => (
          <div key={i} className="glass-card rounded-2xl p-6">
            <h4 className="text-lg font-bold text-gradient mb-2">{k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
            {/* Heuristic: choose chart type based on key */}
            {k.includes('bar') || k.includes('distribution') ? renderChart('bar', v, k) :
             k.includes('line') || k.includes('trend') ? renderChart('line', v, k) :
             k.includes('pie') || k.includes('donut') ? renderChart('pie', v, k) :
             k.includes('heatmap') ? renderChart('table', v, k) :
             renderChart('table', v, k)}
          </div>
        ))}
      </div>
    </div>
  );
};

const ExecutiveDashboard = ({ data, analysisData }: { data: any; analysisData?: any }) => {
  const aiInsights = data.realData?.aiInsights || {};
  return (
    <div className="space-y-8">
      {/* AI Summary */}
      {analysisData?.summary && (
        <div className="glass-card rounded-2xl p-6 mb-4">
          <h3 className="text-2xl font-bold text-gradient mb-2">🧠 Summary</h3>
          <div className="text-[#acd1e9] text-lg">{analysisData.summary}</div>
        </div>
      )}
      {/* Key Insights */}
      <div className="glass-card rounded-2xl p-6 mb-4">
        <h3 className="text-xl font-bold text-gradient mb-4">🔍 Key Insights</h3>
        <ul className="list-disc pl-6 space-y-2">
          {Object.entries(aiInsights.key_insights || {}).map(([k, v], i) => (
            <li key={i} className="text-[#acd1e9]">
              <span className="font-semibold text-white mr-2">{k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
              {typeof v === 'object' ? renderChart('table', v, k) : <span>{String(v)}</span>}
            </li>
          ))}
        </ul>
      </div>
      {/* Graphs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.entries(analysisData?.graphs_data || {}).map(([k, v], i) => (
          <div key={i} className="glass-card rounded-2xl p-6">
            <h4 className="text-lg font-bold text-gradient mb-2">{k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
            {/* Heuristic: choose chart type based on key */}
            {k.includes('bar') || k.includes('distribution') ? renderChart('bar', v, k) :
             k.includes('line') || k.includes('trend') ? renderChart('line', v, k) :
             k.includes('pie') || k.includes('donut') ? renderChart('pie', v, k) :
             k.includes('heatmap') ? renderChart('table', v, k) :
             renderChart('table', v, k)}
          </div>
        ))}
      </div>
    </div>
  );
};

const RoleBasedDashboard: React.FC<RoleBasedDashboardProps> = ({ role, analysisData }) => {
  if (!analysisData) return null;
  const { key_insights = {}, graphs_data = {} } = analysisData.insights || {};
  const summary = analysisData.summary;

  const renderDashboard = () => {
    switch (role) {
      case 'developer':
        return <DeveloperDashboard data={processGitHubData(analysisData)} analysisData={analysisData} />;
      case 'em':
        return <ManagerDashboard data={processGitHubData(analysisData)} analysisData={analysisData} />;
      case 'pm':
        return <ProductManagerDashboard data={processGitHubData(analysisData)} analysisData={analysisData} />;
      case 'qa':
        return <QAManagerDashboard data={processGitHubData(analysisData)} analysisData={analysisData} />;
      case 'executive':
        return <ExecutiveDashboard data={processGitHubData(analysisData)} analysisData={analysisData} />;
      case 'tpm':
      case 'scrum':
      case 'ux':
        return <ManagerDashboard data={processGitHubData(analysisData)} analysisData={analysisData} />; // Using manager dashboard as fallback
      default:
        return <DeveloperDashboard data={processGitHubData(analysisData)} analysisData={analysisData} />;
    }
  };

  return (
    <div className="space-y-8">
      {renderDashboard()}
    </div>
  );
};

export default RoleBasedDashboard; 