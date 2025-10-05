import React from 'react';
import { Link } from 'react-router-dom';
import SearchBar from '../search/SearchBar';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <Link to="/" className="logo">
            <h1>E-Shop</h1>
          </Link>
          <div className="header-search">
            <SearchBar />
          </div>
          <nav className="header-nav">
            <Link to="/cart" className="nav-link">
              Cart
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;