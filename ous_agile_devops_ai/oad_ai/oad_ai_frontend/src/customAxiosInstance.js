import axios from './customAxiosInstance';  // Ensure axios instance is used

const AutoUploadManager = () => {

  // Add console.log to verify the useEffect and request triggering
  useEffect(() => {
    console.log("AutoUploadManager component is mounted");
    axios.defaults.withCredentials = true;

    const fetchData = async () => {
      console.log("Fetching upload status");  // Log for debugging
      await fetchUploadStatus();
    };

    fetchData();
    const intervalId = setInterval(fetchData, 60000); // Refresh every 1 minute

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  // Log error details for better debugging
  const fetchUploadStatus = async () => {
    try {
      const response = await axios.get('/chatbot1/get-upload-status/', {
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
        },
      });
      console.log("Fetched upload status:", response.data);  // Log response for debugging
      // rest of the code...
    } catch (error) {
      console.error('Error during fetchUploadStatus:', error);  // Log the error
      setMessage(`Error fetching upload status: ${error.message || 'Network Error'}`);  // Log detailed message
    }
  };

  // Other code remains the same...
};
