import React from "react";

const RecentActivity = () => {
  return (
    <section>
      <h3 className="text-2xl font-semibold mb-4 text-[#add1ea]">
        Recent Activity
      </h3>
      <div className="space-y-4">
        <div className="flex items-center p-4 bg-[#1a1e22] rounded-lg shadow hover:bg-[#20252a] transition-colors duration-200">
          <div className="flex-shrink-0 flex items-center justify-center h-10 w-10 rounded-full bg-[#2b3136] text-blue-400 mr-4">
            <svg
              fill="currentColor"
              height="20px"
              viewBox="0 0 256 256"
              width="20px"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M248,120H183.42a56,56,0,0,0-110.84,0H8a8,8,0,0,0,0,16H72.58a56,56,0,0,0,110.84,0H248a8,8,0,0,0,0-16ZM128,168a40,40,0,1,1,40-40A40,40,0,0,1,128,168Z"></path>
            </svg>
          </div>
          <div>
            <p className="text-white font-medium">
              Updated README.md in project-alpha
            </p>
            <p className="text-sm text-[#a1adb5]">2 hours ago</p>
          </div>
        </div>
        <div className="flex items-center p-4 bg-[#1a1e22] rounded-lg shadow hover:bg-[#20252a] transition-colors duration-200">
          <div className="flex-shrink-0 flex items-center justify-center h-10 w-10 rounded-full bg-[#2b3136] text-blue-400 mr-4">
            <svg
              fill="currentColor"
              height="20px"
              viewBox="0 0 256 256"
              width="20px"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M248,120H183.42a56,56,0,0,0-110.84,0H8a8,8,0,0,0,0,16H72.58a56,56,0,0,0,110.84,0H248a8,8,0,0,0,0-16ZM128,168a40,40,0,1,1,40-40A40,40,0,0,1,128,168Z"></path>
            </svg>
          </div>
          <div>
            <p className="text-white font-medium">
              Fixed bug #123 in project-beta
            </p>
            <p className="text-sm text-[#a1adb5]">3 hours ago</p>
          </div>
        </div>
        <div className="flex items-center p-4 bg-[#1a1e22] rounded-lg shadow hover:bg-[#20252a] transition-colors duration-200">
          <div className="flex-shrink-0 flex items-center justify-center h-10 w-10 rounded-full bg-[#2b3136] text-green-400 mr-4">
            <svg
              fill="currentColor"
              height="20px"
              viewBox="0 0 256 256"
              width="20px"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M224,80H176V56a8,8,0,0,0-8-8H88a8,8,0,0,0-6.4,3.2L64,72H40a8,8,0,0,0-8,8V192a8,8,0,0,0,8,8H72.25a47.92,47.92,0,0,0,95.5,0H200a32,32,0,0,0,32-32V88A8,8,0,0,0,224,80ZM80,176a32,32,0,1,1,32-32A32,32,0,0,1,80,176Zm144-16a16,16,0,0,1-16,16H176a47.87,47.87,0,0,0-32-42.16V120H216a8,8,0,0,0,0-16H144V80h24V64h40ZM88,64h72v8H88Zm0,16h40v8H88Zm0,16h24v8H88Z"></path>
            </svg>
          </div>
          <div>
            <p className="text-white font-medium">
              Opened PR for new feature in project-gamma
            </p>
            <p className="text-sm text-[#a1adb5]">5 hours ago</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default RecentActivity;
