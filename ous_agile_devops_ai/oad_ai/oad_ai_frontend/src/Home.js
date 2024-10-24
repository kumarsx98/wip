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
import Login from './Login'; // Import the Login component

function Home() {
  const { user } = useAuth();

  return (
    <div style={{
      backgroundColor: '#f4f4f4',
      color: '#333',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'flex-start', // Adjust to move the content up
      alignItems: 'center',
      textAlign: 'center',
      paddingTop: '20px' // Add padding to move content up
    }}>
      <h1>Welcome to the Chatbot App</h1>
      <p>Access the following components:</p>
      <ul style={{ listStyleType: 'none', padding: 0, margin: '10px 0' }}> {/* Reduce margin */}
        <li style={{ margin: '5px 0' }}>  {/* Reduce margin */}
          <Link to="/sources" style={{ color: '#007bff', textDecoration: 'none' }}>View All Sources</Link>
        </li>
        {/* Conditionally render these links based on user authentication */}
        {user && (
          <>
            <li style={{ margin: '5px 0' }}> {/* Reduce margin */}
              <Link to="/create-source" style={{ color: '#007bff', textDecoration: 'none' }}>Create a New Source</Link>
            </li>
            <li style={{ margin: '5px 0' }}> {/* Reduce margin */}
              <Link to="/auto-upload" style={{ color: '#007bff', textDecoration: 'none' }}>Manage Auto-Uploads</Link>
            </li>
          </>
        )}
        {!user && (
          <li style={{ margin: '5px 0' }}> {/* Reduce margin */}
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
        <Route path="/auto-upload" element={<ProtectedRoute component={AutoUploadManager} />} />
        <Route path="/chat-with-source/:sourceName" element={<ProtectedRoute component={ChatWithSource} />} />
        <Route path="/media/previews/*" element={<ProtectedRoute component={FilePreview} />} />
        <Route path="/websocket-test" element={<ProtectedRoute component={WebSocketComponent} />} />
        <Route path="/chatbot/:mysource" element={<ProtectedRoute component={Chatbot} />} /> {/* Add route for Chatbot with mysource param */}

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
