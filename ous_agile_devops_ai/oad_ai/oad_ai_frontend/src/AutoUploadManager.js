import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const AUTO_UPLOAD_URL = '/chatbot1/auto-upload/';
const START_SCHEDULER_URL = '/chatbot1/start-scheduler/';
const GET_UPLOAD_STATUS_URL = '/chatbot1/get-upload-status/';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function AutoUploadManager() {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [uploadDetails, setUploadDetails] = useState([]);
  const [schedulerStatus, setSchedulerStatus] = useState('Not running');
  const [lastAutoUploadResponse, setLastAutoUploadResponse] = useState(null);
  const [autoUploadProgress, setAutoUploadProgress] = useState(0);
  const [autoUploadSteps, setAutoUploadSteps] = useState([]);

  const fetchUploadStatus = useCallback(async () => {
    try {
      console.log('Fetching upload status...');
      const response = await axios.get(GET_UPLOAD_STATUS_URL, {
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
        },
      });
      console.log('Upload status response:', response.data);
      if (response.data.status === 'success') {
        setUploadDetails(response.data.upload_details || []);
        setSchedulerStatus(response.data.scheduler_status || 'Not running');
      } else {
        setMessage('Error fetching upload status: ' + response.data.message);
      }
    } catch (error) {
      console.error('Error fetching upload status:', error);
      setMessage('Error fetching upload status: ' + (error.response?.data?.message || error.message));
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    axios.defaults.withCredentials = true;

    const fetchData = async () => {
      if (isMounted) {
        await fetchUploadStatus();
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 60000); // Refresh every 1 minute

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [fetchUploadStatus]);

  const handleAutoUpload = async () => {
    setIsLoading(true);
    setMessage('');
    setAutoUploadProgress(0);
    setAutoUploadSteps([]);
    try {
      console.log('Triggering auto-upload...');
      setAutoUploadSteps(prevSteps => [...prevSteps, 'Initiating auto-upload process']);
      const response = await axios.post(AUTO_UPLOAD_URL, {}, {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setAutoUploadProgress(percentCompleted);
        }
      });
      console.log('Auto-upload response:', response.data);
      setLastAutoUploadResponse(response.data);
      setMessage(response.data.message || 'Auto-upload process completed.');
      setAutoUploadSteps(prevSteps => [...prevSteps, 'Auto-upload process completed']);
      await fetchUploadStatus(); // Refresh the status immediately after auto-upload
    } catch (error) {
      console.error('Error during auto-upload:', error);
      setMessage('Error during auto-upload: ' + (error.response?.data?.message || error.message));
      setAutoUploadSteps(prevSteps => [...prevSteps, 'Error occurred during auto-upload']);
    } finally {
      setIsLoading(false);
      setAutoUploadProgress(100);
    }
  };

  const startScheduler = async () => {
    try {
      console.log('Starting scheduler...');
      const response = await axios.post(START_SCHEDULER_URL, {}, {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
      });
      console.log('Start scheduler response:', response.data);
      setSchedulerStatus(response.data.status === 'success' ? 'Running' : 'Not running');
      setMessage(response.data.message || 'Scheduler started successfully.');
      await fetchUploadStatus(); // Refresh the status immediately after starting the scheduler
    } catch (error) {
      console.error('Error starting scheduler:', error);
      setMessage('Error starting scheduler: ' + (error.response?.data?.message || error.message));
    }
  };

  return (
    <div style={{ border: '1px solid black', padding: '20px', margin: '20px', color: 'white', backgroundColor: '#333' }}>
      <h2>Auto Upload Manager</h2>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={startScheduler} disabled={schedulerStatus === 'Running'} style={{ marginRight: '10px', padding: '10px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          {schedulerStatus === 'Running' ? 'Scheduler Running' : 'Start Scheduler'}
        </button>
        <button onClick={handleAutoUpload} disabled={isLoading} style={{ padding: '10px', backgroundColor: '#008CBA', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          {isLoading ? 'Uploading...' : 'Trigger Auto Upload'}
        </button>
      </div>
      <p>Scheduler Status: <strong>{schedulerStatus}</strong></p>
      {message && <p style={{ color: '#FFA500' }}>Message: {message}</p>}

      {isLoading && (
        <div style={{ marginTop: '20px' }}>
          <h3>Auto-Upload Progress:</h3>
          <progress value={autoUploadProgress} max="100" style={{ width: '100%' }}></progress>
          <p>{autoUploadProgress}% Complete</p>
          <ul>
            {autoUploadSteps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ul>
        </div>
      )}

      {lastAutoUploadResponse && (
        <div style={{ marginTop: '20px', backgroundColor: '#444', padding: '10px', borderRadius: '4px' }}>
          <h3>Last Auto-Upload Response:</h3>
          <p>Status: <strong>{lastAutoUploadResponse.status}</strong></p>
          <p>Message: {lastAutoUploadResponse.message}</p>
          {Array.isArray(lastAutoUploadResponse.processed_files) && (
            <p>Processed Files: {lastAutoUploadResponse.processed_files.join(', ')}</p>
          )}
        </div>
      )}

      <h3>Recent Uploads:</h3>
      {uploadDetails.length > 0 ? (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ border: '1px solid white', padding: '8px' }}>File Name</th>
                <th style={{ border: '1px solid white', padding: '8px' }}>Source</th>
                <th style={{ border: '1px solid white', padding: '8px' }}>Status</th>
                <th style={{ border: '1px solid white', padding: '8px' }}>Task ID</th>
                <th style={{ border: '1px solid white', padding: '8px' }}>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {uploadDetails.map((detail, index) => (
                <tr key={`${detail.file_name}-${index}`}>
                  <td style={{ border: '1px solid white', padding: '8px' }}>{detail.file_name}</td>
                  <td style={{ border: '1px solid white', padding: '8px' }}>{detail.source}</td>
                  <td style={{ border: '1px solid white', padding: '8px' }}>{detail.status}</td>
                  <td style={{ border: '1px solid white', padding: '8px' }}>{detail.task_id}</td>
                  <td style={{ border: '1px solid white', padding: '8px' }}>{new Date(detail.timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p>No recent uploads</p>
      )}
    </div>
  );
}

export default AutoUploadManager;
