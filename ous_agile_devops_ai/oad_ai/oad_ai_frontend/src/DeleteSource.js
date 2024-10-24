import React, { useState } from 'react';
import axios from 'axios';

//const backendURL = 'http://localhost:8001'; // Your backend URL
const backendURL = 'http://oad-ai.abbvienet.com:8001';

function DeleteSource() {
  const [sourceName, setSourceName] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleDelete = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      // Proceed to call the backend delete endpoint
      const response = await axios.delete(`${backendURL}/delete-source/${sourceName}/`, {
        headers: {
          'Content-Type': 'application/json',
        },
        withCredentials: true,
      });

      if (response.status === 204) {
        setMessage('Source successfully deleted!');
        setSourceName('');
      } else {
        setMessage('An error occurred while deleting the source.');
      }
    } catch (error) {
      if (error.response && error.response.status === 401) {
        setMessage('Unauthorized: Please check your credentials.');
      } else if (error.response && error.response.status === 404) {
        setMessage('Source not found.');
      } else {
        console.error('Error during source deletion:', error);
        setMessage(error.response?.data?.error || 'An error occurred while deleting the source.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', backgroundColor: 'white', maxWidth: '500px', margin: '0 auto' }}>
      <h1 style={{ textAlign: 'center', color: '#333' }}>Delete a Source</h1>
      <form onSubmit={handleDelete} style={{ display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="sourceName" style={{ marginBottom: '5px', display: 'block' }}>Source Name:</label>
          <input
            id="sourceName"
            type="text"
            value={sourceName}
            onChange={(e) => setSourceName(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          style={{
            padding: '10px',
            backgroundColor: '#d9534f',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.7 : 1,
          }}
        >
          {isLoading ? 'Deleting...' : 'Delete Source'}
        </button>
      </form>
      {message && <p style={{ marginTop: '15px', textAlign: 'center', color: message.includes('error') || message.includes('not found') ? 'red' : 'green' }}>{message}</p>}
    </div>
  );
}

export default DeleteSource;
