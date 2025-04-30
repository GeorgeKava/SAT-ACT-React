import React from 'react';
import { Link } from 'react-router-dom';
import './NavBar.css'; // Optional: Add styles for the NavBar

function NavBar() {
  return (
    <nav>
      <Link to="/SAT">SAT</Link>
      <Link to="/ACT">ACT</Link>
      <Link to="/qa">Q&A</Link>
    </nav>
  );
}

export default NavBar;