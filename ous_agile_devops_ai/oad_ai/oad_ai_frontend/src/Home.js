import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { useAuth } from './AuthContext';
import ListSources from './ListSources';
import Documents from './Documents';
import AutoUploadManager from './AutoUploadManager';
import ChatWithSource from './ChatWithSource';
import CreateSource from './CreateSource';
import Chatbot from './Chatbot'; // Import Chatbot
import FilePreview from './FilePreview';
import WebSocketComponent from './WebSocketComponent';
import ProtectedRoute from './ProtectedRoute';

function Home() {
  const { user } = useAuth();

  return (
    <div style={{
      backgroundColor: '#f4f4f4',
      color: '#333',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      textAlign: 'center'
    }}>
      <h1>Welcome to the Chatbot App</h1>
      <p>Access the following components:</p>
      <ul style={{ listStyleType: 'none', padding: 0 }}>
        <li style={{ margin: '10px 0' }}>
          <Link to="/auto-upload" style={{ color: '#007bff', textDecoration: 'none' }}>Manage Auto-Uploads</Link>
        </li>
        <li style={{ margin: '10px 0' }}>
          <Link to="/sources" style={{ color: '#007bff', textDecoration: 'none' }}>View All Sources</Link>
        </li>
        <li style={{ margin: '10px 0' }}>
          <Link to="/create-source" style={{ color: '#007bff', textDecoration: 'none' }}>Create a New Source</Link>
        </li>
        <li style={{ margin: '10px 0' }}>
          <Link to="/chatbot/public" style={{ color: '#007bff', textDecoration: 'none' }}>Public Chatbot</Link>
        </li>
        <li style={{ margin: '10px 0' }}>
          <Link to="/chatbot/internal" style={{ color: '#007bff', textDecoration: 'none' }}>Internal Chatbot</Link>
        </li>
        {!user && (
          <li style={{ margin: '10px 0' }}>
            <Link to="/login" style={{ color: '#007bff', textDecoration: 'none' }}>Login</Link>
          </li>
        )}
      </ul>

      {user ? (
        <p>Hello, <span role="img" aria-label="Star">🌟</span> Your login was successful! <span role="img" aria-label="Star">🌟</span></p>
      ) : (
        <p>Please <Link to="/login" style={{ color: '#007bff', textDecoration: 'none' }}>login</Link> for full access to app features.</p>
      )}

      <Routes>
        <Route path="/auto-upload" element={<AutoUploadManager />} />
        <Route path="/chat-with-source/:sourceName" element={<ChatWithSource />} />
        <Route path="/media/previews/*" element={<FilePreview />} />
        <Route path="/websocket-test" element={<WebSocketComponent />} />
        <Route path="/chatbot/:mysource" element={<Chatbot />} /> {/* Add route for Chatbot with mysource param */}

        {/* Protected Routes */}
        <Route path="/sources" element={<ProtectedRoute component={ListSources} />} />
        <Route path="/sources/:sourceName/documents" element={<ProtectedRoute component={Documents} />} />
        <Route path="/create-source" element={<ProtectedRoute component={CreateSource} />} />
        <Route path="/sources/:source/upload" element={<ProtectedRoute component={<div />} />} /> {/* Placeholder */}
      </Routes>
    </div>
  );
}

export default Home;
