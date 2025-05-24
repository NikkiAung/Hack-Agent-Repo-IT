import React from "react";

const RepositoryHealthSnapshot = () => {
  return (
    <section className="mb-10">
      <h3 className="text-2xl font-semibold mb-4 text-[#add1ea]">
        Repository Health Snapshot
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-[#1a1e22] rounded-xl shadow-lg p-6 hover:shadow-[#add1ea]/15 transition-shadow duration-300">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-lg font-semibold text-white">
              Project Alpha
            </h4>
            <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-green-500/20 text-green-400">
              95% Health
            </span>
          </div>
          <div className="w-full bg-[#2b3136] rounded-full h-2.5 mb-4">
            <div
              className="bg-green-500 h-2.5 rounded-full"
              style={{ width: "95%" }}
            ></div>
          </div>
          <div className="flex justify-between text-sm text-[#a1adb5]">
            <span>
              <span className="font-bold text-white">2</span> Open Issues
            </span>
            <span>
              <span className="font-bold text-white">1</span> Open PRs
            </span>
          </div>
        </div>
        <div className="bg-[#1a1e22] rounded-xl shadow-lg p-6 hover:shadow-[#add1ea]/15 transition-shadow duration-300">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-lg font-semibold text-white">Project Beta</h4>
            <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-yellow-500/20 text-yellow-400">
              78% Health
            </span>
          </div>
          <div className="w-full bg-[#2b3136] rounded-full h-2.5 mb-4">
            <div
              className="bg-yellow-500 h-2.5 rounded-full"
              style={{ width: "78%" }}
            ></div>
          </div>
          <div className="flex justify-between text-sm text-[#a1adb5]">
            <span>
              <span className="font-bold text-white">15</span> Open Issues
            </span>
            <span>
              <span className="font-bold text-white">5</span> Open PRs
            </span>
          </div>
        </div>
        <div className="bg-[#1a1e22] rounded-xl shadow-lg p-6 hover:shadow-[#add1ea]/15 transition-shadow duration-300">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-lg font-semibold text-white">
              Legacy System
            </h4>
            <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-red-500/20 text-red-400">
              45% Health
            </span>
          </div>
          <div className="w-full bg-[#2b3136] rounded-full h-2.5 mb-4">
            <div
              className="bg-red-500 h-2.5 rounded-full"
              style={{ width: "45%" }}
            ></div>
          </div>
          <div className="flex justify-between text-sm text-[#a1adb5]">
            <span>
              <span className="font-bold text-white">50</span> Open Issues
            </span>
            <span>
              <span className="font-bold text-white">0</span> Open PRs
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default RepositoryHealthSnapshot;
