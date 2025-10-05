import React from 'react';
import { Link } from 'react-router-dom';
import SearchBar from '../search/SearchBar';
import CartIcon from '../cart/CartIcon';
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
            <CartIcon />
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;