//listsources.js:

import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

function ListSources() {
    const [globalSources, setGlobalSources] = useState([]);
    const [privateSources, setPrivateSources] = useState([]);
    const [documents, setDocuments] = useState([]);
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [uploadStatus, setUploadStatus] = useState('');
    const [uploadSteps, setUploadSteps] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [sortField, setSortField] = useState('filename');
    const [sortDirection, setSortDirection] = useState('asc');
    const { sourceName } = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        if (sourceName) {
            fetchDocuments(sourceName);
        } else {
            refreshData();
        }
    }, [sourceName]);

    const trimPath = (path) => {
        return path.replace('/chatbot1/media/documents/', '');
    };

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
        setDocuments([]);
    };

    const fetchSources = async () => {
        setIsLoading(true);
        setMessage('');

        try {
            const response = await axios.get('/chatbot1/list-sources/', {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                withCredentials: true,
            });

            if (response.status === 200) {
                const { global, private: privateSources } = response.data.external_sources;
                setGlobalSources(global.filter(source => source.name.startsWith('oad-')) || []);
                setPrivateSources(privateSources.filter(source => source.name.startsWith('oad-')) || []);
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

        try {
            const response = await axios.get(`/chatbot1/list-documents/${source}/`, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                withCredentials: true,
            });

            if (response.status === 200 && response.data.documents) {
                setDocuments(
                    response.data.documents.documents.map((doc) => ({
                        ...doc,
                        path: trimPath(doc.path || `/chatbot1/media/documents/${source}/${doc.filename}`),
                        preview_url: `/media/previews/${source}/${doc.filename}`,
                    }))
                );
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
            const response = await axios.post(`/chatbot1/sync-source/${sourceName}/`, {}, {
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
            alert(error.response?.data?.error || 'An error occurred during synchronization. Please check the server logs for more details.');
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
        setUploadStatus('Preparing upload...');
        setUploadSteps([]);

        try {
            const formData = new FormData();
            formData.append('file', selectedFile);

            const response = await axios.post(`/chatbot1/upload-document/${sourceName}/`, formData, {
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
                setUploadStatus('Upload successful. Processing document...');
                setUploadSteps((prevSteps) => [...prevSteps, 'Document uploaded successfully']);
                await pollUploadStatus(sourceName, response.data.task_id);
            } else if (response.status === 202) {
                setUploadStatus('Document replaced successfully. Processing...');
                setUploadSteps((prevSteps) => [...prevSteps, 'Document replaced successfully']);
                await pollUploadStatus(sourceName, response.data.task_id);
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
            const response = await axios.delete(`/chatbot1/delete-document/${sourceName}/${documentId}/`, {
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                withCredentials: true,
            });

            if (response.status === 204) {
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

    const pollUploadStatus = async (source, taskId, maxAttempts = 10) => {
        for (let i = 0; i < maxAttempts; i++) {
            try {
                const response = await axios.get(`/chatbot1/check-upload-status/${source}/${taskId}/`, {
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    withCredentials: true,
                });

                console.log('Poll response:', response.data);

                if (response.data.status === 'SUCCESS') {
                    setUploadStatus('Upload and processing completed successfully');
                    setUploadSteps((prevSteps) => [...prevSteps, 'Document processed successfully']);
                    setMessage(`Upload completed successfully.\nFull Response: ${JSON.stringify(response.data.full_response, null, 2)}`);
                    await fetchDocuments(source);
                    return;
                } else if (response.data.status === 'ERROR') {
                    setUploadStatus('Upload failed');
                    setUploadSteps((prevSteps) => [...prevSteps, 'Error during document processing']);
                    setMessage(`Upload failed.\nError: ${response.data.message}\nFull Response: ${JSON.stringify(response.data.full_response, null, 2)}`);
                    return;
                }

                setUploadStatus(`Processing document... (Attempt ${i + 1}/${maxAttempts})`);
                setUploadSteps((prevSteps) => [...prevSteps, `Processing attempt ${i + 1}`]);
                await new Promise((resolve) => setTimeout(resolve, 5000));
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

    const navigateToChat = (sourceName) => {
        navigate(`/chat-with-source/${sourceName}`);
    };

    const renderSourceTable = (sources, title) => (
        <div>
            <h2 style={{ color: '#444', marginTop: '20px' }}>{title}</h2>
            {sources.length > 0 ? (
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px', backgroundColor: '#fff' }}>
                    <thead>
                        <tr style={{ backgroundColor: '#f8f9fa' }}>
                            <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Name</th>
                            <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Visibility</th>
                            <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Model</th>
                            <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>ID</th>
                            <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sources.map((source, index) => (
                            <tr key={index} style={{ backgroundColor: '#fff' }}>
                                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>
                                    <Link to={`/sources/${source.name}/documents`} style={{ color: '#007bff', textDecoration: 'none' }}>
                                        {source.name}
                                    </Link>
                                </td>
                                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{source.visibility}</td>
                                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{source.model}</td>
                                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{source.id}</td>
                                <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>
                                    <button
                                        onClick={() => navigateToChat(source.name)}
                                        style={{ backgroundColor: '#ff7f0e', color: '#fff', border: 'none', padding: '10px 20px', cursor: 'pointer' }}>
                                        Chat with Source
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No {title.toLowerCase()} found.</p>
            )}
        </div>
    );

    const renderDocuments = () => (
        <div>
            <h2 style={{ color: '#444', marginTop: '20px' }}>Documents in {sourceName}</h2>
            <div style={{ marginBottom: '20px' }}>
                <button onClick={() => navigate('/sources')} style={buttonStyle}>Back to Sources</button>
                <input type="file" onChange={handleFileChange} style={{ marginRight: '10px' }} />
                <button onClick={handleUpload} style={uploadButtonStyle}>Upload Document</button>
                <button onClick={handleSyncSource} style={syncButtonStyle}>Sync Source</button>
                <button
                    onClick={() => navigateToChat(sourceName)}
                    style={{ backgroundColor: '#ff7f0e', color: '#fff', border: 'none', padding: '10px 20px', cursor: 'pointer' }}
                >
                    Chat with Source
                </button>
            </div>
            {uploadStatus && (
                <div>
                    <p>{uploadStatus}</p>
                    <progress value={uploadProgress} max="100">{uploadProgress}%</progress>
                    {uploadSteps.map((step, index) => (
                        <p key={index}>{step}</p>
                    ))}
                </div>
            )}
            {documents.length > 0 ? (
                <>
                    <p>Total documents: {documents.length}</p>
                    <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px', backgroundColor: '#fff' }}>
                        <thead>
                            <tr style={{ backgroundColor: '#f8f9fa' }}>
                                <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left', cursor: 'pointer' }} onClick={() => handleSort('filename')}>
                                    Filename {sortField === 'filename' && (sortDirection === 'asc' ? '▲' : '▼')}
                                </th>
                                <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left', cursor: 'pointer' }} onClick={() => handleSort('path')}>
                                    Path {sortField === 'path' && (sortDirection === 'asc' ? '▲' : '▼')}
                                </th>
                                <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>ID</th>
                                <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Preview</th>
                                <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Delete</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sortDocuments(documents).map((document, index) => (
                                <tr key={document.id || index} style={{ backgroundColor: '#fff' }}>
                                    <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{document.filename}</td>
                                    <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{document.path}</td>
                                    <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{document.id}</td>
                                    <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>
                                        {document.preview_url ? (
                                            <a
                                                href={document.preview_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                style={{ color: '#00BFFF', textDecoration: 'underline' }}
                                            >
                                                View Preview
                                            </a>
                                        ) : (
                                            'Not available'
                                        )}
                                    </td>
                                    <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>
                                        <button
                                            onClick={() => handleDelete(document.id, document.filename)}
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
        cursor: 'pointer'
    };

    const uploadButtonStyle = {
        backgroundColor: '#4CAF50',
        color: '#fff',
        border: 'none',
        padding: '10px 20px',
        marginRight: '10px',
        cursor: 'pointer'
    };

    const syncButtonStyle = {
        backgroundColor: '#FFB74D',
        color: '#fff',
        border: 'none',
        padding: '10px 20px',
        marginRight: '10px',
        cursor: 'pointer'
    };

    return (
        <div style={{ backgroundColor: '#fff', padding: '20px' }}>
            <h1 style={{ color: '#444' }}>Source {sourceName ? 'Documents' : 'List'}</h1>
            {message && <p>{message}</p>}
            {isLoading && <p>Loading...</p>}
            {!isLoading && (
                <>
                    {!sourceName && renderSourceTable(globalSources, 'Global Sources')}
                    {!sourceName && renderSourceTable(privateSources, 'Private Sources')}
                    {sourceName && renderDocuments()}
                </>
            )}
        </div>
    );
}

export default ListSources;
