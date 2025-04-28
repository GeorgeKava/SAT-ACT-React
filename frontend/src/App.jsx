import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import MathPage from './components/MathPage';
import ChemistryPage from './components/ChemistryPage';
import PhysicsPage from './components/PhysicsPage';
import SATPage from './components/SATPage';
import ACTPage from './components/ACTPage';
import NavBar from './components/NavBar';

function App() {
  return (
    <Router>
      <div>
        <NavBar />
        <Routes>
          <Route path="/" element={<Navigate to="/SAT" />} />
          {/* <Route path="/" element={<MathPage />} /> */}
          {/* <Route path="/chemistry" element={<ChemistryPage />} /> */}
          {/* <Route path="/physics" element={<PhysicsPage />} /> */}
          <Route path="/SAT" element={<SATPage />} />
          <Route path="/ACT" element={<ACTPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;