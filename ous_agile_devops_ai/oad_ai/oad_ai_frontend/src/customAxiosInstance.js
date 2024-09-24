import axios from 'axios';

// Create an Axios instance
const customAxiosInstance = axios.create({
  baseURL: 'http://10.72.19.8:8001',  // Replace with your backend base URL if necessary
  timeout: 1000000,  // Request timeout in milliseconds
  withCredentials: true  // Send credentials such as cookies along with requests
});

// Interceptors to handle common tasks
customAxiosInstance.interceptors.request.use(
  (config) => {
    // Modify request config before sending the request
    console.log('Request sent:', config);  // Logging request config
    return config;
  },
  (error) => {
    // Handle request error
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

customAxiosInstance.interceptors.response.use(
  (response) => {
    // Modify response data before returning it
    console.log('Response received:', response);  // Logging response data
    return response;
  },
  (error) => {
    // Handle response errors
    console.error('Response error:', error);
    return Promise.reject(error);
  }
);

export default customAxiosInstance;
