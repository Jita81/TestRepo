import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  setQuery,
  clearSearch,
  fetchSuggestions,
  clearSuggestions,
  searchProducts,
} from '../../store/slices/searchSlice';
import './SearchBar.css';

const SearchBar = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { query, suggestions } = useSelector((state) => state.search);
  const [inputValue, setInputValue] = useState(query);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const searchRef = useRef(null);
  const debounceTimeout = useRef(null);

  useEffect(() => {
    setInputValue(query);
  }, [query]);

  useEffect(() => {
    // Click outside to close suggestions
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e) => {
    const value = e.target.value;
    setInputValue(value);

    // Clear previous debounce timeout
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }

    // Fetch suggestions with debounce
    if (value.trim().length >= 2) {
      debounceTimeout.current = setTimeout(() => {
        dispatch(fetchSuggestions(value));
        setShowSuggestions(true);
      }, 300);
    } else {
      dispatch(clearSuggestions());
      setShowSuggestions(false);
    }
  };

  const handleSearch = (searchQuery = inputValue) => {
    if (!searchQuery.trim()) {
      dispatch(clearSearch());
      navigate('/');
      return;
    }

    dispatch(setQuery(searchQuery));
    dispatch(searchProducts({ query: searchQuery }));
    setShowSuggestions(false);
    navigate('/?search=' + encodeURIComponent(searchQuery));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSearch();
  };

  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion);
    handleSearch(suggestion);
  };

  const handleClear = () => {
    setInputValue('');
    dispatch(clearSearch());
    dispatch(clearSuggestions());
    setShowSuggestions(false);
    navigate('/');
  };

  return (
    <div className="search-bar" ref={searchRef}>
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-wrapper">
          <input
            type="text"
            className="search-input"
            placeholder="Search for products..."
            value={inputValue}
            onChange={handleInputChange}
            onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
          />
          {inputValue && (
            <button
              type="button"
              className="search-clear"
              onClick={handleClear}
              aria-label="Clear search"
            >
              ✕
            </button>
          )}
        </div>
        <button type="submit" className="search-button">
          🔍 Search
        </button>
      </form>

      {showSuggestions && suggestions.length > 0 && (
        <div className="search-suggestions">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              className="suggestion-item"
              onClick={() => handleSuggestionClick(suggestion)}
            >
              🔍 {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchBar;