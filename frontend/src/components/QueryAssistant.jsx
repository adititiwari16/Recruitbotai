import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

function QueryAssistant() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Function to send query to the API
  const sendQuery = async (question, context = '') => {
    try {
      // Use the full URL including hostname and port
      const apiUrl = 'http://localhost:5000/api/query/ask';
      console.log(`Sending query to ${apiUrl}:`, question);
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: question,
          context: context
        })
      });
      
      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Received response:', data);
      return data.response;
    } catch (error) {
      console.error('Error querying API:', error);
      throw error;
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a question');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const markdownResponse = await sendQuery(query);
      setResponse(markdownResponse);
    } catch (error) {
      setError('Failed to get response from the server. Please try again.');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <div className="card">
        <div className="card-header bg-primary text-white">
          <h4 className="mb-0">Interview Assistant</h4>
        </div>
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label htmlFor="query" className="form-label">Ask a question about interviews or recruitment</label>
              <input
                type="text"
                className="form-control"
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="E.g., What are good questions to ask a frontend developer?"
              />
              {error && <div className="text-danger mt-2">{error}</div>}
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Processing...
                </>
              ) : 'Get Answer'}
            </button>
          </form>
          
          {response && (
            <div className="mt-4">
              <h5>Response:</h5>
              <div className="markdown-content p-3 bg-light rounded">
                <ReactMarkdown>{response}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="card mt-4">
        <div className="card-header bg-info text-white">
          <h5 className="mb-0">Common Questions</h5>
        </div>
        <div className="card-body">
          <p>Try asking about:</p>
          <ul className="list-group list-group-flush">
            <li className="list-group-item">
              <button 
                className="btn btn-link p-0 text-decoration-none"
                onClick={() => {
                  setQuery("What are common interview questions for a software engineer?");
                  document.getElementById("query").focus();
                }}
              >
                Common interview questions for a software engineer
              </button>
            </li>
            <li className="list-group-item">
              <button 
                className="btn btn-link p-0 text-decoration-none"
                onClick={() => {
                  setQuery("How should I prepare for a technical interview?");
                  document.getElementById("query").focus();
                }}
              >
                How to prepare for a technical interview
              </button>
            </li>
            <li className="list-group-item">
              <button 
                className="btn btn-link p-0 text-decoration-none"
                onClick={() => {
                  setQuery("What are red flags to look for when interviewing a candidate?");
                  document.getElementById("query").focus();
                }}
              >
                Red flags to look for when interviewing a candidate
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default QueryAssistant;