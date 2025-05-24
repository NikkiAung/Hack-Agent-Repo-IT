import { useState, useEffect } from 'react';
import styles from './RepoSelector.module.css';

interface RepoSelectorProps {
  onGeneratePath: (learningPath: any) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
}

const RepoSelector: React.FC<RepoSelectorProps> = ({ 
  onGeneratePath,
  setLoading,
  setError
}) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('beginner');
  const [focusAreas, setFocusAreas] = useState<string[]>([]);
  const [backendPort, setBackendPort] = useState(8000);
  const [availableFocusAreas] = useState([
    { id: 'frontend', label: 'Frontend' },
    { id: 'backend', label: 'Backend' },
    { id: 'testing', label: 'Testing' },
    { id: 'architecture', label: 'Architecture' },
    { id: 'deployment', label: 'Deployment' },
    { id: 'performance', label: 'Performance' }
  ]);

  // Check connection to backend
  useEffect(() => {
    const checkBackendConnection = async () => {
      console.log("Checking backend connection...");
      
      try {
        const response = await fetch('http://localhost:8000/');
        if (response.ok) {
          console.log("Backend is available on port 8000");
          setBackendPort(8000);
          return;
        }
      } catch (e) {
        console.log("Backend not available on port 8000");
        try {
          const response = await fetch('http://localhost:8001/');
          if (response.ok) {
            console.log("Backend is available on port 8001");
            setBackendPort(8001);
            return;
          }
        } catch (e) {
          console.log("Backend not available on port 8001 either");
          setError("Backend server is not running. Please start the backend server and try again.");
        }
      }
    };
    
    checkBackendConnection();
  }, [setError]);

  const handleFocusAreaChange = (areaId: string) => {
    setFocusAreas(prev => 
      prev.includes(areaId) 
        ? prev.filter(id => id !== areaId)
        : [...prev, areaId]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      console.log("Submitting form with URL:", repoUrl);
      
      // Create WebSocket connection for progress updates
      const clientId = Math.random().toString(36).substring(2, 15);
      localStorage.setItem('clientId', clientId); // Store for LearningPath component
      
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//localhost:${backendPort}/ws/${clientId}`;
      
      console.log("Connecting to WebSocket:", wsUrl);
      const socket = new WebSocket(wsUrl);
      
      socket.onopen = () => {
        console.log("WebSocket connection established");
      };
      
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Progress update:", data);
      };
      
      socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        setError("Failed to connect to the server for real-time updates.");
        setLoading(false);
      };
      
      // Start the generation process using the REST API
      const response = await fetch(`http://localhost:${backendPort}/generate?repo_url=${encodeURIComponent(repoUrl)}&experience=${experienceLevel}&client_id=${clientId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Poll for results
      const checkResults = async () => {
        try {
          const response = await fetch(`http://localhost:${backendPort}/results/${clientId}`);
          if (response.ok) {
            const data = await response.json();
            if (data.error) {
              setError(data.error);
              setLoading(false);
              socket.close();
              return;
            }
            
            // Add repo URL to the data
            const enrichedData = {
              ...data,
              repo_url: repoUrl,
              repo_name: repoUrl.split('/').pop() || 'Repository'
            };
            
            onGeneratePath(enrichedData);
            setLoading(false);
            socket.close();
          } else {
            // If results not ready, try again after a delay
            setTimeout(checkResults, 1000);
          }
        } catch (err) {
          console.error("Error checking results:", err);
          setError("Failed to retrieve results. Please try again.");
          setLoading(false);
          socket.close();
        }
      };
      
      // Start polling after a short delay
      setTimeout(checkResults, 2000);
      
    } catch (err: any) {
      console.error('Error generating learning path:', err);
      setError(err.message || 'Failed to generate learning path');
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Generate Learning Path</h2>
      <p className={styles.description}>
        Enter a GitHub repository URL to generate a personalized learning path.
      </p>
      
      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.formGroup}>
          <label htmlFor="repo-url">GitHub Repository URL</label>
          <input
            id="repo-url"
            type="url"
            className={styles.input}
            placeholder="https://github.com/username/repository"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            required
          />
        </div>
        
        <div className={styles.formGroup}>
          <label htmlFor="experience">Your Experience Level</label>
          <select
            id="experience"
            className={styles.select}
            value={experienceLevel}
            onChange={(e) => setExperienceLevel(e.target.value)}
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
        
        <div className={styles.formGroup}>
          <label>Focus Areas (Optional)</label>
          <div className={styles.checkboxGroup}>
            {availableFocusAreas.map(area => (
              <div key={area.id} className={styles.checkbox}>
                <input
                  id={`focus-${area.id}`}
                  type="checkbox"
                  checked={focusAreas.includes(area.id)}
                  onChange={() => handleFocusAreaChange(area.id)}
                />
                <label htmlFor={`focus-${area.id}`}>{area.label}</label>
              </div>
            ))}
          </div>
        </div>
        
        <button type="submit" className={styles.submitButton}>
          Generate Learning Path
        </button>
      </form>
    </div>
  );
};

export default RepoSelector;