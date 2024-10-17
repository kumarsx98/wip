import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './Home';
import Login from './Login';
import ChatWithSource from './ChatWithSource';
import CreateSource from './CreateSource';
import ListSources from './ListSources';
import Documents from './Documents';
import Navigation from './Navigation';
import AutoUploadManager from './AutoUploadManager';
import Chatbot from './Chatbot'; // Import Chatbot component
import { AuthProvider } from './AuthContext';
import FilePreview from './FilePreview';
import WebSocketComponent from './WebSocketComponent';
import ProtectedRoute from './ProtectedRoute';
import axios from 'axios';

axios.defaults.withCredentials = true;

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Navigation />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/auto-upload" element={<AutoUploadManager />} />
          <Route path="/chat-with-source/:sourceName" element={<ChatWithSource />} />
          <Route path="/media/previews/*" element={<FilePreview />} />
          <Route path="/websocket-test" element={<WebSocketComponent />} />
          <Route path="/chatbot/:mysource" element={<Chatbot />} /> {/* Updated route for Chatbot with mysource param */}

          {/* Protected Routes */}
          <Route path="/sources" element={<ProtectedRoute component={ListSources} />} />
          <Route path="/sources/:sourceName/documents" element={<ProtectedRoute component={Documents} />} />
          <Route path="/create-source" element={<ProtectedRoute component={CreateSource} />} />
          <Route path="/sources/:source/upload" element={<ProtectedRoute component={<div />} />} /> {/* Placeholder */}
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
