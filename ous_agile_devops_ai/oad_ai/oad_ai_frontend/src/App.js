import React from 'react';
import { BrowserRouter as Router, Route, Routes, useLocation } from 'react-router-dom';
import Home from './Home';
import Login from './Login';
import ChatWithSource from './ChatWithSource';
import CreateSource from './CreateSource';
import ListSources from './ListSources';
import Documents from './Documents';
import DeleteSource from './DeleteSource'; // Import DeleteSource component
import Navigation from './Navigation';
import AutoUploadManager from './AutoUploadManager';
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
        <MainLayout />
      </Router>
    </AuthProvider>
  );
};

const MainLayout = () => {
  const location = useLocation();
  const isChatWithSource = location.pathname.startsWith('/chat-with-source');

  return (
    <div>
      {!isChatWithSource && <Navigation />}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/sources" element={<ListSources />} /> {/* Accessible without authentication */}
        <Route path="/chat-with-source/:sourceName" element={<ChatWithSource />} /> {/* Accessible without authentication */}
        <Route path="/media/previews/*" element={<FilePreview />} /> {/* Accessible without authentication */}

        {/* Protected Routes */}
        <Route path="/create-source" element={<ProtectedRoute component={CreateSource} />} />
        <Route path="/auto-upload" element={<ProtectedRoute component={AutoUploadManager} />} />
        <Route path="/websocket-test" element={<ProtectedRoute component={WebSocketComponent} />} />
        <Route path="/sources/:sourceName/documents" element={<ProtectedRoute component={Documents} />} />
        <Route path="/sources/:source/upload" element={<ProtectedRoute component={<div />} />} /> {/* Placeholder */}
        <Route path="/delete-source" element={<ProtectedRoute component={DeleteSource} />} /> {/* Protected Delete Source */}
      </Routes>
    </div>
  );
};

export default App;
