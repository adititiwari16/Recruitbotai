import React, { useState, useEffect } from 'react';
import { submitAnswer, completeInterview } from '../services/api';
import VideoRecorder from './VideoRecorder';

function InterviewSession({ 
  interviewData, 
  questionsData, 
  currentQuestionIndex, 
  onAnswerSubmit,
  onInterviewComplete
}) {
  const [answer, setAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [showEvaluation, setShowEvaluation] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [isCompleting, setIsCompleting] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  // Current question
  const currentQuestion = questionsData[currentQuestionIndex];

  // Handle answer change
  const handleAnswerChange = (e) => {
    setAnswer(e.target.value);
    setError('');
  };

  // Handle answer submission
  const handleSubmitAnswer = async () => {
    // Validate answer
    if (!answer.trim()) {
      setError('Please provide an answer');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const response = await submitAnswer(currentQuestion.id, answer);
      
      setIsSubmitting(false);
      setEvaluation(response.evaluation);
      setShowEvaluation(true);
    } catch (error) {
      setIsSubmitting(false);
      setError(error.message || 'Failed to submit answer. Please try again.');
    }
  };

  // Handle next question
  const handleNextQuestion = () => {
    onAnswerSubmit(currentQuestion.id, answer, evaluation);
    setAnswer('');
    setShowEvaluation(false);
    setEvaluation(null);
  };

  // Handle complete interview
  const handleCompleteInterview = async () => {
    setIsCompleting(true);
    
    try {
      const response = await completeInterview(interviewData.id);
      
      setIsCompleting(false);
      onInterviewComplete(response, response.report);
    } catch (error) {
      setIsCompleting(false);
      setError(error.message || 'Failed to complete interview. Please try again.');
    }
  };

  // Handle when the evaluation is shown and it's the last question
  useEffect(() => {
    if (showEvaluation && currentQuestionIndex === questionsData.length - 1) {
      handleCompleteInterview();
    }
  }, [showEvaluation, currentQuestionIndex, questionsData.length]);

  return (
    <div className="container mt-5">
      <div className="row">
        <div className="col-md-8">
          <div className="card mb-4">
            <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <h4 className="mb-0">Interview Session</h4>
              <span className="badge bg-light text-dark">Question {currentQuestionIndex + 1} of {questionsData.length}</span>
            </div>
            <div className="card-body">
              {error && (
                <div className="alert alert-danger" role="alert">
                  {error}
                </div>
              )}

              <div className="question-box mb-4">
                <h5>Question:</h5>
                <p className="lead">{currentQuestion?.text}</p>
              </div>

              {!showEvaluation ? (
                <div className="answer-box">
                  <h5>Your Answer:</h5>
                  <textarea
                    className="form-control"
                    rows="6"
                    value={answer}
                    onChange={handleAnswerChange}
                    placeholder="Type your answer here..."
                    disabled={isSubmitting}
                  ></textarea>
                </div>
              ) : (
                <div className="evaluation-box">
                  <div className="card bg-light">
                    <div className="card-header">
                      <h5 className="mb-0">Evaluation</h5>
                    </div>
                    <div className="card-body">
                      <h6 className="mb-2">Score: <span className="badge bg-info">{evaluation?.score}/10</span></h6>
                      
                      <div className="mb-3">
                        <h6>Strengths:</h6>
                        <p>{evaluation?.strengths}</p>
                      </div>
                      
                      <div className="mb-3">
                        <h6>Areas for Improvement:</h6>
                        <p>{evaluation?.areas_for_improvement}</p>
                      </div>
                      
                      {evaluation?.additional_insights && (
                        <div className="mb-3">
                          <h6>Additional Insights:</h6>
                          <p>{evaluation.additional_insights}</p>
                        </div>
                      )}
                      
                      <div>
                        <h6>Overall Feedback:</h6>
                        <p>{evaluation?.overall_feedback}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="d-flex justify-content-between mt-4">
                {!showEvaluation ? (
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleSubmitAnswer}
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Evaluating...
                      </>
                    ) : 'Submit Answer'}
                  </button>
                ) : (
                  <button
                    type="button"
                    className="btn btn-success"
                    onClick={handleNextQuestion}
                    disabled={isCompleting}
                  >
                    {isCompleting ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Completing Interview...
                      </>
                    ) : currentQuestionIndex < questionsData.length - 1 ? 'Next Question' : 'Complete Interview'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card">
            <div className="card-header bg-secondary text-white">
              <h5 className="mb-0">Video Recording</h5>
            </div>
            <div className="card-body">
              <VideoRecorder 
                isRecording={isRecording}
                onToggleRecording={() => setIsRecording(!isRecording)}
              />
            </div>
          </div>
          
          <div className="card mt-4">
            <div className="card-header bg-info text-white">
              <h5 className="mb-0">Interview Progress</h5>
            </div>
            <div className="card-body">
              <div className="progress mb-3">
                <div 
                  className="progress-bar" 
                  role="progressbar" 
                  style={{ width: `${((currentQuestionIndex + (showEvaluation ? 1 : 0)) / questionsData.length) * 100}%` }}
                  aria-valuenow={((currentQuestionIndex + (showEvaluation ? 1 : 0)) / questionsData.length) * 100}
                  aria-valuemin="0" 
                  aria-valuemax="100"
                >
                  {Math.round(((currentQuestionIndex + (showEvaluation ? 1 : 0)) / questionsData.length) * 100)}%
                </div>
              </div>
              
              <ul className="list-group list-group-flush">
                {questionsData.map((q, index) => (
                  <li 
                    key={q.id} 
                    className={`list-group-item d-flex justify-content-between align-items-center ${index === currentQuestionIndex ? 'active' : ''}`}
                  >
                    Question {index + 1}
                    {(index < currentQuestionIndex || (index === currentQuestionIndex && showEvaluation)) && (
                      <span className="badge bg-success rounded-pill">
                        <i className="bi bi-check"></i>
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default InterviewSession;
