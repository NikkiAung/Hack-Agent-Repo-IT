import KeyAlerts from "@/components/welcome-home/key-alerts";
import RecentActivity from "@/components/welcome-home/recent-activity";
import Shortcuts from "@/components/welcome-home/shortcuts";
import RepositoryHealthSnapshot from "@/components/welcome-home/repository-health-snapshot";
import { auth } from "@/server/auth";

export default async function Home() {
  const session = await auth();
  return (
    <main className="py-8">
      {/* Hero Section with Enhanced Styling */}
      <div className="relative mb-12">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-indigo-600/20 rounded-3xl blur-xl" />
        <div className="relative glass-card rounded-3xl p-8 hover-lift">
          <h2 className="text-5xl font-bold tracking-tight mb-4 text-gradient">
            {session?.user.name
              ? `Welcome back, ${session?.user.name}!`
              : "Welcome to Genini!"}
          </h2>
          <p className="text-xl text-muted-foreground">
            Here's your personalized overview of GitHub.
          </p>
          <div className="mt-6 flex items-center gap-4">
            <div className="h-1 w-20 bg-gradient-to-r from-primary to-accent rounded-full" />
            <div className="h-1 w-12 bg-gradient-to-r from-accent to-chart-2 rounded-full" />
            <div className="h-1 w-8 bg-gradient-to-r from-chart-2 to-chart-3 rounded-full" />
          </div>
        </div>
      </div>

      {/* Enhanced Key Alerts */}
      <div className="mb-12">
        <KeyAlerts />
      </div>

      {/* Grid Layout with Enhanced Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        <div className="glass-card rounded-2xl p-1 hover-lift glow-blue">
          <div className="bg-card/50 rounded-2xl p-6 h-full">
            <RecentActivity />
          </div>
        </div>
        <div className="glass-card rounded-2xl p-1 hover-lift glow-accent">
          <div className="bg-card/50 rounded-2xl p-6 h-full">
            <Shortcuts />
          </div>
        </div>
      </div>

      {/* Repository Health with Enhanced Styling */}
      <div className="mb-12">
        <RepositoryHealthSnapshot />
      </div>

      {/* Enhanced AI Agent Button */}
      <div className="fixed bottom-8 right-8 z-40">
        <button
          aria-label="Chat with AI Agent"
          className="group relative flex items-center justify-center gap-3 h-16 px-8 bg-gradient-to-r from-primary to-accent text-primary-foreground rounded-2xl shadow-2xl hover:shadow-primary/25 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background focus:ring-primary transition-all duration-300 animate-pulse-glow hover-lift"
        >
          {/* Animated background */}
          <div className="absolute inset-0 bg-gradient-to-r from-primary/80 to-accent/80 rounded-2xl blur-sm group-hover:blur-md transition-all duration-300" />

          {/* Content */}
          <div className="relative flex items-center gap-3">
            <svg
              className="h-7 w-7 transform group-hover:rotate-12 group-hover:scale-110 transition-transform duration-300"
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
              />
            </svg>
            <span className="text-lg font-bold tracking-wide">AI Agent</span>
          </div>

          {/* Floating particles effect */}
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-accent rounded-full animate-ping" />
          <div
            className="absolute -bottom-1 -left-1 w-2 h-2 bg-primary rounded-full animate-ping"
            style={{ animationDelay: "1s" }}
          />
        </button>
      </div>
    </main>
  );
}
