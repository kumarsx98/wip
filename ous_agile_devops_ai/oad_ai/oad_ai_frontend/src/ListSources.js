import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const PAGE_SIZE = 10; // Number of sources per page

function ListSources() {
  const [globalSources, setGlobalSources] = useState([]);
  const [privateSources, setPrivateSources] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [page, setPage] = useState(1); // Current page number
  const [totalPages, setTotalPages] = useState(1); // Total number of pages

  const fetchSources = async () => {
    setIsLoading(true);
    setMessage('');

    try {
      const response = await axios.get('/chatbot1/list-sources/', {
        headers: {
          'Content-Type': 'application/json',
        },
        withCredentials: true,
      });

      if (response.status === 200) {
        const { global, private: privateSources } = response.data.external_sources;
        const filteredGlobal = global.filter(source => source.name.startsWith('oad-')) || [];
        const filteredPrivate = privateSources.filter(source => source.name.startsWith('oad-')) || [];
        setGlobalSources(filteredGlobal);
        setPrivateSources(filteredPrivate);

        // Calculate total pages for pagination
        setTotalPages(Math.ceil(filteredGlobal.length / PAGE_SIZE));
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

  const getTableHeaders = () => (
    <tr style={{ backgroundColor: '#f8f9fa' }}>
      <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Name</th>
      <th style={{ border: '1px solid #dee2e6', padding: '12px', textAlign: 'left' }}>Visibility</th>
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
      <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{source.visibility}</td>
      <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{source.model}</td>
      <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{source.created_at}</td>
      <td style={{ border: '1px solid #dee2e6', padding: '12px' }}>{source.updated_at}</td>
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

  const renderSourceTable = (sources, title) => (
    <div>
      <h2 style={{ color: '#444', marginTop: '20px' }}>{title}</h2>
      {sources.length > 0 ? (
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px', backgroundColor: '#fff' }}>
          <thead>{getTableHeaders()}</thead>
          <tbody>
            {sources.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE).map(source => renderSourceRow(source))}
          </tbody>
        </table>
      ) : (
        <p>No {title.toLowerCase()} found.</p>
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
          {renderSourceTable(globalSources, 'Global Sources')}
          {renderSourceTable(privateSources, 'Private Sources')}
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
