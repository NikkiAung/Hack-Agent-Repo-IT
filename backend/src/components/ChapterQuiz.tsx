import { useState } from 'react';
import axios from 'axios';
import styles from './ChapterQuiz.module.css';

interface QuizQuestion {
  question: string;
  choices: string[];
  correct_answer?: string;
  explanation?: string;
}

interface QuizProps {
  chapterId: number;
  questions: QuizQuestion[];
  onQuizComplete: (score: number, feedback: string) => void;
}

const ChapterQuiz: React.FC<QuizProps> = ({ chapterId, questions, onQuizComplete }) => {
  const [answers, setAnswers] = useState<string[]>(Array(questions.length).fill(''));
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [results, setResults] = useState<{
    score: number;
    feedback: string;
    questions: Array<QuizQuestion & { user_answer?: string }>;
  } | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnswerSelect = (questionIndex: number, answer: string) => {
    if (submitted) return;
    
    const newAnswers = [...answers];
    newAnswers[questionIndex] = answer;
    setAnswers(newAnswers);
  };

  const handleSubmit = async () => {
    // Check if all questions are answered
    if (answers.some(answer => answer === '')) {
      setError('Please answer all questions before submitting.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Format user answers for API
      const userAnswers = questions.map((q, index) => ({
        question_id: index,
        answer: answers[index]
      }));

      // Submit answers to API for evaluation
      const response = await axios.post(`/api/test-knowledge/${chapterId}`, userAnswers);
      
      setResults(response.data);
      setSubmitted(true);
      onQuizComplete(response.data.score, response.data.feedback);
    } catch (err) {
      setError('Failed to submit quiz. Please try again.');
      console.error('Error submitting quiz:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setAnswers(Array(questions.length).fill(''));
    setSubmitted(false);
    setResults(null);
    setError(null);
  };

  return (
    <div className={styles.quizContainer}>
      <h3 className={styles.quizTitle}>Knowledge Check</h3>
      
      {error && <div className={styles.error}>{error}</div>}
      
      <div className={styles.questions}>
        {questions.map((question, qIndex) => (
          <div key={qIndex} className={styles.questionCard}>
            <h4 className={styles.questionText}>{question.question}</h4>
            
            <div className={styles.choices}>
              {question.choices.map((choice, cIndex) => (
                <div 
                  key={cIndex} 
                  className={`${styles.choiceItem} ${
                    answers[qIndex] === choice ? styles.selected : ''
                  } ${
                    submitted && results ? (
                      choice === results.questions[qIndex].correct_answer 
                        ? styles.correct 
                        : (answers[qIndex] === choice ? styles.incorrect : '')
                    ) : ''
                  }`}
                  onClick={() => handleAnswerSelect(qIndex, choice)}
                >
                  <div className={styles.choiceIndicator}>{String.fromCharCode(65 + cIndex)}</div>
                  <div className={styles.choiceText}>{choice}</div>
                </div>
              ))}
            </div>
            
            {submitted && results && results.questions[qIndex].explanation && (
              <div className={styles.explanation}>
                <strong>Explanation:</strong> {results.questions[qIndex].explanation}
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className={styles.quizActions}>
        {submitted ? (
          <div className={styles.results}>
            <div className={styles.scoreCard}>
              <div className={styles.scoreValue}>{results?.score}%</div>
              <div className={styles.scoreName}>Score</div>
            </div>
            
            <div className={styles.feedback}>
              <p>{results?.feedback}</p>
            </div>
            
            <button className={styles.retryButton} onClick={handleRetry}>
              Try Again
            </button>
          </div>
        ) : (
          <button 
            className={styles.submitButton} 
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? 'Submitting...' : 'Submit Answers'}
          </button>
        )}
      </div>
    </div>
  );
};

export default ChapterQuiz;