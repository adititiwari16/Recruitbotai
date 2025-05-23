import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

function QueryAssistantStandalone() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Function to send query to the API
  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a question');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:5000/api/query/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: query
        })
      });
      
      const data = await response.json();
      console.log('Response from API:', data);
      
      if (data.response) {
        setResponse(data.response);
      } else {
        setError('Received an invalid response from the API');
      }
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to get a response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Display a standalone version of the query assistant
  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-10">
          <div className="card mb-4">
            <div className="card-header bg-primary text-white">
              <h2 className="mb-0">Interview Assistant</h2>
              <p className="mb-0">Ask questions about interviews, candidate assessment, and more</p>
            </div>
            <div className="card-body">
              <form onSubmit={handleQuerySubmit}>
                <div className="mb-3">
                  <label htmlFor="query" className="form-label">What would you like to know?</label>
                  <div className="input-group">
                    <input
                      type="text"
                      className="form-control"
                      id="query"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="E.g., What are good questions to ask a frontend developer?"
                    />
                    <button 
                      type="submit" 
                      className="btn btn-primary" 
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Processing...
                        </>
                      ) : 'Get Answer'}
                    </button>
                  </div>
                  {error && <div className="text-danger mt-2">{error}</div>}
                </div>
              </form>
              
              {response && (
                <div className="mt-4 p-3 border rounded bg-light">
                  <h5>Response:</h5>
                  <div className="markdown-content">
                    <ReactMarkdown>{response}</ReactMarkdown>
                  </div>
                </div>
              )}
              
              <div className="mt-4">
                <h5>Try asking about:</h5>
                <div className="row">
                  <div className="col-md-4 mb-2">
                    <button 
                      className="btn btn-outline-secondary w-100 text-start"
                      onClick={() => {
                        setQuery("Common interview questions for software engineers");
                        document.getElementById("query").focus();
                      }}
                    >
                      <i className="bi bi-code-square me-2"></i>
                      Interview Questions
                    </button>
                  </div>
                  <div className="col-md-4 mb-2">
                    <button 
                      className="btn btn-outline-secondary w-100 text-start"
                      onClick={() => {
                        setQuery("How to prepare for a technical interview");
                        document.getElementById("query").focus();
                      }}
                    >
                      <i className="bi bi-journal-check me-2"></i>
                      Interview Preparation
                    </button>
                  </div>
                  <div className="col-md-4 mb-2">
                    <button 
                      className="btn btn-outline-secondary w-100 text-start"
                      onClick={() => {
                        setQuery("Red flags to watch for in candidates");
                        document.getElementById("query").focus();
                      }}
                    >
                      <i className="bi bi-flag-fill me-2"></i>
                      Candidate Red Flags
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default QueryAssistantStandalone;