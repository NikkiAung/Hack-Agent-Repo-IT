import React from "react";

const KeyAlerts = () => {
  return (
    <section className="mb-10">
      <h3 className="text-2xl font-semibold mb-4 text-[#add1ea]">
        Key Alerts
      </h3>
      <div className="bg-[#1a1e22] rounded-xl shadow-lg p-6 flex flex-col md:flex-row items-center gap-6 hover:shadow-[#add1ea]/20 transition-shadow duration-300">
        <div className="flex-shrink-0">
          <svg
            className="h-16 w-16 text-red-500"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 9v3.75m0-10.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.75c0 5.592 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.57-.598-3.75h-.152c-3.196 0-6.1-1.249-8.25-3.286zm0 13.036h.008v.008H12v-.008z"
              strokeLinecap="round"
              strokeLinejoin="round"
            ></path>
          </svg>
        </div>
        <div className="flex-1">
          <p className="text-xl font-bold text-white">
            100+ New Security Alerts
          </p>
          <p className="text-[#a1adb5] mt-1">
            Critical vulnerabilities found in your repositories. Review them
            now.
          </p>
        </div>
        <a
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-[#121517] bg-[#add1ea] hover:bg-[#9cbcd3] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#1a1e22] focus:ring-[#add1ea]"
          href="#"
        >
          View Alerts
          <svg
            aria-hidden="true"
            className="ml-2 -mr-1 h-5 w-5"
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              clipRule="evenodd"
              d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z"
              fillRule="evenodd"
            ></path>
          </svg>
        </a>
      </div>
    </section>
  );
};

export default KeyAlerts;
