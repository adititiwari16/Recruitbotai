import React from 'react';
import ReactMarkdown from 'react-markdown';

function ReportGenerator({ reportData }) {
  return (
    <div className="report-generator">
      <div className="markdown-content">
        <ReactMarkdown>{reportData}</ReactMarkdown>
      </div>
    </div>
  );
}

export default ReportGenerator;
