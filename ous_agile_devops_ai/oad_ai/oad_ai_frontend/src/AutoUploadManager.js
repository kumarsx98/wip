import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import debounce from 'lodash/debounce';

const baseURL = 'http://oad-ai.abbvienet.com:8001'; // Define your backend base URL

const AutoUploadManager = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [uploadDetails, setUploadDetails] = useState([]);
  const [schedulerStatus, setSchedulerStatus] = useState('Not running');
  const [networkErrorCount, setNetworkErrorCount] = useState(0);

  // Helper to parse and format timestamp
  const parseTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) {
      return 'N/A';
    }
    return date.toLocaleString();
  };

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

  const axiosInstance = axios.create({
    baseURL: baseURL,
    timeout: 120000,  // 2 minutes
    headers: { 'X-CSRFToken': getCookie('csrftoken') }
  });

  const fetchPreviews = async () => {
    try {
      const response = await axiosInstance.get('/chatbot1/list-previews/');
      console.log('Fetched previews:', response.data);
      return response.data.previews || [];
    } catch (error) {
      console.error('Error fetching previews:', error.message);
      setMessage(`Error fetching previews: ${error.message}`);
      return [];
    }
  };

  const retryWithBackoff = async (fn, retries = 5, delay = 2000) => {
    try {
      return await fn();
    } catch (error) {
      if (retries > 0) {
        console.warn(`Retrying in ${delay / 1000} seconds... ${retries} attempts left. Reason: ${error.message}`);
        await new Promise((resolve) => setTimeout(resolve, delay));
        return retryWithBackoff(fn, retries - 1, delay * 2);  // Double the delay for each retry
      } else {
        throw error;
      }
    }
  };

  const handleUploadFile = async (fileDetail) => {
    try {
      await retryWithBackoff(async () => {
        console.log(`Uploading file: ${fileDetail.file_name}`);
        await axiosInstance.post('/chatbot1/auto-upload/', { file: fileDetail.file_name });  // Use your existing endpoint
        // Update status immediately on successful upload
        setUploadDetails(prevDetails =>
          prevDetails.map(detail =>
            detail.uniqueId === fileDetail.uniqueId ? { ...detail, status: 'COMPLETED' } : detail
          )
        );
      });
    } catch (error) {
      console.error(`Failed to upload ${fileDetail.file_name}:`, error.message);
      if (!error.message.includes('Network Error')) {
        // Update status to 'FAILED' if not network error
        setUploadDetails(prevDetails =>
          prevDetails.map(detail =>
            detail.uniqueId === fileDetail.uniqueId ? { ...detail, status: 'FAILED' } : detail
          )
        );
      }
      throw error;  // Re-throw to trigger retry mechanism
    }
  };

  const fetchAndProcessUploads = async () => {
    try {
      const previews = await fetchPreviews();
      const response = await axiosInstance.get('/chatbot1/get-upload-status/');
      console.log('Fetched upload status:', response.data);

      const updatedDetailsMap = new Map();
      response.data.upload_details.forEach((detail, index) => {
        const uniqueId = `${detail.file_name}_${detail.timestamp}_${index}`;
        const encodedFileName = encodeURIComponent(detail.file_name);
        const previewUrl = previews.find((preview) => preview.includes(detail.file_name)) || '';
        const updatedDetail = {
          uniqueId,
          ...detail,
          file_name: encodedFileName,
          timestamp: detail.timestamp,
          preview_url: previewUrl ? `${baseURL}/media/previews/${encodedFileName}` : 'Not available',
        };
        updatedDetailsMap.set(uniqueId, updatedDetail); // Use uniqueId to ensure uniqueness
      });

      const updatedDetails = Array.from(updatedDetailsMap.values());
      setUploadDetails(updatedDetails);
      setSchedulerStatus(response.data.scheduler_status);

      // Set to maintain uploaded files
      const uploadedFiles = new Set(updatedDetails.filter(detail => detail.status === 'COMPLETED').map(detail => detail.file_name));

      // Process pending uploads immediately after fetching status
      for (const fileDetail of updatedDetails) {
        if (fileDetail.status === 'PENDING' && !uploadedFiles.has(fileDetail.file_name)) {
          await handleUploadFile(fileDetail);
          uploadedFiles.add(fileDetail.file_name);  // Add file name to the set after successful upload
        }
      }
    } catch (error) {
      console.error('Error fetching upload status:', error.message);
      setMessage(`Error fetching upload status: ${error.message}`);
    }
  };

  // Debounce the fetch and process uploads to avoid overlapping requests.
  const debouncedFetchAndProcessUploads = useCallback(
    debounce(fetchAndProcessUploads, 1000),
    []
  );

  useEffect(() => {
    const interval = setInterval(() => {
      debouncedFetchAndProcessUploads();
    }, 600000);  // 10 minutes in milliseconds

    // Initial fetch and start scheduler
    debouncedFetchAndProcessUploads();

    return () => clearInterval(interval);  // Cleanup interval on unmount
  }, []);

  const handleAutoUpload = async () => {
    setIsLoading(true);
    setMessage('');
    setNetworkErrorCount(0);

    try {
      setMessage('Initiating auto-upload process');
      console.log('Initiating auto-upload process');

      debouncedFetchAndProcessUploads();

      setMessage('Auto-upload process completed.');
    } catch (error) {
      console.error('Error during auto-upload:', error.message);
      setMessage(`Error during auto-upload: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const startScheduler = async () => {
    try {
      const response = await axiosInstance.post('/chatbot1/start-scheduler/');
      console.log('Start scheduler response:', response.data);

      setSchedulerStatus(response.data.status === 'success' ? 'Running' : 'Not running');
      setMessage(response.data.message || 'Scheduler started successfully.');
    } catch (error) {
      console.error('Error starting scheduler:', error.message);
      setMessage(`Error starting scheduler: ${error.message}`);
    }
  };

  const formatTimestamp = (timestamp) => {
    return timestamp ? new Date(timestamp).toLocaleString() : 'N/A';
  };

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
          {uploadDetails
            .filter(detail => detail.status === 'COMPLETED' || detail.status === 'FAILED')
            .map((detail, index) => (
              <tr key={`${detail.uniqueId}-${index}`}>
                <td style={{ border: '1px solid white', padding: '8px' }}>{decodeURIComponent(detail.file_name)}</td>
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
