import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

//const baseURL = 'http://localhost:8001';
const baseURL = 'http://oad-ai.abbvienet.com:8001';

const PAGE_SIZE = 11;

function ListSources() {
    const [privateSources, setPrivateSources] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    const fetchSources = async () => {
        setIsLoading(true);
        setMessage('');

        try {
            const response = await axios.get(`${baseURL}/chatbot1/list-sources/`, {
                headers: {
                    'Content-Type': 'application/json',
                },
                withCredentials: true,
            });

            if (response.status === 200) {
                const { private: privateSources } = response.data.external_sources;
                const filteredPrivate = privateSources.filter(source => source.name.startsWith('oad-')) || [];
                setPrivateSources(filteredPrivate);
                setTotalPages(Math.ceil(filteredPrivate.length / PAGE_SIZE));
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

    useEffect(() => {
        fetchSources();
    }, [page]);

    const formatDate = (dateStr) => {
        if (dateStr === 'N/A') return 'N/A';
        const date = new Date(dateStr);  // Assuming dateStr is in ISO 8601 format
        return date.toLocaleString();  // Convert to local time zone
    };

    const getTableHeaders = () => (
        <tr style={{ backgroundColor: '#f8f9fa' }}>
            <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Name</th>
            <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Description</th>
            <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Model</th>
            <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Created Date</th>
            <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Updated Date</th>
            <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Actions</th>
        </tr>
    );

    const renderSourceRow = (source) => (
        <tr key={source.name} style={{ backgroundColor: '#fff' }}>
            <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>
                <Link to={`/sources/${source.name}/documents`} style={{ color: '#007bff', textDecoration: 'none' }}>
                    {source.name}
                </Link>
            </td>
            <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{source.description || 'null'}</td>
            <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{source.model}</td>
            <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{formatDate(source.created_at)}</td>
            <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{formatDate(source.updated_at)}</td>
            <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>
                <a
                    href={`/chat-with-source/${source.name}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ backgroundColor: '#ff7f0e', color: '#fff', border: 'none', padding: '10px 20px', cursor: 'pointer', display: 'inline-block', textDecoration: 'none' }}
                >
                    Chat with Source
                </a>
            </td>
        </tr>
    );

    const renderSourceTable = (sources) => (
        <div>
            {sources.length > 0 ? (
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px', backgroundColor: '#fff' }}>
                    <thead>{getTableHeaders()}</thead>
                    <tbody>
                        {sources.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE).map(source => renderSourceRow(source))}
                    </tbody>
                </table>
            ) : (
                <p>No sources found.</p>
            )}
        </div>
    );

    const handlePreviousPage = () => {
        if (page > 1) {
            setPage(page - 1);
        }
    };

    const handleNextPage = () => {
        if (page < totalPages) {
            setPage(page + 1);
        }
    };

    return (
        <div style={{ backgroundColor: '#fff', padding: '20px' }}>
            <h1 style={{ color: '#444' }}>Source List</h1>
            {message && <p>{message}</p>}
            {isLoading && <p>Loading...</p>}
            {!isLoading && (
                <>
                    {renderSourceTable(privateSources)}
                    <div>
                        <button onClick={handlePreviousPage} disabled={page === 1}>Previous</button>
                        <button onClick={handleNextPage} disabled={page === totalPages}>Next</button>
                    </div>
                </>
            )}
        </div>
    );
}

export default ListSources;
