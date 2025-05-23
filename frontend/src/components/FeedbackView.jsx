import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

function FeedbackView({ userData, interviewData, feedbackData, reportData, onRestart }) {
  const [activeTab, setActiveTab] = useState('report');

  // Helper function to determine status badge class
  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-success';
      case 'failed':
        return 'bg-danger';
      default:
        return 'bg-secondary';
    }
  };

  // Handle download report
  const handleDownloadReport = () => {
    // Create a blob from the report markdown
    const blob = new Blob([reportData], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    
    // Create a temporary link and trigger download
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview-report-${userData.name.replace(/\s+/g, '-')}-${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    
    // Cleanup
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  };

  return (
    <div className="container mt-5">
      <div className="row">
        <div className="col-md-8 offset-md-2">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h4 className="mb-0">Interview Results</h4>
            </div>
            
            <div className="card-body">
              <div className="row mb-4">
                <div className="col-md-6">
                  <h5>Candidate Information</h5>
                  <ul className="list-group list-group-flush">
                    <li className="list-group-item"><strong>Name:</strong> {userData.name}</li>
                    {userData.age && <li className="list-group-item"><strong>Age:</strong> {userData.age}</li>}
                    {userData.experience && <li className="list-group-item"><strong>Experience:</strong> {userData.experience} years</li>}
                    {userData.job_title && <li className="list-group-item"><strong>Current Job:</strong> {userData.job_title}</li>}
                  </ul>
                </div>
                
                <div className="col-md-6">
                  <h5>Interview Summary</h5>
                  <ul className="list-group list-group-flush">
                    <li className="list-group-item"><strong>Role:</strong> {interviewData.role}</li>
                    <li className="list-group-item"><strong>Experience Level:</strong> {interviewData.experience_level}</li>
                    <li className="list-group-item">
                      <strong>Status:</strong> 
                      <span className={`badge ms-2 ${getStatusBadgeClass(interviewData.status)}`}>
                        {interviewData.status === 'completed' ? 'PASS' : 'FAIL'}
                      </span>
                    </li>
                    <li className="list-group-item">
                      <strong>Score:</strong> 
                      <span className="badge bg-info ms-2">{Math.round(interviewData.score)}/100</span>
                    </li>
                  </ul>
                </div>
              </div>
              
              <ul className="nav nav-tabs mb-3">
                <li className="nav-item">
                  <button 
                    className={`nav-link ${activeTab === 'report' ? 'active' : ''}`}
                    onClick={() => setActiveTab('report')}
                  >
                    Detailed Report
                  </button>
                </li>
                <li className="nav-item">
                  <button 
                    className={`nav-link ${activeTab === 'feedback' ? 'active' : ''}`}
                    onClick={() => setActiveTab('feedback')}
                  >
                    Overall Feedback
                  </button>
                </li>
              </ul>
              
              <div className="tab-content">
                {activeTab === 'report' && (
                  <div className="tab-pane fade show active">
                    <div className="markdown-content">
                      <ReactMarkdown>{reportData}</ReactMarkdown>
                    </div>
                  </div>
                )}
                
                {activeTab === 'feedback' && (
                  <div className="tab-pane fade show active">
                    <div className="alert alert-info">
                      <h5 className="alert-heading">AI Evaluation</h5>
                      <p>{feedbackData.feedback}</p>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="d-flex justify-content-between mt-4">
                <button 
                  type="button" 
                  className="btn btn-outline-primary"
                  onClick={onRestart}
                >
                  Start New Interview
                </button>
                
                <button 
                  type="button" 
                  className="btn btn-success"
                  onClick={handleDownloadReport}
                >
                  <i className="bi bi-download me-2"></i>
                  Download Report
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FeedbackView;
