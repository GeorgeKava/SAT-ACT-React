import React, { useState } from 'react';
import axios from 'axios';

function QAPage() {
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const captureProblem = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/qa?type=capture');
      console.log(response.data);
      setResult(response.data.result);
    } catch (error) {
      console.error('Error capturing problem:', error);
      setResult('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Question & Answer Assistant</h1>
      <div>
        <h2>Live Video Feed</h2>
        <img src="http://127.0.0.1:5000/api/video_feed" alt="Live Video Feed" />
        <button onClick={captureProblem} disabled={loading}>
          {loading ? 'Processing...' : 'Capture Question'}
        </button>
      </div>
      {result && (
        <div>
          <h2>Extracted Information</h2>
          <p>{result}</p>
        </div>
      )}
    </div>
  );
}

export default QAPage;