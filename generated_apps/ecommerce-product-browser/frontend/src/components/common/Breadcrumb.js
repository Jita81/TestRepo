import React from 'react';
import { Link } from 'react-router-dom';
import './Breadcrumb.css';

const Breadcrumb = ({ items }) => {
  if (!items || items.length === 0) {
    return null;
  }

  return (
    <nav className="breadcrumb" aria-label="Breadcrumb">
      <ol className="breadcrumb-list">
        <li className="breadcrumb-item">
          <Link to="/" className="breadcrumb-link">
            Home
          </Link>
        </li>
        {items.map((item, index) => (
          <li key={item.id || index} className="breadcrumb-item">
            <span className="breadcrumb-separator">›</span>
            {index === items.length - 1 ? (
              <span className="breadcrumb-current">{item.name}</span>
            ) : (
              <Link
                to={item.slug ? `/category/${item.slug}` : '#'}
                className="breadcrumb-link"
              >
                {item.name}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

export default Breadcrumb;