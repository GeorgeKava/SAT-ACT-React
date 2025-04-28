import React, { useState } from 'react';
import axios from 'axios';

function SATPage() {
  const [problem, setProblem] = useState('');
  const [result, setResult] = useState('');
  const [showVideoFeed, setShowVideoFeed] = useState(false); // State to toggle video feed visibility

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/SAT?type=text', { sat_problem: problem });
      setResult(response.data.result);
    } catch (error) {
      console.error('Error submitting problem:', error);
    }
  };

  const captureProblem = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/SAT?type=capture');
      setResult(response.data.result);
    } catch (error) {
      console.error('Error capturing problem:', error);
    }
  };

  return (
    <div>
      <h1>SAT Assistant</h1>
      <form onSubmit={handleSubmit}>
        <label>Type your SAT problem:</label>
        <input
          type="text"
          value={problem}
          onChange={(e) => setProblem(e.target.value)}
          placeholder="e.g., Any Math, Reading, English, or Science problem."
        />
        <button type="submit">Submit</button>
      </form>
      <div>
        <button onClick={() => setShowVideoFeed(!showVideoFeed)}>
          {showVideoFeed ? 'Hide Video Feed' : 'Show Video Feed'}
        </button>
        {showVideoFeed && (
          <div>
            <h2>Live Video Feed</h2>
            <img src="http://127.0.0.1:5000/api/video_feed" alt="Live Video Feed" />
            <button onClick={captureProblem}>Capture Problem</button>
          </div>
        )}
      </div>
      {result && (
        <div>
          <h2>Solution</h2>
          <p>{result}</p>
        </div>
      )}
    </div>
  );
}

export default SATPage;