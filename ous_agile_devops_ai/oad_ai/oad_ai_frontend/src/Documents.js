import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

//const baseURL = 'http://localhost:8001'; // Define your backend base URL here
const baseURL = 'http://oad-ai.abbvienet.com:8001';


function Documents() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [sortField, setSortField] = useState('filename');
  const [sortDirection, setSortDirection] = useState('asc');
  const { sourceName } = useParams();
  const navigate = useNavigate();

  const handleSort = (field) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const sortDocuments = (docs) => docs.sort((a, b) => {
    let comparison = 0;
    if (a[sortField] < b[sortField]) {
      comparison = -1;
    } else if (a[sortField] > b[sortField]) {
      comparison = 1;
    }
    return sortDirection === 'asc' ? comparison : -comparison;
  });

  const checkPreviewAvailability = async (previewUrl) => {
    try {
      await axios.head(previewUrl);
      return true;
    } catch (error) {
      return false;
    }
  };

  const fetchDocuments = async (source) => {
    setIsLoading(true);
    setMessage('');

    try {
      const response = await axios.get(`${baseURL}/chatbot1/list-documents/${source}/`, {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        withCredentials: true,
      });

      if (response.status === 200 && response.data.documents) {
        const docPromises = response.data.documents.documents.map(async (doc) => {
          const filename = `${source}#${doc.filename}`;
          const previewUrl = `${baseURL}/media/previews/${encodeURIComponent(filename)}`;

          return {
            ...doc,
            displayName: doc.filename,
            preview_url: previewUrl,
            isPreviewAvailable: await checkPreviewAvailability(previewUrl),
          };
        });

        const docs = await Promise.all(docPromises);
        setDocuments(docs);
        setMessage(docs.length === 0 ? 'No documents found.' : '');
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

  useEffect(() => {
    if (sourceName) {
      fetchDocuments(sourceName);
    }
  }, [sourceName]);

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
      const response = await axios.post(`${baseURL}/chatbot1/sync-source/${sourceName}/`, {}, {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        withCredentials: true,
      });
      alert(response.data.message);
      fetchDocuments(sourceName);
    } catch (error) {
      console.error('Error syncing source:', error);
      console.error('Error details:', error.response?.data);
      alert(
        error.response?.data?.error || 'An error occurred during synchronization. Please check the server logs for more details.'
      );
    }
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile || !sourceName) {
      setMessage('Please select a file and a source to upload.');
      return;
    }

    setIsLoading(true);
    setMessage('');
    setUploadProgress(0);
    setUploadStatus('Uploading document...');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post(`${baseURL}/upload_document/${sourceName}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        withCredentials: true,
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
          setUploadStatus(`Uploading: ${percentCompleted}%`);
        },
      });

      console.log('Full API Response:', response.data);

      if (response.status === 200 || response.status === 201) {
        setUploadStatus('Document uploaded successfully!');

        // Add a delay before fetching the documents to ensure that the backend processing is complete
        setTimeout(() => {
          fetchDocuments(sourceName);
        }, 1000); // Optionally refresh the document list
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

  const handleDelete = async (documentId, filename) => {
    if (!window.confirm(`Are you sure you want to delete ${filename}?`)) return;

    setIsLoading(true);
    setMessage('');

    try {
      const response = await axios.delete(`${baseURL}/chatbot1/delete-document/${sourceName}/${documentId}/`, {
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
        },
        withCredentials: true,
      });

      if (response.status === 204) {
        setDocuments((previousDocs) => previousDocs.filter((doc) => doc.id !== documentId));
        setMessage(`${filename} was deleted successfully.`);
        fetchDocuments(sourceName);
      } else {
        setMessage('An error occurred while deleting the document.');
      }
    } catch (error) {
      console.error('Error during document deletion:', error);
      setMessage(error.response?.data?.error || 'An error occurred while deleting the document.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderDocuments = () => (
    <div>
      {documents.length > 0 ? (
        <>
          <p>Total documents: {documents.length}</p>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px', backgroundColor: '#fff' }}>
            <thead>
              <tr style={{ backgroundColor: '#f8f9fa' }}>
                <th
                  style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left', cursor: 'pointer' }}
                  onClick={() => handleSort('filename')}
                >
                  Filename {sortField === 'filename' && (sortDirection === 'asc' ? '▲' : '▼')}
                </th>
                <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Preview</th>
                <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Delete</th>
              </tr>
            </thead>
            <tbody>
              {sortDocuments(documents).map((document, index) => (
                <tr key={document.id || index} style={{ backgroundColor: '#fff' }}>
                  <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{document.displayName}</td>
                  <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>
                    {document.isPreviewAvailable ? (
                      <a
                        href={document.preview_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: '#00BFFF', textDecoration: 'underline' }}
                      >
                        View Preview
                      </a>
                    ) : (
                      'File is not available for preview'
                    )}
                  </td>
                  <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>
                    <button
                      onClick={() => handleDelete(document.id, document.displayName)}
                      style={{ backgroundColor: '#E57373', color: '#fff', border: 'none', padding: '10px', cursor: 'pointer' }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      ) : (
        <p>No documents found in {sourceName}.</p>
      )}
    </div>
  );

  const buttonStyle = {
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    padding: '10px 20px',
    marginRight: '10px',
    cursor: 'pointer',
    fontSize: '13px',
    display: 'inline-block',
    textDecoration: 'none'
  };

  const uploadButtonStyle = {
    backgroundColor: '#4CAF50',
    color: '#fff',
    border: 'none',
    padding: '10px 20px',
    marginRight: '10px',
    cursor: 'pointer',
    fontSize: '13px',
    display: 'inline-block'
  };

  const syncButtonStyle = {
    backgroundColor: '#FFB74D',
    color: '#fff',
    border: 'none',
    padding: '10px 20px',
    marginRight: '10px',
    cursor: 'pointer',
    fontSize: '13px',
    display: 'inline-block'
  };

  const chatButtonStyle = {
    backgroundColor: '#ff7f0e',
    color: '#fff',
    border: 'none',
    padding: '8px 16px',
    cursor: 'pointer',
    marginRight: '10px',
    display: 'inline-block',
    textDecoration: 'none',
    fontSize: '14px'
  };

  return (
    <div style={{ backgroundColor: '#fff', padding: '20px' }}>
      <h1 style={{ color: '#444' }}>Documents in {sourceName}</h1>
      <div style={{ marginBottom: '20px', display: 'flex', alignItems: 'center' }}>
        <button onClick={() => navigate('/sources')} style={buttonStyle}>Back to Sources</button>
        <input type="file" onChange={handleFileChange} style={{ marginRight: '10px' }} />
        <button onClick={handleUpload} style={uploadButtonStyle}>Upload Document</button>
        <button onClick={handleSyncSource} style={syncButtonStyle}>Sync Source</button>
        <a
          href={`/chat-with-source/${sourceName}`}
          target="_blank"
          rel="noopener noreferrer"
          style={chatButtonStyle}
        >
          Chat with Source
        </a>
      </div>
      {message && <p>{message}</p>}
      {isLoading && <p>Loading...</p>}
      {!isLoading && renderDocuments()}
      {uploadStatus && (
        <div>
          <p>{uploadStatus}</p>
          <progress value={uploadProgress} max="100">{uploadProgress}%</progress>
        </div>
      )}
    </div>
  );
}

export default Documents;
