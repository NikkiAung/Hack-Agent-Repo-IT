import React from "react";

const CodeHealth = () => {
  return (
    <section className="mb-8">
      <h2 className="text-2xl font-semibold mb-4 text-[#add1ea]">
        Code Health, Churn & Hotspots
      </h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Code Quality Metrics */}
        <div className="bg-card rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-medium mb-4">Code Quality Metrics</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1">
                <span>Test Coverage</span>
                <span className="font-medium">78%</span>
              </div>
              <div className="w-full bg-[#2b3136] rounded-full h-2">
                <div className="bg-[hsl(var(--chart-1))] h-2 rounded-full" style={{ width: "78%" }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span>Code Duplication</span>
                <span className="font-medium">12%</span>
              </div>
              <div className="w-full bg-[#2b3136] rounded-full h-2">
                <div className="bg-[hsl(var(--chart-2))] h-2 rounded-full" style={{ width: "12%" }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span>Technical Debt</span>
                <span className="font-medium">Medium</span>
              </div>
              <div className="w-full bg-[#2b3136] rounded-full h-2">
                <div className="bg-[hsl(var(--chart-3))] h-2 rounded-full" style={{ width: "50%" }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Code Churn */}
        <div className="bg-card rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-medium mb-4">Code Churn</h3>
          <div className="aspect-[4/3] bg-[#1a1e22] rounded-lg flex items-center justify-center">
            <div className="h-4/5 w-4/5 relative">
              {/* Placeholder for code churn line chart */}
              <div className="absolute inset-0">
                <svg viewBox="0 0 100 100" className="w-full h-full">
                  <polyline
                    points="0,70 15,65 30,60 45,40 60,45 75,30 90,20 100,25"
                    fill="none"
                    stroke="hsl(var(--chart-2))"
                    strokeWidth="2"
                  />
                  <polyline
                    points="0,50 15,55 30,45 45,30 60,35 75,40 90,30 100,35"
                    fill="none"
                    stroke="hsl(var(--chart-1))"
                    strokeWidth="2"
                  />
                </svg>
              </div>
            </div>
          </div>
          <div className="mt-2 text-sm">
            <div className="flex justify-between">
              <div className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-[hsl(var(--chart-1))] mr-2"></span>
                <span>Added</span>
              </div>
              <div className="flex items-center">
                <span className="w-3 h-3 rounded-full bg-[hsl(var(--chart-2))] mr-2"></span>
                <span>Deleted</span>
              </div>
            </div>
          </div>
        </div>

        {/* Code Hotspots */}
        <div className="bg-card rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-medium mb-4">Code Hotspots</h3>
          <div className="space-y-3">
            <div className="p-3 bg-[#1a1e22] rounded-lg">
              <div className="flex justify-between">
                <span className="font-medium">src/api/auth.ts</span>
                <span className="text-yellow-400">High</span>
              </div>
              <div className="text-sm text-card-foreground/70 mt-1">
                48 changes in last 7 days
              </div>
            </div>
            <div className="p-3 bg-[#1a1e22] rounded-lg">
              <div className="flex justify-between">
                <span className="font-medium">src/components/form.tsx</span>
                <span className="text-red-400">Critical</span>
              </div>
              <div className="text-sm text-card-foreground/70 mt-1">
                72 changes in last 7 days
              </div>
            </div>
            <div className="p-3 bg-[#1a1e22] rounded-lg">
              <div className="flex justify-between">
                <span className="font-medium">src/utils/helpers.ts</span>
                <span className="text-green-400">Low</span>
              </div>
              <div className="text-sm text-card-foreground/70 mt-1">
                12 changes in last 7 days
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CodeHealth;