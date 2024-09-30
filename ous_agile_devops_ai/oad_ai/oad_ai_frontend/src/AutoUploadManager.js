import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AutoUploadManager = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [uploadDetails, setUploadDetails] = useState([]);
  const [schedulerStatus, setSchedulerStatus] = useState('Not running');
  const [autoUploadProgress, setAutoUploadProgress] = useState(0);
  const [autoUploadSteps, setAutoUploadSteps] = useState([]);

  const fetchUploadStatus = async () => {
    try {
      const response = await axios.get('/chatbot1/get-upload-status/', {
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
      });

      const previews = await fetchPreviews();
      const updatedDetails = response.data.upload_details.map((detail) => {
        const encodedFileName = encodeURIComponent(detail.file_name);
        const previewUrl = previews.find((preview) => preview.includes(detail.file_name)) || '';
        return {
          ...detail,
          preview_url: previewUrl ? `http://10.72.19.8:8001/media/previews/${encodedFileName}` : 'Not available',
        };
      });
      setUploadDetails(updatedDetails);
      setSchedulerStatus(response.data.scheduler_status);
    } catch (error) {
      console.error('Error fetching upload status:', error);
      setMessage(`Error fetching upload status: ${error.message}`);
    }
  };

  useEffect(() => {
    fetchUploadStatus();
  }, [fetchUploadStatus]);

  const fetchPreviews = async () => {
    try {
      const response = await axios.get('/chatbot1/list-previews/');
      return response.data.previews || [];
    } catch (error) {
      console.error('Error fetching previews:', error);
      return [];
    }
  };

  const handleAutoUpload = async () => {
    setIsLoading(true);
    setMessage('');
    setAutoUploadProgress(0);
    setAutoUploadSteps([]);
    try {
      setAutoUploadSteps((prevSteps) => [...prevSteps, 'Initiating auto-upload process']);

      const response = await axios.post('/chatbot1/auto-upload/', {}, {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setAutoUploadProgress(percentCompleted);
        },
      });

      setMessage(response.data.message || 'Auto-upload process completed.');
      setAutoUploadSteps((prevSteps) => [...prevSteps, 'Auto-upload process completed']);
      await fetchUploadStatus(); // Refresh the status immediately after auto-upload
    } catch (error) {
      console.error('Error during auto-upload:', error);
      setMessage(`Error during auto-upload: ${error.response?.data?.message || error.message}`);
      setAutoUploadSteps((prevSteps) => [...prevSteps, 'Error occurred during auto-upload']);
    } finally {
      setIsLoading(false);
      setAutoUploadProgress(100);
    }
  };

  const startScheduler = async () => {
    try {
      const response = await axios.post('/chatbot1/start-scheduler/', {}, {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
      });

      setSchedulerStatus(response.data.status === 'success' ? 'Running' : 'Not running');
      setMessage(response.data.message || 'Scheduler started successfully.');
    } catch (error) {
      console.error('Error starting scheduler:', error);
      setMessage(`Error starting scheduler: ${error.response?.data?.message || error.message}`);
    }
  };

  const formatTimestamp = (timestamp) => {
    return timestamp ? new Date(timestamp).toLocaleString() : 'N/A';
  };

  function getCookie(name) {
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
  }

  return (
    <div style={{ border: '1px solid black', padding: '20px', margin: '20px', color: 'white', backgroundColor: '#333' }}>
      <h2>Auto Upload Manager</h2>
      <div style={{ marginBottom: '20px' }}>
        <button
          onClick={startScheduler}
          disabled={schedulerStatus === 'Running'}
          style={{
            marginRight: '10px',
            padding: '10px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          {schedulerStatus === 'Running' ? 'Scheduler Running' : 'Start Scheduler'}
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
            cursor: 'pointer',
          }}
        >
          {isLoading ? 'Uploading...' : 'Trigger Auto Upload'}
        </button>
      </div>
      <p>
        Scheduler Status: <strong>{schedulerStatus}</strong>
      </p>
      {message && <p style={{ color: '#FFA500' }}>Message: {message}</p>}

      {isLoading && (
        <div style={{ marginTop: '20px' }}>
          <h3>Auto-Upload Progress:</h3>
          <progress value={autoUploadProgress} max='100' style={{ width: '100%' }}></progress>
          <p>{autoUploadProgress}% Complete</p>
          <ul>
            {autoUploadSteps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ul>
        </div>
      )}

      <h3>Recent Uploads:</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid white', padding: '8px' }}>File Name</th>
            <th style={{ border: '1px solid white', padding: '8px' }}>Source</th>
            <th style={{ border: '1px solid white', padding: '8px' }}>Status</th>
            <th style={{ border: '1px solid white', padding: '8px' }}>Task ID</th>
            <th style={{ border: '1px solid white', padding: '8px' }}>Timestamp</th>
            <th style={{ border: '1px solid white', padding: '8px' }}>Preview</th>
          </tr>
        </thead>
        <tbody>
          {uploadDetails.map((detail, index) => (
            <tr key={`${detail.file_name}-${index}`}>
              <td style={{ border: '1px solid white', padding: '8px' }}>{detail.file_name}</td>
              <td style={{ border: '1px solid white', padding: '8px' }}>{detail.source}</td>
              <td style={{ border: '1px solid white', padding: '8px' }}>{detail.status}</td>
              <td style={{ border: '1px solid white', padding: '8px' }}>{detail.task_id || 'N/A'}</td>
              <td style={{ border: '1px solid white', padding: '8px' }}>{formatTimestamp(detail.timestamp)}</td>
              <td style={{ border: '1px solid white', padding: '8px' }}>
                {detail.preview_url ? (
                  <a href={detail.preview_url} target='_blank' rel='noopener noreferrer' style={{ color: '#00BFFF', textDecoration: 'underline' }}>
                    View Preview
                  </a>
                ) : (
                  'Not available'
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AutoUploadManager;
