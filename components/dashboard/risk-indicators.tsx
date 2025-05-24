import React from "react";

const RiskIndicators = () => {
  return (
    <section className="mb-8">
      <h2 className="text-2xl font-semibold mb-4 text-[#add1ea]">
        Risk & Vulnerability Indicators
      </h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Security Vulnerabilities */}
        <div className="bg-card rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-medium mb-4">Security Vulnerabilities</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
              <div className="flex items-center">
                <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center mr-3">
                  <svg className="w-4 h-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div>
                  <div className="font-medium">Critical Vulnerability</div>
                  <div className="text-sm text-card-foreground/70">Outdated dependency: react-router v5.2.0</div>
                </div>
              </div>
              <div className="text-red-500 font-medium">CVE-2021-27536</div>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
              <div className="flex items-center">
                <div className="w-8 h-8 rounded-full bg-yellow-500/20 flex items-center justify-center mr-3">
                  <svg className="w-4 h-4 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div>
                  <div className="font-medium">Medium Vulnerability</div>
                  <div className="text-sm text-card-foreground/70">Insecure configuration in webpack.config.js</div>
                </div>
              </div>
              <div className="text-yellow-500 font-medium">GHSA-7jgj-8wvc</div>
            </div>
          </div>
          <div className="mt-4 text-sm text-right">
            <a href="#" className="text-[#add1ea] hover:underline">View all 5 vulnerabilities →</a>
          </div>
        </div>

        {/* Risk Assessment */}
        <div className="bg-card rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-medium mb-4">Risk Assessment</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-[#1a1e22] rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-yellow-500 mb-1">Medium</div>
              <div className="text-sm text-card-foreground/70">Overall Risk Level</div>
            </div>
            <div className="bg-[#1a1e22] rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-[#add1ea] mb-1">7.2/10</div>
              <div className="text-sm text-card-foreground/70">Risk Score</div>
            </div>
            <div className="bg-[#1a1e22] rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-green-500 mb-1">85%</div>
              <div className="text-sm text-card-foreground/70">Compliance Rate</div>
            </div>
            <div className="bg-[#1a1e22] rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-red-500 mb-1">3</div>
              <div className="text-sm text-card-foreground/70">Critical Issues</div>
            </div>
          </div>
          <div className="mt-6">
            <h4 className="font-medium mb-2">Risk Factors</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span>Dependency Vulnerabilities</span>
                <div className="w-24 bg-[#2b3136] rounded-full h-2">
                  <div className="bg-red-500 h-2 rounded-full" style={{ width: "80%" }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span>Code Quality</span>
                <div className="w-24 bg-[#2b3136] rounded-full h-2">
                  <div className="bg-yellow-500 h-2 rounded-full" style={{ width: "60%" }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span>Test Coverage</span>
                <div className="w-24 bg-[#2b3136] rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: "75%" }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default RiskIndicators;