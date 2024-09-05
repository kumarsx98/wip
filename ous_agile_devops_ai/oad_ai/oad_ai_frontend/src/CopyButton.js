import React, { useState } from 'react';

const CopyButton = ({ text }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000); // Reset after 2 seconds
    });
  };

  return (
    <div>
      <button className="copy-button" onClick={handleCopy}>
        Copy
      </button>
      {copied && <span className="copied-message">Copied to clipboard</span>}
    </div>
  );
};

export default CopyButton;
