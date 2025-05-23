import React, { useState, useRef, useEffect } from 'react';

function VideoRecorder({ isRecording, onToggleRecording }) {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [stream, setStream] = useState(null);
  const [videoURL, setVideoURL] = useState('');
  const [error, setError] = useState('');
  const [hasPermission, setHasPermission] = useState(false);

  // Initialize camera when component mounts
  useEffect(() => {
    async function setupCamera() {
      try {
        const videoStream = await navigator.mediaDevices.getUserMedia({ 
          video: true,
          audio: true 
        });
        
        setStream(videoStream);
        if (videoRef.current) {
          videoRef.current.srcObject = videoStream;
        }
        setHasPermission(true);
        setError('');
      } catch (err) {
        console.error('Error accessing camera:', err);
        setError('Could not access camera or microphone. Please check permissions.');
        setHasPermission(false);
      }
    }

    setupCamera();

    // Cleanup function
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Handle recording state changes
  useEffect(() => {
    if (!stream || !hasPermission) return;

    if (isRecording) {
      startRecording();
    } else if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      stopRecording();
    }
  }, [isRecording, stream, hasPermission]);

  // Start recording
  const startRecording = () => {
    setRecordedChunks([]);
    setVideoURL('');
    
    const mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        setRecordedChunks(prev => [...prev, event.data]);
      }
    };
    
    mediaRecorder.onstop = () => {
      const blob = new Blob(recordedChunks, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      setVideoURL(url);
    };
    
    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.start();
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
  };

  // Download recorded video
  const handleDownload = () => {
    if (recordedChunks.length === 0) return;
    
    const blob = new Blob(recordedChunks, { type: 'video/webm' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview-recording-${new Date().toISOString()}.webm`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  };

  return (
    <div className="video-recorder">
      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}
      
      <div className="video-container mb-3">
        {!videoURL ? (
          <video 
            ref={videoRef} 
            autoPlay 
            muted 
            playsInline
            className="w-100 rounded"
            style={{ 
              backgroundColor: "#000", 
              height: hasPermission ? "auto" : "240px",
              maxHeight: "240px"
            }}
          ></video>
        ) : (
          <video 
            src={videoURL} 
            controls 
            className="w-100 rounded"
            style={{ maxHeight: "240px" }}
          ></video>
        )}
      </div>
      
      <div className="d-flex justify-content-between">
        <button 
          type="button"
          className={`btn ${isRecording ? 'btn-danger' : 'btn-success'}`}
          onClick={onToggleRecording}
          disabled={!hasPermission}
        >
          {isRecording ? (
            <>
              <i className="bi bi-stop-circle me-2"></i>
              Stop Recording
            </>
          ) : (
            <>
              <i className="bi bi-record-circle me-2"></i>
              Start Recording
            </>
          )}
        </button>
        
        {videoURL && (
          <button 
            type="button"
            className="btn btn-primary"
            onClick={handleDownload}
          >
            <i className="bi bi-download me-2"></i>
            Download
          </button>
        )}
      </div>
      
      <div className="mt-3 small text-muted">
        {isRecording ? (
          <p className="text-danger">
            <span className="blink">⚫</span> Recording in progress...
          </p>
        ) : (
          <p>Click 'Start Recording' to record your interview session.</p>
        )}
      </div>
    </div>
  );
}

export default VideoRecorder;
