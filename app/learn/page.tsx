"use client";
import React, { useState, useEffect, useRef } from "react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
// @ts-ignore: No types for uuid in some setups
import { v4 as uuidv4 } from 'uuid';
import Confetti from 'react-confetti';

interface Chapter {
  id: number;
  title: string;
  description: string;
  tasks: string[];
  tips: string[];
  next_steps: string;
}

interface LearningPath {
  overall_progress: number;
  chapters: Chapter[];
}

const roles = [
  { id: 'developer', name: 'Developer', icon: '🧑‍💻' },
  { id: 'em', name: 'Engineering Manager', icon: '👨‍💼' },
  { id: 'tpm', name: 'Technical Program Manager', icon: '🧑‍💼' },
  { id: 'pm', name: 'Product Manager', icon: '📋' },
  { id: 'qa', name: 'QA Manager', icon: '🧪' },
  { id: 'scrum', name: 'Scrum Master', icon: '🧑‍🏫' },
  { id: 'ux', name: 'UX Designer', icon: '🧑‍🎨' },
  { id: 'executive', name: 'Executive/Director', icon: '💼' }
];

const Learn = () => {
  const [learningPath, setLearningPath] = useState<LearningPath | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [repoUrl, setRepoUrl] = useState("");
  const [experienceLevel, setExperienceLevel] = useState("beginner");
  const [isGenerating, setIsGenerating] = useState(false);
  const [onboardingRepoUrl, setOnboardingRepoUrl] = useState("");
  const [onboardingRole, setOnboardingRole] = useState(roles[0].id);
  const [onboardingPlan, setOnboardingPlan] = useState<any>(null);
  const [isOnboardingLoading, setIsOnboardingLoading] = useState(false);
  const [onboardingError, setOnboardingError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string>("");
  const [progress, setProgress] = useState<any>({ completed_steps: [], badges: [], streak: 0, level: 1 });
  const [codeTourSteps, setCodeTourSteps] = useState<any[]>([]);
  const [codeTourIndex, setCodeTourIndex] = useState(0);
  const [codeTourOpen, setCodeTourOpen] = useState(false);
  const [isCodeTourLoading, setIsCodeTourLoading] = useState(false);
  const [codeTourError, setCodeTourError] = useState<string | null>(null);
  const [recommendedIssues, setRecommendedIssues] = useState<any[]>([]);
  const [isRecLoading, setIsRecLoading] = useState(false);
  const [recError, setRecError] = useState<string | null>(null);
  const [quizOpen, setQuizOpen] = useState(false);
  const [quizQuestions, setQuizQuestions] = useState<any[]>([]);
  const [quizAnswers, setQuizAnswers] = useState<any>({});
  const [quizResult, setQuizResult] = useState<null | boolean>(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const [quizChapterId, setQuizChapterId] = useState<number | null>(null);
  const [levelUpOpen, setLevelUpOpen] = useState(false);
  const [badgeEarned, setBadgeEarned] = useState<string | null>(null);
  const [streakToast, setStreakToast] = useState<string | null>(null);
  const prevProgress = useRef<any>({ level: 1, badges: [], streak: 0 });

  // On mount, set userId
  useEffect(() => {
    let storedId = localStorage.getItem('onboarding_user_id') || '';
    if (!storedId) {
      storedId = uuidv4();
      localStorage.setItem('onboarding_user_id', storedId);
    }
    setUserId(storedId);
    fetchProgress(storedId);
  }, []);

  // Fetch learning path on mount
  useEffect(() => {
    fetchLearningPath();
  }, []);

  // On progress update, check for level up, new badge, or streak
  useEffect(() => {
    if (!progress) return;
    // Level up
    if (progress.level > prevProgress.current.level) {
      setLevelUpOpen(true);
      setShowConfetti(true);
      setTimeout(() => { setLevelUpOpen(false); setShowConfetti(false); }, 3500);
    }
    // New badge
    const newBadges = progress.badges?.filter((b: string) => !prevProgress.current.badges.includes(b));
    if (newBadges && newBadges.length > 0) {
      setBadgeEarned(newBadges[0]);
      setTimeout(() => setBadgeEarned(null), 3500);
    }
    // Streak reminder (on page load or streak increase)
    if (progress.streak > prevProgress.current.streak) {
      setStreakToast(`🔥 Welcome back! Your streak is ${progress.streak} days!`);
      setTimeout(() => setStreakToast(null), 3500);
    }
    prevProgress.current = progress;
  }, [progress]);

  const backendUrl = "http://localhost:8000";

  const fetchLearningPath = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/learning-path`);
      if (!response.ok) {
        throw new Error("Failed to fetch learning path");
      }
      const data = await response.json();
      setLearningPath(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const generateNewLearningPath = async () => {
    if (!repoUrl.trim()) {
      alert("Please enter a GitHub repository URL");
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch(`${backendUrl}/api/generate-learning-path`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repoUrl,
          experience_level: experienceLevel,
          focus_areas: [],
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate learning path");
      }

      const result = await response.json();
      const clientId = result.client_id;

      // Poll for results
      const pollForResults = async () => {
        try {
          const resultResponse = await fetch(`${backendUrl}/api/learning-path/${clientId}`);
          if (resultResponse.ok) {
            const learningPathData = await resultResponse.json();
            setLearningPath(learningPathData);
            setIsGenerating(false);
          } else if (resultResponse.status === 404) {
            // Still generating, try again
            setTimeout(pollForResults, 2000);
          } else {
            throw new Error("Failed to get results");
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : "An error occurred");
          setIsGenerating(false);
        }
      };

      // Start polling after a short delay
      setTimeout(pollForResults, 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setIsGenerating(false);
    }
  };

  const generateOnboardingPlan = async () => {
    if (!onboardingRepoUrl.trim()) {
      alert("Please enter a GitHub repository URL");
      return;
    }
    setIsOnboardingLoading(true);
    setOnboardingError(null);
    setOnboardingPlan(null);
    try {
      const response = await fetch(`${backendUrl}/api/onboarding-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: onboardingRepoUrl, role: onboardingRole })
      });
      if (!response.ok) throw new Error("Failed to generate onboarding plan");
      const result = await response.json();
      setOnboardingPlan(result.plan);
    } catch (err) {
      setOnboardingError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsOnboardingLoading(false);
    }
  };

  const fetchProgress = async (uid: string) => {
    try {
      const resp = await fetch(`${backendUrl}/api/onboarding-progress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: uid, event: 'fetch', details: {} })
      });
      if (resp.ok) {
        setProgress(await resp.json());
      }
    } catch {}
  };

  const handleChapterExpand = async (chapterId: number) => {
    if (!userId) return;
    try {
      const resp = await fetch(`${backendUrl}/api/onboarding-progress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, event: 'completed_step', details: { step_id: chapterId } })
      });
      if (resp.ok) {
        setProgress(await resp.json());
      }
    } catch {}
  };

  const startCodeTour = async () => {
    if (!onboardingRepoUrl.trim()) {
      alert("Please enter a GitHub repository URL for the code tour");
      return;
    }
    setIsCodeTourLoading(true);
    setCodeTourError(null);
    setCodeTourSteps([]);
    setCodeTourIndex(0);
    setCodeTourOpen(true);
    try {
      const resp = await fetch(`${backendUrl}/api/code-tour`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: onboardingRepoUrl, role: onboardingRole })
      });
      if (!resp.ok) throw new Error("Failed to generate code tour");
      const result = await resp.json();
      setCodeTourSteps(result.steps || []);
    } catch (err) {
      setCodeTourError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsCodeTourLoading(false);
    }
  };

  const fetchRecommendedIssues = async () => {
    if (!onboardingRepoUrl.trim()) {
      alert("Please enter a GitHub repository URL for recommendations");
      return;
    }
    setIsRecLoading(true);
    setRecError(null);
    setRecommendedIssues([]);
    try {
      const resp = await fetch(`${backendUrl}/api/recommend-issues`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: onboardingRepoUrl, role: onboardingRole, experience_level: experienceLevel })
      });
      if (!resp.ok) throw new Error("Failed to fetch recommendations");
      const result = await resp.json();
      setRecommendedIssues(result.recommendations || []);
    } catch (err) {
      setRecError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsRecLoading(false);
    }
  };

  // Mock quiz generator (replace with AI later)
  const generateQuizForChapter = (chapter: Chapter) => [
    {
      question: `What is the main focus of "${chapter.title}"?`,
      options: [chapter.description, 'Unrelated topic', 'Another wrong answer'],
      answer: 0
    },
    {
      question: 'Is it important to read the README.md file?',
      options: ['Yes', 'No'],
      answer: 0
    }
  ];

  const openQuizForChapter = (chapter: Chapter) => {
    setQuizQuestions(generateQuizForChapter(chapter));
    setQuizAnswers({});
    setQuizResult(null);
    setQuizOpen(true);
    setQuizChapterId(chapter.id);
  };

  const submitQuiz = async () => {
    const correct = quizQuestions.every((q, i) => quizAnswers[i] === q.answer);
    setQuizResult(correct);
    if (correct && userId && quizChapterId) {
      await fetch(`${backendUrl}/api/onboarding-progress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, event: 'quiz_passed', details: { step_id: quizChapterId } })
      });
      fetchProgress(userId);
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 3000);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white text-lg">Loading learning path...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-400 text-lg">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {showConfetti && <Confetti width={window.innerWidth} height={window.innerHeight} />}
      {/* Level Up Modal */}
      {levelUpOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60">
          <div className="bg-[#1a1e22] rounded-2xl shadow-2xl p-8 max-w-md w-full flex flex-col items-center relative">
            <span className="text-5xl mb-4 animate-bounce">🎉</span>
            <div className="text-white text-3xl font-bold mb-2">Level Up!</div>
            <div className="text-[#3d98f4] text-xl font-semibold mb-2">You reached Level {progress.level}!</div>
            <button className="mt-4 px-6 py-2 bg-[#3d98f4] text-white rounded-lg font-medium hover:bg-[#2d7ce0] transition-colors" onClick={() => setLevelUpOpen(false)}>Close</button>
          </div>
        </div>
      )}
      {/* Badge Earned Modal */}
      {badgeEarned && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60">
          <div className="bg-[#1a1e22] rounded-2xl shadow-2xl p-8 max-w-md w-full flex flex-col items-center relative animate-pulse">
            <span className="text-5xl mb-4">🏅</span>
            <div className="text-white text-2xl font-bold mb-2">Badge Earned!</div>
            <div className="text-[#3d98f4] text-lg font-semibold mb-2">{badgeEarned}</div>
            <button className="mt-4 px-6 py-2 bg-[#3d98f4] text-white rounded-lg font-medium hover:bg-[#2d7ce0] transition-colors" onClick={() => setBadgeEarned(null)}>Close</button>
          </div>
        </div>
      )}
      {/* Streak Toast */}
      {streakToast && (
        <div className="fixed top-6 left-1/2 transform -translate-x-1/2 z-50">
          <div className="bg-[#223649] text-[#3d98f4] px-6 py-3 rounded-full shadow-lg font-semibold text-lg flex items-center gap-2 animate-fade-in">
            <span>🔥</span> {streakToast}
          </div>
        </div>
      )}
      <div className="container mx-auto px-4 py-8">
        <main>
          {/* Gamified Progress Tracker */}
          <section className="mb-10">
            <h2 className="text-3xl font-semibold tracking-tight mb-2">Onboarding Progress</h2>
            <div className="bg-[#1a1e22] p-6 rounded-xl shadow-lg mb-4 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-4 mb-2">
                  <span className="text-white font-bold text-lg">Level {progress.level}</span>
                  <span className="text-[#acd1e9] text-sm">Streak: {progress.streak} 🔥</span>
                </div>
                <div className="w-full bg-[#314d68] rounded-full h-3 mb-2">
                  <div
                    className="bg-[#3d98f4] h-3 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min((progress.completed_steps?.length || 0) / (learningPath?.chapters.length || 1) * 100, 100)}%` }}
                  ></div>
                </div>
                <div className="text-[#acd1e9] text-xs">{progress.completed_steps?.length || 0} / {learningPath?.chapters.length || 0} steps completed</div>
              </div>
              <div className="flex flex-col items-center">
                <div className="flex gap-2 flex-wrap">
                  {progress.badges?.map((badge: string, idx: number) => (
                    <span key={idx} className="inline-flex items-center px-3 py-1 bg-[#223649] text-[#3d98f4] rounded-full font-semibold text-sm border border-[#3d98f4]">
                      {badge === 'First PR' && '🚀'}
                      {badge === 'First Review' && '🔍'}
                      {badge === 'Quiz Master' && '🏆'}
                      {badge !== 'First PR' && badge !== 'First Review' && badge !== 'Quiz Master' && '🎖️'}
                      <span className="ml-2">{badge}</span>
                    </span>
                  ))}
                  {progress.badges?.length === 0 && <span className="text-[#90adcb] text-sm">No badges yet</span>}
                </div>
              </div>
            </div>
          </section>

          {/* Personalized Onboarding Plan Section */}
          <section className="mb-12">
            <h2 className="text-4xl font-semibold tracking-tight mb-4">
              Personalized Onboarding Plan
            </h2>
            <div className="bg-[#1a1e22] p-6 rounded-xl shadow-lg mb-8">
              <div className="space-y-4">
                <div>
                  <label className="block text-white text-sm font-medium mb-2">
                    GitHub Repository URL
                  </label>
                  <input
                    type="text"
                    value={onboardingRepoUrl}
                    onChange={(e) => setOnboardingRepoUrl(e.target.value)}
                    placeholder="https://github.com/username/repository"
                    className="w-full px-3 py-2 bg-[#223649] border border-[#314d68] rounded-lg text-white placeholder-[#90adcb] focus:outline-none focus:ring-2 focus:ring-[#3d98f4]"
                  />
                </div>
                <div>
                  <label className="block text-white text-sm font-medium mb-2">
                    Select Your Role
                  </label>
                  <select
                    value={onboardingRole}
                    onChange={(e) => setOnboardingRole(e.target.value)}
                    className="w-full px-3 py-2 bg-[#223649] border border-[#314d68] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#3d98f4]"
                  >
                    {roles.map((role) => (
                      <option key={role.id} value={role.id}>{role.icon} {role.name}</option>
                    ))}
                  </select>
                </div>
                <button
                  onClick={generateOnboardingPlan}
                  disabled={isOnboardingLoading}
                  className="px-6 py-2 bg-[#3d98f4] text-white rounded-lg font-medium hover:bg-[#2d7ce0] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isOnboardingLoading ? "Generating..." : "Generate Onboarding Plan"}
                </button>
              </div>
              {/* Onboarding Plan Output */}
              {onboardingError && (
                <div className="text-red-400 mt-4">Error: {onboardingError}</div>
              )}
              {onboardingPlan && (
                <div className="mt-8">
                  <h3 className="text-2xl font-bold text-gradient mb-4">Step-by-Step Plan</h3>
                  <ol className="list-decimal pl-6 space-y-4">
                    {onboardingPlan.steps?.map((step: any, idx: number) => (
                      <li key={idx} className="bg-[#223649] rounded-lg p-4">
                        <div className="font-semibold text-white mb-1">{step.title}</div>
                        <div className="text-[#acd1e9] mb-1">{step.description}</div>
                        {step.url && (
                          <a href={step.url} target="_blank" rel="noopener noreferrer" className="text-[#3d98f4] underline text-sm">View Resource</a>
                        )}
                      </li>
                    ))}
                  </ol>
                  {onboardingPlan.tips && onboardingPlan.tips.length > 0 && (
                    <div className="mt-6">
                      <h4 className="text-lg font-semibold mb-2 text-white">Tips</h4>
                      <ul className="list-disc pl-6 space-y-1">
                        {onboardingPlan.tips.map((tip: string, idx: number) => (
                          <li key={idx} className="text-[#acd1e9]">{tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {onboardingPlan.summary && (
                    <div className="mt-6">
                      <h4 className="text-lg font-semibold mb-2 text-white">Summary</h4>
                      <div className="text-[#acd1e9]">{onboardingPlan.summary}</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </section>

          {/* Recommended Issues Section */}
          <section className="mb-10">
            <h2 className="text-2xl font-semibold tracking-tight mb-4">Recommended for You</h2>
            <button
              onClick={fetchRecommendedIssues}
              className="px-6 py-2 bg-gradient-to-r from-green-500 to-cyan-400 text-white rounded-lg font-medium shadow-lg hover:from-green-600 hover:to-cyan-500 transition-colors mb-4"
              disabled={isRecLoading}
            >
              {isRecLoading ? "Fetching..." : "Get Recommendations"}
            </button>
            {recError && <div className="text-red-400 mb-2">Error: {recError}</div>}
            <div className="space-y-4">
              {recommendedIssues.length === 0 && !isRecLoading && !recError && (
                <div className="text-[#90adcb]">No recommendations yet. Enter a repo URL and click above!</div>
              )}
              {recommendedIssues.map((issue: any, idx: number) => (
                <div key={idx} className="bg-[#1a1e22] rounded-xl p-4 shadow flex flex-col md:flex-row md:items-center md:justify-between gap-4 border border-[#223649]">
                  <div>
                    <div className="text-lg font-semibold text-white mb-1">{issue.title}</div>
                    <div className="text-[#acd1e9] text-sm mb-1">{issue.description}</div>
                  </div>
                  {issue.url && (
                    <a href={issue.url} target="_blank" rel="noopener noreferrer" className="px-4 py-2 bg-[#3d98f4] text-white rounded-lg font-medium hover:bg-[#2d7ce0] transition-colors text-sm">View on GitHub</a>
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* Repository Input Section */}
          <section className="mb-10">
            <h2 className="text-4xl font-semibold tracking-tight mb-4">
              GitHub Repository Onboarding
            </h2>
            <div className="bg-[#1a1e22] p-6 rounded-xl shadow-lg mb-8">
              <div className="space-y-4">
                <div>
                  <label className="block text-white text-sm font-medium mb-2">
                    GitHub Repository URL
                  </label>
                  <input
                    type="text"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="https://github.com/username/repository"
                    className="w-full px-3 py-2 bg-[#223649] border border-[#314d68] rounded-lg text-white placeholder-[#90adcb] focus:outline-none focus:ring-2 focus:ring-[#3d98f4]"
                  />
                </div>
                <div>
                  <label className="block text-white text-sm font-medium mb-2">
                    Experience Level
                  </label>
                  <select
                    value={experienceLevel}
                    onChange={(e) => setExperienceLevel(e.target.value)}
                    className="w-full px-3 py-2 bg-[#223649] border border-[#314d68] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#3d98f4]"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
                <button
                  onClick={generateNewLearningPath}
                  disabled={isGenerating}
                  className="px-6 py-2 bg-[#3d98f4] text-white rounded-lg font-medium hover:bg-[#2d7ce0] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isGenerating ? "Generating..." : "Generate Learning Path"}
                </button>
              </div>
            </div>
          </section>

          {/* Progress Section */}
          <section className="mb-10">
            <h2 className="text-4xl font-semibold tracking-tight mb-4">
              My Learning Path
            </h2>
            <div className="bg-[#1a1e22] p-6 rounded-xl shadow-lg mb-8">
              <div className="flex justify-between items-center mb-2">
                <p className="text-white text-base font-medium">
                  Overall Progress
                </p>
                <p className="text-[#acd1e9] text-sm font-semibold">
                  {learningPath?.overall_progress || 0}%
                </p>
              </div>
              <div className="w-full bg-[#314d68] rounded-full h-2.5">
                <div
                  className="bg-[#acd1e9] h-2.5 rounded-full"
                  style={{ width: `${learningPath?.overall_progress || 0}%` }}
                ></div>
              </div>
            </div>
          </section>

          {/* Code Tour Button */}
          <section className="mb-6">
            <button
              onClick={startCodeTour}
              className="px-6 py-2 bg-gradient-to-r from-blue-500 to-cyan-400 text-white rounded-lg font-medium shadow-lg hover:from-blue-600 hover:to-cyan-500 transition-colors"
              disabled={isCodeTourLoading}
            >
              {isCodeTourLoading ? "Generating Code Tour..." : "🚦 Start Code Tour"}
            </button>
            {codeTourError && <div className="text-red-400 mt-2">Error: {codeTourError}</div>}
          </section>

          {/* Code Tour Modal */}
          {codeTourOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60">
              <div className="bg-[#1a1e22] rounded-2xl shadow-2xl p-8 max-w-lg w-full relative">
                <button
                  className="absolute top-4 right-4 text-[#acd1e9] hover:text-white text-2xl"
                  onClick={() => setCodeTourOpen(false)}
                  aria-label="Close Code Tour"
                >
                  ×
                </button>
                {codeTourSteps.length > 0 ? (
                  <>
                    <div className="mb-4">
                      <div className="text-[#3d98f4] font-bold text-lg mb-1">Step {codeTourIndex + 1} of {codeTourSteps.length}</div>
                      <div className="text-white text-xl font-semibold mb-2">{codeTourSteps[codeTourIndex]?.title}</div>
                      <div className="text-[#acd1e9] mb-2">{codeTourSteps[codeTourIndex]?.description}</div>
                      {codeTourSteps[codeTourIndex]?.file && (
                        <div className="text-[#90adcb] text-xs mb-1">File: {codeTourSteps[codeTourIndex].file}{codeTourSteps[codeTourIndex].line ? `, Line: ${codeTourSteps[codeTourIndex].line}` : ''}</div>
                      )}
                      {codeTourSteps[codeTourIndex]?.snippet && (
                        <pre className="bg-[#223649] rounded-lg p-3 text-xs text-[#acd1e9] overflow-x-auto mb-2">
                          {codeTourSteps[codeTourIndex].snippet}
                        </pre>
                      )}
                      {codeTourSteps[codeTourIndex]?.why && (
                        <div className="text-[#3d98f4] italic">Why: {codeTourSteps[codeTourIndex].why}</div>
                      )}
                    </div>
                    <div className="flex justify-between items-center mt-6">
                      <button
                        className="px-4 py-2 bg-[#223649] text-white rounded-lg font-medium hover:bg-[#2a3f56] transition-colors"
                        onClick={() => setCodeTourIndex(i => Math.max(i - 1, 0))}
                        disabled={codeTourIndex === 0}
                      >
                        Previous
                      </button>
                      <button
                        className="px-4 py-2 bg-[#3d98f4] text-white rounded-lg font-medium hover:bg-[#2d7ce0] transition-colors"
                        onClick={() => setCodeTourIndex(i => Math.min(i + 1, codeTourSteps.length - 1))}
                        disabled={codeTourIndex === codeTourSteps.length - 1}
                      >
                        Next
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="text-white text-lg">{isCodeTourLoading ? "Loading..." : "No code tour steps available."}</div>
                )}
              </div>
            </div>
          )}

          {/* Chapters Section */}
          <section>
            <h2 className="text-2xl font-semibold tracking-tight mb-6">
              Learning Chapters
            </h2>

            {isGenerating && (
              <div className="bg-[#1a1e22] p-6 rounded-xl shadow-lg mb-6">
                <div className="flex items-center space-x-3">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-[#3d98f4]"></div>
                  <span className="text-white">
                    Generating personalized learning path...
                  </span>
                </div>
              </div>
            )}

            <Accordion type="single" collapsible className="space-y-4">
              {learningPath?.chapters.map((chapter: Chapter) => (
                <AccordionItem
                  key={chapter.id}
                  value={`chapter-${chapter.id}`}
                  className="bg-[#1a1e22] rounded-xl border-none"
                  onClick={() => { handleChapterExpand(chapter.id); openQuizForChapter(chapter); }}
                >
                  <AccordionTrigger className="px-6 py-4 hover:no-underline">
                    <div className="flex items-center gap-4 w-full">
                      <div className="text-white flex items-center justify-center rounded-lg bg-[#223649] shrink-0 size-12">
                        <svg
                          fill="currentColor"
                          height="24px"
                          viewBox="0 0 256 256"
                          width="24px"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path d="M224,48H160a40,40,0,0,0-32,16A40,40,0,0,0,96,48H32A16,16,0,0,0,16,64V192a16,16,0,0,0,16,16H96a24,24,0,0,1,24,24,8,8,0,0,0,16,0,24,24,0,0,1,24-24h64a16,16,0,0,0,16-16V64A16,16,0,0,0,224,48ZM96,192H32V64H96a24,24,0,0,1,24,24V200A39.81,39.81,0,0,0,96,192Zm128,0H160a39.81,39.81,0,0,0-24,8V88a24,24,0,0,1,24-24h64Z"></path>
                        </svg>
                      </div>
                      <div className="flex-grow text-left">
                        <p className="text-white text-lg font-semibold leading-tight">
                          Chapter {chapter.id}: {chapter.title}
                        </p>
                        <p className="text-[#90adcb] text-sm font-normal mt-1">
                          {chapter.description}
                        </p>
                      </div>
                      <div className="shrink-0 flex items-center gap-3">
                        <div className="w-20 bg-[#314d68] rounded-full h-2">
                          <div
                            className="bg-[#acd1e9] h-2 rounded-full"
                            style={{ width: `${Math.random() * 100}%` }}
                          ></div>
                        </div>
                        <p className="text-white text-sm font-medium w-8 text-right">
                          {Math.floor(Math.random() * 100)}%
                        </p>
                      </div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="px-6 pb-4">
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-white text-sm font-semibold mb-2">
                          Tasks:
                        </h4>
                        <ul className="list-disc list-inside space-y-1 text-[#90adcb] text-sm ml-4">
                          {chapter.tasks.map((task: string, taskIndex: number) => (
                            <li key={taskIndex}>{task}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="text-white text-sm font-semibold mb-2">
                          Tips:
                        </h4>
                        <ul className="list-disc list-inside space-y-1 text-[#90adcb] text-sm ml-4">
                          {chapter.tips.map((tip: string, tipIndex: number) => (
                            <li key={tipIndex}>{tip}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="text-white text-sm font-semibold mb-2">
                          Next Steps:
                        </h4>
                        <p className="text-[#90adcb] text-sm">
                          {chapter.next_steps}
                        </p>
                      </div>
                      <div className="flex gap-2 mt-4">
                        <button className="px-4 py-2 bg-[#3d98f4] text-white rounded-lg text-sm font-medium hover:bg-[#2d7ce0] transition-colors">
                          Continue Learning
                        </button>
                        <button className="px-4 py-2 bg-[#223649] text-white rounded-lg text-sm font-medium hover:bg-[#2a3f56] transition-colors">
                          Review Notes
                        </button>
                      </div>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </section>

          {/* Quiz Modal */}
          {quizOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60">
              <div className="bg-[#1a1e22] rounded-2xl shadow-2xl p-8 max-w-md w-full relative">
                <button
                  className="absolute top-4 right-4 text-[#acd1e9] hover:text-white text-2xl"
                  onClick={() => setQuizOpen(false)}
                  aria-label="Close Quiz"
                >
                  ×
                </button>
                <div className="mb-4">
                  <div className="text-white text-xl font-semibold mb-2">Mini-Quiz</div>
                  {quizQuestions.map((q, idx) => (
                    <div key={idx} className="mb-4">
                      <div className="text-[#acd1e9] mb-2">{q.question}</div>
                      <div className="flex flex-col gap-2">
                        {q.options.map((opt: string, oidx: number) => (
                          <label key={oidx} className="flex items-center gap-2 cursor-pointer">
                            <input
                              type="radio"
                              name={`quiz-q${idx}`}
                              checked={quizAnswers[idx] === oidx}
                              onChange={() => setQuizAnswers((a: any) => ({ ...a, [idx]: oidx }))}
                              className="accent-[#3d98f4]"
                              disabled={quizResult !== null}
                            />
                            <span className="text-white text-sm">{opt}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
                {quizResult === null ? (
                  <button
                    className="px-6 py-2 bg-[#3d98f4] text-white rounded-lg font-medium hover:bg-[#2d7ce0] transition-colors"
                    onClick={submitQuiz}
                  >
                    Submit Quiz
                  </button>
                ) : quizResult ? (
                  <div className="text-green-400 text-lg font-bold flex items-center gap-2 mt-2">🎉 Correct! Badge earned!</div>
                ) : (
                  <div className="text-red-400 text-lg font-bold flex items-center gap-2 mt-2">❌ Some answers are incorrect. Try again!</div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Learn;
