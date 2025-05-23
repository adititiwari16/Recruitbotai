import React, { useState } from 'react';
import UserForm from './components/UserForm';
import InterviewSetup from './components/InterviewSetup';
import InterviewSession from './components/InterviewSession';
import FeedbackView from './components/FeedbackView';
import QueryAssistant from './components/QueryAssistant';

function App() {
  const [currentStep, setCurrentStep] = useState('userForm');
  const [userData, setUserData] = useState(null);
  const [interviewData, setInterviewData] = useState(null);
  const [questionsData, setQuestionsData] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [feedbackData, setFeedbackData] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [showQueryAssistant, setShowQueryAssistant] = useState(false);

  // Handle user form submission
  const handleUserSubmit = (user) => {
    setUserData(user);
    setCurrentStep('interviewSetup');
  };

  // Handle interview setup submission
  const handleInterviewStart = (interview, questions) => {
    setInterviewData(interview);
    setQuestionsData(questions);
    setCurrentStep('interviewSession');
  };

  // Handle question answer submission
  const handleAnswerSubmit = (questionId, answer, evaluation) => {
    // Update questions data with the answer and evaluation
    const updatedQuestions = questionsData.map(q => 
      q.id === questionId 
        ? { ...q, answer, evaluation } 
        : q
    );
    
    setQuestionsData(updatedQuestions);
    
    // If there are more questions, move to the next one
    if (currentQuestionIndex < questionsData.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      // If this was the last question, move to feedback view
      setCurrentStep('processingFeedback');
    }
  };

  // Handle interview completion
  const handleInterviewComplete = (feedback, report) => {
    setFeedbackData(feedback);
    setReportData(report);
    setCurrentStep('feedbackView');
  };

  // Handle restart interview
  const handleRestart = () => {
    setCurrentStep('userForm');
    setUserData(null);
    setInterviewData(null);
    setQuestionsData([]);
    setCurrentQuestionIndex(0);
    setFeedbackData(null);
    setReportData(null);
  };

  // Render the appropriate component based on current step
  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'userForm':
        return <UserForm onSubmit={handleUserSubmit} />;
      
      case 'interviewSetup':
        return <InterviewSetup 
                 userData={userData} 
                 onStart={handleInterviewStart} 
               />;
      
      case 'interviewSession':
        return <InterviewSession 
                 interviewData={interviewData}
                 questionsData={questionsData}
                 currentQuestionIndex={currentQuestionIndex}
                 onAnswerSubmit={handleAnswerSubmit}
                 onInterviewComplete={handleInterviewComplete}
               />;
      
      case 'processingFeedback':
        return (
          <div className="container mt-5 text-center">
            <div className="card">
              <div className="card-body">
                <h2 className="card-title">Processing Your Interview</h2>
                <p className="card-text">Please wait while our AI analyzes your responses...</p>
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
              </div>
            </div>
          </div>
        );
      
      case 'feedbackView':
        return <FeedbackView 
                 userData={userData}
                 interviewData={interviewData}
                 feedbackData={feedbackData}
                 reportData={reportData}
                 onRestart={handleRestart}
               />;
      
      default:
        return <UserForm onSubmit={handleUserSubmit} />;
    }
  };

  return (
    <div className="app-container">
      <header className="bg-primary text-white text-center py-4 mb-4">
        <div className="container">
          <h1 className="display-4">RecruitBot</h1>
          <p className="lead">AI-Powered Interview Evaluation Tool</p>
          
          {/* Toggle button for query assistant */}
          <button 
            className="btn btn-outline-light mt-2"
            onClick={() => setShowQueryAssistant(!showQueryAssistant)}
          >
            {showQueryAssistant ? 'Hide Interview Assistant' : 'Show Interview Assistant'}
          </button>
        </div>
      </header>
      
      {/* Query Assistant Panel (collapsible) */}
      {showQueryAssistant && (
        <div className="container mb-4">
          <QueryAssistant />
        </div>
      )}
      
      {renderCurrentStep()}
      
      <footer className="bg-dark text-white text-center py-3 mt-5">
        <div className="container">
          <p className="mb-0">© 2023 RecruitBot - AI-Powered Interview Evaluation Tool</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
