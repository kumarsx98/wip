import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './Home';
import Chatbot from './Chatbot';
import CreateSource from './CreateSource';
import SourceList from './ListSources';
import Login from './Login';
import Navigation from './Navigation';
import './App.css';
import AutoUploadManager from './AutoUploadManager';
import { AuthProvider } from './AuthContext';
import ProtectedRoute from './ProtectedRoute';
import axios from 'axios';

axios.defaults.withCredentials = true;

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navigation />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/sources" element={<SourceList />} />
          <Route path="/auto-upload" element={<AutoUploadManager />} />
          <Route
            path="/:mysource"
            element={
              <ProtectedRoute>
                <Chatbot />
              </ProtectedRoute>
            }
          />
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
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;