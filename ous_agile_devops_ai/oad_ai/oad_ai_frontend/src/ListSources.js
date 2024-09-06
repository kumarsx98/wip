import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ListSources() {
  const [globalSources, setGlobalSources] = useState([]);
  const [privateSources, setPrivateSources] = useState([]);
  const [selectedSource, setSelectedSource] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadSteps, setUploadSteps] = useState([]);
  const [sortField, setSortField] = useState('filename');
  const [sortDirection, setSortDirection] = useState('asc');


  const handleSort = (field) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const sortDocuments = (docs) => {
    return docs.sort((a, b) => {
      let comparison = 0;
      if (a[sortField] < b[sortField]) {
        comparison = -1;
      } else if (a[sortField] > b[sortField]) {
        comparison = 1;
      }
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  };




  const refreshData = async () => {
    await fetchSources();
    if (selectedSource) {
      await fetchDocuments(selectedSource);
    }
  };

  useEffect(() => {
    refreshData();
  }, []);

  const fetchSources = async () => {
    setIsLoading(true);
    setMessage('');

    try {
      const response = await axios.get('/chatbot1/list-sources/', {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        withCredentials: true
      });

      if (response.status === 200) {
        setGlobalSources(response.data.global_sources || []);
        setPrivateSources(response.data.private_sources || []);
      } else {
        setMessage('An error occurred while fetching the sources.');
      }
    } catch (error) {
      console.error('Error during source fetching:', error);
      setMessage(error.response?.data?.error || 'An error occurred while fetching the sources.');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDocuments = async (source) => {
  setIsLoading(true);
  setMessage('');
  setSelectedSource(source);

  try {
    const response = await axios.get(`/chatbot1/list-documents/${source}/`, {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      withCredentials: true
    });

    if (response.status === 200 && response.data.documents) {
      setDocuments(response.data.documents.documents.map(doc => ({
        ...doc,
        path: doc.path || `/chatbot1/media/documents/${source}/${doc.filename}`,
        created_at: doc.created_at || null,
        modified_at: doc.modified_at || null
      })));
      setMessage(response.data.documents.documents.length === 0 ? 'No documents found.' : '');
    } else {
      setMessage('An error occurred while fetching the documents.');
    }
  } catch (error) {
    console.error('Error during document fetching:', error);
    setMessage(error.response?.data?.error || 'An error occurred while fetching the documents.');
  } finally {
    setIsLoading(false);
  }
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

  const handleSyncSource = async () => {
    try {
      const response = await axios.post(`/chatbot1/sync-source/${selectedSource}/`, {}, {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        withCredentials: true
      });
      alert(response.data.message);
      fetchDocuments(selectedSource);
    } catch (error) {
      console.error('Error syncing source:', error);
      console.error('Error details:', error.response?.data);
      alert(error.response?.data?.error || 'An error occurred during synchronization. Please check the server logs for more details.');
    }
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile || !selectedSource) {
      setMessage('Please select a file and a source to upload.');
      return;
    }

    setIsLoading(true);
    setMessage('');
    setUploadProgress(0);
    setUploadStatus('Preparing upload...');
    setUploadSteps([]);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post(`/chatbot1/upload-document/${selectedSource}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        withCredentials: true,
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
          setUploadStatus(`Uploading: ${percentCompleted}%`);
        }
      });

      console.log('Full API Response:', response.data);

      if (response.status === 200 || response.status === 201) {
        setUploadStatus('Upload successful. Processing document...');
        setUploadSteps(prevSteps => [...prevSteps, 'Document uploaded successfully']);
        await pollUploadStatus(selectedSource, response.data.task_id);
      } else if (response.status === 202) {
        setUploadStatus('Document replaced successfully. Processing...');
        setUploadSteps(prevSteps => [...prevSteps, 'Document replaced successfully']);
        await pollUploadStatus(selectedSource, response.data.task_id);
      } else {
        setUploadStatus('Upload failed');
        setMessage('An error occurred while uploading the document.');
      }
    } catch (error) {
      console.error('Error during document upload:', error);
      setUploadStatus('Upload failed');
      setMessage(error.response?.data?.error || 'An error occurred while uploading the document.');
    } finally {
      setIsLoading(false);
      setUploadProgress(0);
      setSelectedFile(null);
    }
  };

  const pollUploadStatus = async (source, taskId, maxAttempts = 10) => {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        const response = await axios.get(`/chatbot1/check-upload-status/${source}/${taskId}/`, {
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
          },
          withCredentials: true
        });

        console.log('Poll response:', response.data);

        if (response.data.status === 'SUCCESS') {
          setUploadStatus('Upload and processing completed successfully');
          setUploadSteps(prevSteps => [...prevSteps, 'Document processed successfully']);
          setMessage(`Upload completed successfully.\nFull Response: ${JSON.stringify(response.data.full_response, null, 2)}`);
          await fetchDocuments(source);
          return;
        } else if (response.data.status === 'ERROR') {
          setUploadStatus('Upload failed');
          setUploadSteps(prevSteps => [...prevSteps, 'Error during document processing']);
          setMessage(`Upload failed.\nError: ${response.data.message}\nFull Response: ${JSON.stringify(response.data.full_response, null, 2)}`);
          return;
        }

        setUploadStatus(`Processing document... (Attempt ${i + 1}/${maxAttempts})`);
        setUploadSteps(prevSteps => [...prevSteps, `Processing attempt ${i + 1}`]);
        await new Promise(resolve => setTimeout(resolve, 5000));
      } catch (error) {
        console.error('Error polling upload status:', error);
        setUploadStatus('Error checking upload status');
        setMessage(`Error checking upload status: ${error.message}`);
        return;
      }
    }

    setUploadStatus('Upload status check timed out');
    setMessage('Upload status check timed out. The upload may still be in progress.');
  };

  const renderSourceList = (sources, title) => (
    <div>
      <h2 style={{ color: '#444', marginTop: '20px' }}>{title}</h2>
      {sources.length > 0 ? (
        <ul style={{ listStyleType: 'none', padding: 0 }}>
          {sources.map((source) => (
            <li key={source} style={{ marginBottom: '10px', border: '1px solid #ccc', padding: '10px', borderRadius: '4px' }}>
              <h3 style={{ margin: '0' }}>
                <a href="#" onClick={(e) => { e.preventDefault(); fetchDocuments(source); }} style={{ color: '#007bff', textDecoration: 'none' }}>
                  {source}
                </a>
              </h3>
            </li>
          ))}
        </ul>
      ) : (
        <p>No {title.toLowerCase()} found.</p>
      )}
    </div>
  );

 const renderDocuments = () => (
  <div>
    <h2 style={{ color: '#444', marginTop: '20px' }}>Documents in {selectedSource}</h2>
    {documents.length > 0 ? (
      <>
        <p>Total documents: {documents.length}</p>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa' }}>
              <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left', cursor: 'pointer' }} onClick={() => handleSort('filename')}>
                Filename {sortField === 'filename' && (sortDirection === 'asc' ? '▲' : '▼')}
              </th>
              <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left', cursor: 'pointer' }} onClick={() => handleSort('path')}>
                Path {sortField === 'path' && (sortDirection === 'asc' ? '▲' : '▼')}
              </th>
              <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left', cursor: 'pointer' }} onClick={() => handleSort('created_at')}>
                Created At {sortField === 'created_at' && (sortDirection === 'asc' ? '▲' : '▼')}
              </th>
              <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left', cursor: 'pointer' }} onClick={() => handleSort('modified_at')}>
                Modified At {sortField === 'modified_at' && (sortDirection === 'asc' ? '▲' : '▼')}
              </th>
            </tr>
          </thead>
          <tbody>
            {sortDocuments(documents).map((document, index) => (
              <tr key={document.id || index}>
                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{document.filename}</td>
                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>
                  {document.path && (
                    <a href={document.path} target="_blank" rel="noopener noreferrer" style={{ color: '#007bff' }}>
                      {document.path}
                    </a>
                  )}
                </td>
                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>
                  {document.created_at ? new Date(document.created_at).toLocaleString() : 'N/A'}
                </td>
                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>
                  {document.modified_at ? new Date(document.modified_at).toLocaleString() : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </>
    ) : (
      <p>No documents available in this source.</p>
    )}

    <button onClick={() => setSelectedSource(null)} style={{ marginTop: '20px', padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginRight: '10px' }}>
      Back to Sources
    </button>
    <button onClick={handleSyncSource} style={{ marginTop: '20px', padding: '10px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
      Sync Source
    </button>
  </div>
);

  const renderUploadSection = () => (
    <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '20px', borderRadius: '4px' }}>
      <h3>Upload Document</h3>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={isLoading || !selectedFile} style={{ marginLeft: '10px', padding: '10px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
        {isLoading ? 'Uploading...' : 'Upload Document'}
      </button>

      {uploadProgress > 0 && uploadProgress < 100 && (
        <div style={{ marginTop: '10px' }}>
          <progress value={uploadProgress} max="100"></progress>
          <span>{uploadProgress}%</span>
        </div>
      )}

      {uploadStatus && (
        <p style={{ marginTop: '10px', fontWeight: 'bold' }}>{uploadStatus}</p>
      )}

      {uploadSteps.length > 0 && (
        <div style={{ marginTop: '10px' }}>
          <h4>Upload Progress:</h4>
          <ul>
            {uploadSteps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  return (
    <div style={{ padding: '20px', backgroundColor: 'white', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ textAlign: 'center', color: '#333' }}>List of Sources</h1>
      {isLoading && !uploadStatus ? (
        <p style={{ textAlign: 'center' }}>Loading...</p>
      ) : (
        selectedSource ? (
          <>
            {renderDocuments()}
            {renderUploadSection()}
          </>
        ) : (
          <>
            {renderSourceList(globalSources, 'Global Sources')}
            {renderSourceList(privateSources, 'Private Sources')}
          </>
        )
      )}
      {message && <p style={{ color: 'red', textAlign: 'center' }}>{message}</p>}
    </div>
  );
}

export default ListSources;