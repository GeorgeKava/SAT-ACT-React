import React from 'react';
import { Link } from 'react-router-dom';
import './NavBar.css'; // Optional: Add styles for the NavBar

function NavBar() {
  return (
    <nav>
      {/* <Link to="/">Math</Link> */}
      {/* <Link to="/chemistry">Chemistry</Link> */}
      {/* <Link to="/physics">Physics</Link> */}
      <Link to="/SAT">SAT</Link>
      <Link to="/ACT">ACT</Link>
    </nav>
  );
}

export default NavBar;