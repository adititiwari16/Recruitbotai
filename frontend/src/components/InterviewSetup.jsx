import React, { useState } from 'react';
import { startInterview } from '../services/api';

function InterviewSetup({ userData, onStart }) {
  const [role, setRole] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Available roles
  const roles = [
    { id: 'software_engineer', name: 'Software Engineer' },
    { id: 'product_manager', name: 'Product Manager' },
    { id: 'data_scientist', name: 'Data Scientist' },
    { id: 'ux_designer', name: 'UX Designer' },
    { id: 'frontend_developer', name: 'Frontend Developer' },
    { id: 'backend_developer', name: 'Backend Developer' },
    { id: 'fullstack_developer', name: 'Fullstack Developer' },
    { id: 'devops_engineer', name: 'DevOps Engineer' },
    { id: 'project_manager', name: 'Project Manager' },
    { id: 'marketing_specialist', name: 'Marketing Specialist' }
  ];

  // Experience levels
  const experienceLevels = [
    { id: 'entry', name: 'Entry Level (0-2 years)' },
    { id: 'mid', name: 'Mid Level (3-5 years)' },
    { id: 'senior', name: 'Senior Level (6-9 years)' },
    { id: 'expert', name: 'Expert Level (10+ years)' }
  ];

  // Handle role selection
  const handleRoleChange = (e) => {
    setRole(e.target.value);
    setError('');
  };

  // Handle experience level selection
  const handleExperienceLevelChange = (e) => {
    setExperienceLevel(e.target.value);
    setError('');
  };

  // Handle start interview
  const handleStartInterview = async () => {
    // Validate selections
    if (!role) {
      setError('Please select a role');
      return;
    }

    if (!experienceLevel) {
      setError('Please select an experience level');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await startInterview({
        user_id: userData.id,
        role: roles.find(r => r.id === role).name,
        experience_level: experienceLevel
      });

      setIsLoading(false);
      onStart(response.interview, response.questions);
    } catch (error) {
      setIsLoading(false);
      setError(error.message || 'Failed to start interview. Please try again.');
    }
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h4 className="mb-0">Interview Setup</h4>
            </div>
            <div className="card-body">
              {error && (
                <div className="alert alert-danger" role="alert">
                  {error}
                </div>
              )}

              <div className="mb-4">
                <h5>Welcome, {userData.name}!</h5>
                <p className="text-muted">
                  Select the role and experience level for your interview. 
                  Our AI will generate relevant questions based on your selections.
                </p>
              </div>

              <div className="mb-3">
                <label htmlFor="role" className="form-label">Select Role</label>
                <select
                  className="form-select"
                  id="role"
                  value={role}
                  onChange={handleRoleChange}
                >
                  <option value="">Choose a role...</option>
                  {roles.map(r => (
                    <option key={r.id} value={r.id}>{r.name}</option>
                  ))}
                </select>
              </div>

              <div className="mb-4">
                <label htmlFor="experienceLevel" className="form-label">Select Experience Level</label>
                <select
                  className="form-select"
                  id="experienceLevel"
                  value={experienceLevel}
                  onChange={handleExperienceLevelChange}
                >
                  <option value="">Choose experience level...</option>
                  {experienceLevels.map(el => (
                    <option key={el.id} value={el.id}>{el.name}</option>
                  ))}
                </select>
              </div>

              <div className="mb-3">
                <h5>What to Expect</h5>
                <ul className="list-group list-group-flush">
                  <li className="list-group-item">You'll be asked 5 interview questions relevant to the selected role and experience level</li>
                  <li className="list-group-item">Answer each question thoroughly but concisely</li>
                  <li className="list-group-item">Our AI will evaluate your answers and provide feedback</li>
                  <li className="list-group-item">You'll receive a detailed report at the end of the interview</li>
                </ul>
              </div>

              <div className="d-grid gap-2">
                <button
                  type="button"
                  className="btn btn-success"
                  onClick={handleStartInterview}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Preparing Interview...
                    </>
                  ) : 'Start Interview'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default InterviewSetup;
