import React from "react";

const KnowledgeDiscovery = () => {
  return (
    <section className="mb-8">
      <h2 className="text-2xl font-semibold mb-4 text-[#add1ea]">
        Knowledge Discovery
      </h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Code Expertise Map */}
        <div className="bg-card rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-medium mb-4">Code Expertise Map</h3>
          <div className="aspect-[4/3] bg-[#1a1e22] rounded-lg p-4">
            <div className="w-full h-full relative">
              {/* Placeholder for expertise map visualization */}
              <div className="absolute inset-0 flex flex-wrap justify-center items-center gap-3 p-4">
                {[
                  { name: "Frontend", size: "large", color: "chart-1" },
                  { name: "API", size: "medium", color: "chart-2" },
                  { name: "Database", size: "medium", color: "chart-3" },
                  { name: "Auth", size: "small", color: "chart-4" },
                  { name: "Utils", size: "small", color: "chart-5" },
                  { name: "Testing", size: "medium", color: "chart-1" },
                  { name: "Config", size: "small", color: "chart-2" },
                  { name: "State", size: "medium", color: "chart-3" },
                ].map((item, index) => {
                  const sizeClass = 
                    item.size === "large" ? "text-xl p-4" : 
                    item.size === "medium" ? "text-base p-3" : "text-sm p-2";
                  
                  return (
                    <div 
                      key={index}
                      className={`rounded-full ${sizeClass} font-medium`}
                      style={{ backgroundColor: `hsl(var(--${item.color})/0.2)`, color: `hsl(var(--${item.color}))` }}
                    >
                      {item.name}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
          <div className="mt-4 text-sm">
            <p>Primary expertise areas based on commit history and code ownership.</p>
          </div>
        </div>

        {/* Knowledge Gaps */}
        <div className="bg-card rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-medium mb-4">Knowledge Gaps & Documentation</h3>
          <div className="space-y-3">
            <div className="p-3 bg-[#1a1e22] rounded-lg">
              <div className="flex justify-between">
                <span className="font-medium">Authentication Flow</span>
                <span className="text-red-400">No Documentation</span>
              </div>
              <div className="text-sm text-card-foreground/70 mt-1">
                Complex code with single maintainer (John Doe)
              </div>
            </div>
            <div className="p-3 bg-[#1a1e22] rounded-lg">
              <div className="flex justify-between">
                <span className="font-medium">Payment Processing</span>
                <span className="text-yellow-400">Outdated Docs</span>
              </div>
              <div className="text-sm text-card-foreground/70 mt-1">
                Documentation last updated 8 months ago
              </div>
            </div>
            <div className="p-3 bg-[#1a1e22] rounded-lg">
              <div className="flex justify-between">
                <span className="font-medium">API Endpoints</span>
                <span className="text-green-400">Well Documented</span>
              </div>
              <div className="text-sm text-card-foreground/70 mt-1">
                OpenAPI spec up-to-date with 100% coverage
              </div>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-[#2b3136]">
            <h4 className="font-medium mb-2">Documentation Health</h4>
            <div className="flex items-center">
              <div className="w-full bg-[#2b3136] rounded-full h-2.5 mr-2">
                <div className="bg-yellow-500 h-2.5 rounded-full" style={{ width: "65%" }}></div>
              </div>
              <span className="text-sm font-medium">65%</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default KnowledgeDiscovery;