import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import AppNav from "@/components/navigation/app-nav";
import Footer from "@/components/navigation/footer";
import AiAgentChatbot from "@/components/chatbot/ai-agent-chatbot";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Genini - AI-Powered Repository Analytics",
  description: "Advanced repository analytics and insights powered by AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen`}
      >
        {/* Background effects */}
        <div className="fixed inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-950/20 via-slate-900/40 to-indigo-950/30" />
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
          <div
            className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse"
            style={{ animationDelay: "2s" }}
          />
        </div>

        <div className="relative z-10">
          <div className="max-w-7xl mx-auto px-6 lg:px-8">
            <AppNav />
            <section className="min-h-screen">{children}</section>
            <Toaster position="top-center" richColors closeButton />
          </div>
          <Footer />
        </div>
        {/* Enhanced AI Agent Button */}
        <AiAgentChatbot apiEndpoint={"dummy-point"} apiKey={"dummy-key"} />
      </body>
    </html>
  );
}
