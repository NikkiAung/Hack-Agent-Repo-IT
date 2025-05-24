"use client";

import React from "react";
import CommitAnalytics from "@/components/dashboard/commit-analytics";
import CodeHealth from "@/components/dashboard/code-health";
import RiskIndicators from "@/components/dashboard/risk-indicators";
import KnowledgeDiscovery from "@/components/dashboard/knowledge-discovery";

const DashboardPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e13] via-[#1a1e23] to-[#0f1419] text-white">
      {/* Header */}
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-[#add1ea] to-[#7dd3fc] bg-clip-text text-transparent mb-2">
            Analytics Dashboard
          </h1>
          <p className="text-lg text-gray-400">
            Comprehensive insights into your repository's health, performance, and risk factors
          </p>
        </div>

        {/* Dashboard Components */}
        <div className="space-y-8">
          <CommitAnalytics />
          <CodeHealth />
          <RiskIndicators />
          <KnowledgeDiscovery />
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;