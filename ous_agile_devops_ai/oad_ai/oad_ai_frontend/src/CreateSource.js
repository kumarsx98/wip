import React, { useState } from 'react';
import axios from 'axios';

//const baseURL = 'http://localhost:8001'; // Define your backend base URL here
const baseURL = 'http://oad-ai.abbvienet.com:8001';

function CreateSource() {
  const [sourceName, setSourceName] = useState('');
  const [description, setDescription] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      const response = await axios.post(`${baseURL}/chatbot1/create-source/`,
        {
          source: sourceName,
          description: description
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          withCredentials: true
        }
      );

      if (response.status === 201) {
        setMessage('Source successfully created!');
        setSourceName('');
        setDescription('');
      } else {
        setMessage('An error occurred while creating the source.');
      }
    } catch (error) {
      if (error.response && error.response.status === 409) {
        setMessage('Source already exists.');
      } else {
        console.error('Error during source creation:', error);
        setMessage(error.response?.data?.error || 'An error occurred while creating the source.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Function to get CSRF token from cookies
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; cookies[i]; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  return (
    <div style={{ padding: '20px', backgroundColor: 'white', maxWidth: '500px', margin: '0 auto' }}>
      <h1 style={{ textAlign: 'center', color: '#333' }}>Create a New Source</h1>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column' }}>
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
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="description" style={{ marginBottom: '5px', display: 'block' }}>Description:</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc', minHeight: '100px' }}
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          style={{
            padding: '10px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.7 : 1
          }}
        >
          {isLoading ? 'Creating...' : 'Create Source'}
        </button>
      </form>
      {message && <p style={{ marginTop: '15px', textAlign: 'center', color: message.includes('error') || message.includes('exists') ? 'red' : 'green' }}>{message}</p>}
    </div>
  );
}

export default CreateSource;
