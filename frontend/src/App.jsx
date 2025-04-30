import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';

import SATPage from './components/SATPage';
import ACTPage from './components/ACTPage';
import NavBar from './components/NavBar';
import QAPage from './components/QAPage';

function App() {
  return (
    <Router>
      <div>
        <NavBar />
        <Routes>
          <Route path="/" element={<Navigate to="/SAT" />} />
          <Route path="/SAT" element={<SATPage />} />
          <Route path="/ACT" element={<ACTPage />} />
          <Route path="/qa" element={<QAPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;