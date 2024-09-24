// src/customAxiosInstance.js

import axios from 'axios';

// Function to get CSRF token from cookies
const getCsrfToken = () => {
  let csrfToken = null;
  const matches = document.cookie.match(new RegExp(
    '(?:^|; )' + 'csrftoken'.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + '=([^;]*)'
  ));
  csrfToken = matches ? decodeURIComponent(matches[1]) : undefined;
  return csrfToken;
};

// Axios instance
const axiosInstance = axios.create({
  baseURL: 'http://10.72.19.8:8001',  // Point to the backend server
  withCredentials: true,  // Include cookies in the requests
});

// Add a request interceptor to include CSRF token in all requests
axiosInstance.interceptors.request.use(config => {
  const csrfToken = getCsrfToken();
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default axiosInstance;
