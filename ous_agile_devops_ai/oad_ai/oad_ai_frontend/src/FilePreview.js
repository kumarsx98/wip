

import React, { useEffect } from 'react';

const FilePreview = () => {
  const { pathname } = window.location;
  const fileUrl = `http://localhost:8001${pathname}`; // Direct link to Django backend

  useEffect(() => {
    console.log(`Loading file from: ${fileUrl}`);
  }, [fileUrl]);

  return (
    <div>
      <h2>File Preview</h2>
      <iframe src={fileUrl} title="File Preview" width="100%" height="800px" style={{ border: 'none' }} />
    </div>
  );
};

export default FilePreview;
