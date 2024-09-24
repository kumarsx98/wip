const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/chatbot1',
    createProxyMiddleware({
      target: 'http://localhost:8001',
      changeOrigin: true,
      pathRewrite: {
        '^/chatbot1': '', // Remove leading '/chatbot1' from the path
      },
      timeout: 600000, // Timeout for connecting to the upstream server (default: 2 minutes)
      proxyTimeout: 600000, // Timeout for receiving a response from the upstream server (default: 2 minutes)
      onProxyReq: (proxyReq, req, res) => {
        // Set custom headers here if needed
      },
      onError: (err, req, res) => {
        res.writeHead(500, {
          'Content-Type': 'text/plain'
        });
        res.end('Something went wrong. And we are reporting a custom error message.');
      }
    })
  );
};
