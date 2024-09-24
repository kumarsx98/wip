import React from 'react';
import axios from './customAxiosInstance';  // Import the customAxiosInstance
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './Home';
import ChatWithSource from './ChatWithSource';
import CreateSource from './CreateSource';
import ListSources from './ListSources';
import Documents from './Documents'; // Import the new Documents component
import Login from './Login';
import Navigation from './Navigation';
import AutoUploadManager from './AutoUploadManager';
import { AuthProvider } from './AuthContext';
import ProtectedRoute from './ProtectedRoute';
import FilePreview from './FilePreview';

// Set default axios configuration
axios.defaults.withCredentials = true;

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navigation />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/sources" element={<ListSources />} />
          <Route path="/sources/:sourceName/documents" element={<Documents />} /> {/* Update the route to use Documents */}
          <Route path="/auto-upload" element={<AutoUploadManager />} />
          <Route
            path="/create-source"
            element={
              <ProtectedRoute>
                <CreateSource />
              </ProtectedRoute>
            }
          />
          <Route
            path="/sources/:source/upload"
            element={
              <ProtectedRoute>
                {/* <UploadDocument /> */}
              </ProtectedRoute>
            }
          />
          <Route path="/chat-with-source/:sourceName" element={<ChatWithSource />} />
          <Route path="/media/previews/*" element={<FilePreview />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
