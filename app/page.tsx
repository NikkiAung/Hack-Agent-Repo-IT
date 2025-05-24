import KeyAlerts from "@/components/welcome-home/key-alerts";
import RecentActivity from "@/components/welcome-home/recent-activity";
import Shortcuts from "@/components/welcome-home/shortcuts";
import RepositoryHealthSnapshot from "@/components/welcome-home/repository-health-snapshot";
import { auth } from "@/server/auth";
import SplitText from "./components/SplitText/SplitText";
import BlurText from "./components/BlurText/BlurText";

export default async function Home() {
  const session = await auth();
  return (
    <main className="py-8">
      {/* Hero Section with Enhanced Styling */}
      <div className="relative mb-12">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-indigo-600/20 rounded-3xl blur-xl" />
        <div className="relative glass-card rounded-3xl p-8 hover-lift">
          <SplitText
            text={
              session?.user.name
                ? `Welcome back, ${session?.user.name}!`
                : "Welcome to Genini!"
            }
            className="text-5xl font-semibold text-center mb-6"
            delay={150}
            animationFrom={{ opacity: 0, transform: "translate3d(0,50px,0)" }}
            animationTo={{ opacity: 1, transform: "translate3d(0,0,0)" }}
            easing="easeOutCubic"
            threshold={0.2}
            rootMargin="-50px"
          />
          <BlurText
            text="Here's your personalized overview of GitHub."
            delay={150}
            animateBy="words"
            direction="top"
            className="text-xl text-muted-foreground"
          />
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
    </main>
  );
}
