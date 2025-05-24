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
    </main>
  );
}
