import React, { useEffect, useState } from 'react';

const FilePreview = () => {
  const { pathname } = window.location;
  const [fileUrl, setFileUrl] = useState('');

  useEffect(() => {
    const currentUrl = window.location.origin; // Get the current server address
    const fileUrl = `${currentUrl}${pathname}`;
    setFileUrl(fileUrl);
    console.log(`Loading file from: ${fileUrl}`);
  }, [pathname]);

  return (
    <div>
      <h2>File Preview</h2>
      {fileUrl ? (
        <iframe src={fileUrl} title="File Preview" width="100%" height="800px" style={{ border: 'none' }} />
      ) : (
        <p>Loading file preview...</p>
      )}
    </div>
  );
};

export default FilePreview;
