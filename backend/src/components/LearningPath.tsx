import { useState, useEffect } from 'react';
import styles from './LearningPath.module.css';
import RepoSelector from './RepoSelector';
import ChapterQuiz from './ChapterQuiz';

interface Chapter {
  id: number;
  title: string;
  description: string;
  tasks: string[];
  tips: string[];
  next_steps: string;
  quiz_questions?: Array<{
    question: string;
    choices: string[];
    correct_answer?: string;
    explanation?: string;
  }>;
}

interface LearningPathData {
  overall_progress: number;
  chapters: Chapter[];
  repo_name?: string;
  repo_description?: string;
  repo_url?: string;
  onboarding_summary?: any;
}

const LearningPath: React.FC = () => {
  const [data, setData] = useState<LearningPathData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showSelector, setShowSelector] = useState<boolean>(false);
  const [expandedChapter, setExpandedChapter] = useState<number | null>(null);
  const [showQuiz, setShowQuiz] = useState<{ [key: number]: boolean }>({});
  const [chapterScores, setChapterScores] = useState<{ [key: number]: number }>({});
  const [progressMessage, setProgressMessage] = useState<string>("Loading...");
  const [backendPort, setBackendPort] = useState<number | null>(null);

  // Check which backend port is available
  useEffect(() => {
    const checkBackendPort = async () => {
      try {
        // Try port 8000 first
        try {
          const response = await fetch('http://localhost:8000/');
          if (response.ok) {
            console.log("Backend found on port 8000");
            setBackendPort(8000);
            return;
          }
        } catch (e) {
          console.log("Backend not available on port 8000, trying 8001");
        }
        
        // Try port 8001 next
        try {
          const response = await fetch('http://localhost:8001/');
          if (response.ok) {
            console.log("Backend found on port 8001");
            setBackendPort(8001);
            return;
          }
        } catch (e) {
          console.log("Backend not available on port 8001 either");
          setError("Cannot connect to backend server. Please ensure it is running.");
          setLoading(false);
          return;
        }
      } catch (err) {
        console.error("Error checking backend ports:", err);
        setError("Failed to connect to backend. Please ensure the server is running.");
        setLoading(false);
      }
    };
    
    checkBackendPort();
  }, []);

  // Load initial data once backend port is determined
  useEffect(() => {
    if (backendPort) {
      const fetchData = async () => {
        try {
          // Try to load from the API endpoint
          const response = await fetch(`http://localhost:${backendPort}/api/learning-path`);
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          
          const jsonData = await response.json();
          setData(jsonData);
          setError(null);
        } catch (err) {
          console.error("Error fetching learning path:", err);
          // Create default data if API fails
          setData({
            overall_progress: 0,
            chapters: [
              {
                id: 1,
                title: "Getting Started",
                description: "Begin by generating a learning path for a specific GitHub repository.",
                tasks: ["Click the 'Generate For Repo' button above", "Enter a GitHub repository URL", "Wait for the analysis to complete"],
                tips: ["Choose a repository you want to learn about", "The analysis might take a minute to complete"],
                next_steps: "After generating a learning path, explore the chapters to understand the repository."
              }
            ]
          });
        } finally {
          setLoading(false);
        }
      };
      
      fetchData();
    }
  }, [backendPort]);

  // Listen for WebSocket progress updates
  useEffect(() => {
    if (!backendPort) return;
    
    const setupWebSocket = () => {
      try {
        const clientId = localStorage.getItem('clientId');
        if (clientId) {
          const socket = new WebSocket(`ws://localhost:${backendPort}/ws/${clientId}`);
          
          socket.onopen = () => {
            console.log("WebSocket connection established");
          };
          
          socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setProgressMessage(`${data.message} (${data.progress}%)`);
          };
          
          socket.onerror = (error) => {
            console.error("WebSocket error:", error);
          };
          
          return socket;
        }
      } catch (err) {
        console.error("WebSocket setup error:", err);
      }
      return null;
    };
    
    const socket = setupWebSocket();
    
    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, [backendPort]);

  const handleGeneratePath = (newLearningPath: LearningPathData) => {
    console.log("New learning path received:", newLearningPath);
    setData(newLearningPath);
    setShowSelector(false);
    setExpandedChapter(null);
    setShowQuiz({});
    setChapterScores({});
  };

  const toggleExpandChapter = (chapterId: number) => {
    setExpandedChapter(expandedChapter === chapterId ? null : chapterId);
  };

  const toggleQuiz = (chapterId: number) => {
    setShowQuiz(prev => ({
      ...prev,
      [chapterId]: !prev[chapterId]
    }));
  };

  const handleQuizComplete = (chapterId: number, score: number, feedback: string) => {
    setChapterScores(prev => ({
      ...prev,
      [chapterId]: score
    }));
    
    // If we have scores for all chapters, calculate overall progress
    if (data) {
      const newChapterScores = { ...chapterScores, [chapterId]: score };
      const chaptersWithScores = Object.keys(newChapterScores).length;
      
      if (chaptersWithScores === data.chapters.length) {
        // All chapters have scores, calculate overall progress
        const totalScore = Object.values(newChapterScores).reduce((sum, score) => sum + score, 0);
        const overallProgress = Math.round(totalScore / data.chapters.length);
        
        // Update overall progress
        setData(prev => prev ? { ...prev, overall_progress: overallProgress } : null);
      }
    }
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
        <p>{progressMessage}</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Developer Onboarding Path</h1>
        <button 
          className={styles.generateButton}
          onClick={() => setShowSelector(!showSelector)}
          disabled={!backendPort}
        >
          {showSelector ? 'Cancel' : 'Generate For Repo'}
        </button>
      </div>
      
      {showSelector && (
        <RepoSelector 
          onGeneratePath={handleGeneratePath}
          setLoading={setLoading}
          setError={setError}
        />
      )}
      
      {error && <div className={styles.error}>{error}</div>}

      {data && (
        <>
          {data.repo_name && (
            <div className={styles.repoInfo}>
              <h2 className={styles.repoName}>{data.repo_name}</h2>
              {data.repo_description && <p className={styles.repoDescription}>{data.repo_description}</p>}
              {data.repo_url && (
                <a href={data.repo_url} target="_blank" rel="noopener noreferrer" className={styles.repoLink}>
                  View Repository
                </a>
              )}
            </div>
          )}
        
          <div className={styles.overallProgress}>
            <div className={styles.progressHeader}>
              <h2>Overall Progress</h2>
              <span className={styles.progressPercentage}>{data.overall_progress}%</span>
            </div>
            <div className={styles.progressBarContainer}>
              <div 
                className={styles.progressBarFill} 
                style={{ width: `${data.overall_progress}%` }}
              />
            </div>
          </div>

          {data.onboarding_summary && (
            <div className={styles.onboardingSummary}>
              <h2 className={styles.summaryTitle}>Repository Insights</h2>
              <div className={styles.summaryGrid}>
                <div className={styles.summaryCard}>
                  <h3>Environment & Tooling</h3>
                  <p><strong>Languages:</strong> {data.onboarding_summary.environment_tooling?.languages?.join(", ") || "None detected"}</p>
                  <p><strong>Config Files:</strong> {data.onboarding_summary.environment_tooling?.config_files?.join(", ") || "None detected"}</p>
                </div>
                
                <div className={styles.summaryCard}>
                  <h3>Git Workflow</h3>
                  <p><strong>Default Branch:</strong> {data.onboarding_summary.git_workflow?.default_branch || "main"}</p>
                  <p><strong>Protected Branches:</strong> {data.onboarding_summary.git_workflow?.protected_branches?.join(", ") || "None detected"}</p>
                </div>
                
                <div className={styles.summaryCard}>
                  <h3>Code Style</h3>
                  <p><strong>Linters:</strong> {data.onboarding_summary.code_style?.linters?.join(", ") || "None detected"}</p>
                </div>
                
                <div className={styles.summaryCard}>
                  <h3>CI/CD</h3>
                  <p><strong>Workflows:</strong> {data.onboarding_summary.ci_cd?.workflows?.join(", ") || "None detected"}</p>
                </div>
              </div>
            </div>
          )}

          <h2 className={styles.chaptersTitle}>Onboarding Chapters</h2>
          <div className={styles.chapters}>
            {data.chapters.map((chapter) => {
              const chapterProgress = chapterScores[chapter.id] || 0;
              const isExpanded = expandedChapter === chapter.id;
              
              return (
                <div 
                  key={chapter.id} 
                  className={`${styles.chapter} ${isExpanded ? styles.expanded : ''}`}
                >
                  <div 
                    className={styles.chapterHeader}
                    onClick={() => toggleExpandChapter(chapter.id)}
                  >
                    <div className={styles.chapterIcon}>
                      <svg 
                        fill="currentColor" 
                        height="28px" 
                        viewBox="0 0 256 256" 
                        width="28px" 
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path d="M224,48H160a40,40,0,0,0-32,16A40,40,0,0,0,96,48H32A16,16,0,0,0,16,64V192a16,16,0,0,0,16,16H96a24,24,0,0,1,24,24,8,8,0,0,0,16,0,24,24,0,0,1,24-24h64a16,16,0,0,0,16-16V64A16,16,0,0,0,224,48ZM96,192H32V64H96a24,24,0,0,1,24,24V200A39.81,39.81,0,0,0,96,192Zm128,0H160a39.81,39.81,0,0,0-24,8V88a24,24,0,0,1,24-24h64Z"></path>
                      </svg>
                    </div>
                    
                    <div className={styles.chapterHeaderContent}>
                      <h3 className={styles.chapterTitle}>{chapter.title}</h3>
                      
                      <div className={styles.chapterProgressContainer}>
                        <div className={styles.progressBarContainer}>
                          <div 
                            className={styles.progressBarFill} 
                            style={{ width: `${chapterProgress}%` }}
                          />
                        </div>
                        <span className={styles.progressPercentage}>{chapterProgress}%</span>
                      </div>
                    </div>
                    
                    <div className={styles.expandIcon}>
                      {isExpanded ? (
                        <svg fill="currentColor" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M19 13H5v-2h14v2z"></path>
                        </svg>
                      ) : (
                        <svg fill="currentColor" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"></path>
                        </svg>
                      )}
                    </div>
                  </div>
                  
                  {isExpanded && (
                    <div className={styles.chapterContent}>
                      <p className={styles.chapterDescription}>{chapter.description}</p>
                      
                      {chapter.tasks.length > 0 && (
                        <div className={styles.section}>
                          <h4>Tasks</h4>
                          <ul className={styles.list}>
                            {chapter.tasks.map((task, index) => (
                              <li key={index} className={styles.task}>
                                {task}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {chapter.tips.length > 0 && (
                        <div className={styles.section}>
                          <h4>Tips</h4>
                          <ul className={styles.list}>
                            {chapter.tips.map((tip, index) => (
                              <li key={index} className={styles.tip}>
                                {tip}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {chapter.next_steps && (
                        <div className={styles.section}>
                          <h4>Next Steps</h4>
                          <p className={styles.nextStep}>{chapter.next_steps}</p>
                        </div>
                      )}
                      
                      {chapter.quiz_questions && chapter.quiz_questions.length > 0 && (
                        <div className={styles.quizSection}>
                          <button 
                            className={styles.quizButton}
                            onClick={() => toggleQuiz(chapter.id)}
                          >
                            {showQuiz[chapter.id] ? 'Hide Knowledge Check' : 'Test Your Knowledge'}
                          </button>
                          
                          {showQuiz[chapter.id] && (
                            <ChapterQuiz 
                              chapterId={chapter.id}
                              questions={chapter.quiz_questions}
                              onQuizComplete={(score, feedback) => handleQuizComplete(chapter.id, score, feedback)}
                            />
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};

export default LearningPath;