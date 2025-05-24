import React from "react";

const CommitAnalytics = () => {
  return (
    <section className="mb-8">
      <h2 className="text-2xl font-semibold mb-4 text-[#add1ea]">
        Commit & Contributor Analytics
      </h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Commit Frequency Chart */}
        <div className="bg-card rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-medium mb-4">Commit Frequency</h3>
          <div className="aspect-[4/3] bg-[#1a1e22] rounded-lg flex items-center justify-center">
            <div className="h-4/5 w-4/5 relative">
              {/* Placeholder for commit frequency chart */}
              <div className="absolute bottom-0 left-0 w-full h-full flex items-end">
                {[40, 65, 30, 85, 55, 70, 45].map((height, index) => (
                  <div 
                    key={index} 
                    className="flex-1 mx-1"
                    style={{ height: `${height}%` }}
                  >
                    <div 
                      className="w-full rounded-t-sm" 
                      style={{ 
                        height: '100%', 
                        backgroundColor: `hsl(var(--chart-${(index % 5) + 1}))` 
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="mt-4 text-sm text-card-foreground/70">
            <p>Average: <span className="font-medium">12.5 commits/day</span></p>
            <p>Trend: <span className="text-green-500">↑ 8% from last month</span></p>
          </div>
        </div>

        {/* Contributor Activity */}
        <div className="bg-card rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-medium mb-4">Contributor Activity</h3>
          <div className="aspect-[4/3] bg-[#1a1e22] rounded-lg flex items-center justify-center">
            <div className="h-4/5 w-4/5 relative">
              {/* Placeholder for contributor pie chart */}
              <div className="w-full h-full flex items-center justify-center">
                <div className="w-32 h-32 rounded-full border-8 border-[hsl(var(--chart-1))] relative">
                  <div className="absolute top-0 left-0 w-full h-full rounded-full border-8 border-transparent border-t-[hsl(var(--chart-2))] border-r-[hsl(var(--chart-2))] rotate-45"></div>
                  <div className="absolute top-0 left-0 w-full h-full rounded-full border-8 border-transparent border-b-[hsl(var(--chart-3))] rotate-[190deg]"></div>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-[hsl(var(--chart-1))] mr-2"></span>
              <span>John Doe (45%)</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-[hsl(var(--chart-2))] mr-2"></span>
              <span>Jane Smith (30%)</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-[hsl(var(--chart-3))] mr-2"></span>
              <span>Others (25%)</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CommitAnalytics;