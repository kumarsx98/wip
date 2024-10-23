import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

//const baseURL = 'http://localhost:8001'; // Change this to your backend URL
const baseURL = 'http://oad-ai.abbvienet.com:8001';

const getCookie = (name) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === `${name}=`) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

const AutoUploadManager = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [uploadDetails, setUploadDetails] = useState([]);
  const [schedulerStatus, setSchedulerStatus] = useState('Not running');

  const autoUploadIntervalRef = useRef(null);
  const statusCheckIntervalRef = useRef(null);

  const axiosInstance = axios.create({
    baseURL: baseURL,
    timeout: 300000, // 5 minutes timeout
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/json',
    }
  });

  // Fetch upload status
  const fetchUploadStatus = async () => {
    try {
      const response = await axiosInstance.get('/chatbot1/get-upload-status/');
      if (response.data.upload_details) {
        setUploadDetails(response.data.upload_details);

        const hasPendingUploads = response.data.upload_details.some(
          detail => detail.status === 'PENDING'
        );

        if (hasPendingUploads) {
          setTimeout(fetchUploadStatus, 3000); // Check every 3 seconds for pending uploads
        }
      }
      return response.data;
    } catch (error) {
      console.error('Error fetching upload status:', error);
      setMessage(`Error fetching status: ${error.message}`);
      return null;
    }
  };

  // Handle auto upload
  const handleAutoUpload = async () => {
    setIsLoading(true);
    setMessage('Starting auto-upload process...');
    try {
      const response = await axiosInstance.post('/chatbot1/trigger-auto-upload/');
      if (response.data.status === 'success') {
        setMessage(`Auto-upload completed successfully. Processed ${response.data.processed_files || 0} files.`);
        await fetchUploadStatus();
      } else {
        setMessage(`Auto-upload completed with some issues: ${response.data.message}`);
      }
    } catch (error) {
      console.error('Error during auto-upload:', error);
      setMessage(`Error during auto-upload: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUploadStatus();
  }, []);

  useEffect(() => {
    if (schedulerStatus === 'Running') {
      autoUploadIntervalRef.current = setInterval(handleAutoUpload, 600000); // Auto upload every 10 minutes
      statusCheckIntervalRef.current = setInterval(fetchUploadStatus, 180000); // Check status every 3 minutes
    } else {
      clearInterval(autoUploadIntervalRef.current);
      clearInterval(statusCheckIntervalRef.current);
    }

    // Cleanup on unmount or status change
    return () => {
      clearInterval(autoUploadIntervalRef.current);
      clearInterval(statusCheckIntervalRef.current);
    };
  }, [schedulerStatus]);

  const toggleScheduler = () => {
    if (schedulerStatus === 'Running') {
      setSchedulerStatus('Not running');
      setMessage('Scheduler stopped.');
    } else {
      setSchedulerStatus('Running');
      setMessage('Scheduler started.');
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    return timestamp ? new Date(timestamp).toLocaleString() : 'N/A';
  };

  return (
    <div style={{ border: '1px solid black', padding: '20px', margin: '20px', color: 'white', backgroundColor: '#333' }}>
      <h2>Auto Upload Manager</h2>

      <div style={{ marginBottom: '20px' }}>
        <button
          onClick={toggleScheduler}
          style={{
            marginRight: '10px',
            padding: '10px',
            backgroundColor: schedulerStatus === 'Running' ? '#FF5733' : '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          {schedulerStatus === 'Running' ? 'Stop Scheduler' : 'Start Scheduler'}
        </button>

        <button
          onClick={handleAutoUpload}
          disabled={isLoading}
          style={{
            padding: '10px',
            backgroundColor: '#008CBA',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
          }}
        >
          {isLoading ? 'Processing...' : 'Trigger Auto Upload'}
        </button>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <p>Scheduler Status: <strong>{schedulerStatus}</strong></p>
        {message && (
          <p style={{ color: '#FFA500' }}>
            Status: {message}
          </p>
        )}
      </div>

      <h3>Recent Uploads:</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid white', padding: '8px' }}>File Name</th>
            <th style={{ border: '1px solid white', padding: '8px' }}>Status</th>
            <th style={{ border: '1px solid white', padding: '8px' }}>Source</th>
            <th style={{ border: '1px solid white', padding: '8px' }}>Task ID</th>
            <th style={{ border: '1px solid white', padding: '8px' }}>Timestamp</th>
            <th style={{ border: '1px solid white', padding: '8px' }}>Preview</th>
          </tr>
        </thead>
        <tbody>
          {uploadDetails.map((detail, index) => (
            <tr key={index}>
              <td style={{ border: '1px solid white', padding: '8px' }}>
                {decodeURIComponent(detail.file_name)}
              </td>
              <td style={{
                border: '1px solid white',
                padding: '8px',
                color: detail.status === 'COMPLETED' ? '#4CAF50' :
                       detail.status === 'FAILED' ? '#ff0000' : '#FFA500'
              }}>
                {detail.status}
              </td>
              <td style={{ border: '1px solid white', padding: '8px' }}>
                {detail.source}
              </td>
              <td style={{ border: '1px solid white', padding: '8px' }}>
                {detail.task_id || 'N/A'}
              </td>
              <td style={{ border: '1px solid white', padding: '8px' }}>
                {formatTimestamp(detail.timestamp)}
              </td>
              <td style={{ border: '1px solid white', padding: '8px' }}>
                {detail.preview_url ? (
                  <a href={detail.preview_url} target="_blank" rel="noopener noreferrer" style={{ color: '#00BFFF', textDecoration: 'underline' }}>
                    View Preview
                  </a>
                ) : 'Not available'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AutoUploadManager;
