import KeyAlerts from "@/components/welcome-home/key-alerts";
import RecentActivity from "@/components/welcome-home/recent-activity";
import Shortcuts from "@/components/welcome-home/shortcuts";
import RepositoryHealthSnapshot from "@/components/welcome-home/repository-health-snapshot";

export default function Home() {
  return (
    <main>
      <div>
        <h2 className="text-4xl font-bold tracking-tight mb-2">
          Welcome back, User!
        </h2>
        <p className="text-lg text-[#a1adb5]">
          Here's your personalized overview of GitHub.
        </p>
      </div>
      <KeyAlerts />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
        <RecentActivity />
        <Shortcuts />
      </div>

      <RepositoryHealthSnapshot />

      <div className="fixed bottom-8 right-8 z-40">
        <button
          aria-label="Chat with AI Agent"
          className="flex items-center justify-center gap-2 h-14 px-6 bg-[#add1ea] text-[#121517] rounded-full shadow-xl hover:bg-[#9cbcd3] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#121517] focus:ring-[#add1ea] transition-all duration-300 group"
        >
          <svg
            className="h-6 w-6 transform group-hover:rotate-12 transition-transform"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-3.862 8.25-8.625 8.25S3.75 16.556 3.75 12 7.612 3.75 12.375 3.75 21 7.444 21 12z"
              strokeLinecap="round"
              strokeLinejoin="round"
            ></path>
          </svg>
          <span className="text-base font-bold tracking-wide">AI Agent</span>
        </button>
      </div>
    </main>
  );
}
