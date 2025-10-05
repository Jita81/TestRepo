import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  setCategory,
  setPriceRange,
  setSort,
  setInStock,
  clearFilters,
} from '../../store/slices/filtersSlice';
import './FilterPanel.css';

const FilterPanel = ({ categories, onApplyFilters }) => {
  const dispatch = useDispatch();
  const filters = useSelector((state) => state.filters);
  const [localMinPrice, setLocalMinPrice] = useState(filters.minPrice || '');
  const [localMaxPrice, setLocalMaxPrice] = useState(filters.maxPrice || '');

  const sortOptions = [
    { value: 'newest', label: 'Newest First' },
    { value: 'price_asc', label: 'Price: Low to High' },
    { value: 'price_desc', label: 'Price: High to Low' },
    { value: 'name_asc', label: 'Name: A to Z' },
    { value: 'name_desc', label: 'Name: Z to A' },
    { value: 'popularity', label: 'Most Popular' },
  ];

  const handleCategoryChange = (category) => {
    dispatch(setCategory(category));
    onApplyFilters();
  };

  const handleSortChange = (e) => {
    dispatch(setSort(e.target.value));
    onApplyFilters();
  };

  const handleInStockChange = (e) => {
    dispatch(setInStock(e.target.checked));
    onApplyFilters();
  };

  const handlePriceFilter = () => {
    const min = localMinPrice ? parseFloat(localMinPrice) : null;
    const max = localMaxPrice ? parseFloat(localMaxPrice) : null;
    dispatch(setPriceRange([min, max]));
    onApplyFilters();
  };

  const handleClearFilters = () => {
    dispatch(clearFilters());
    setLocalMinPrice('');
    setLocalMaxPrice('');
    onApplyFilters();
  };

  const hasActiveFilters = filters.category || filters.minPrice || filters.maxPrice || filters.inStock;

  return (
    <div className="filter-panel">
      <div className="filter-header">
        <h3>Filters</h3>
        {hasActiveFilters && (
          <button className="clear-filters-btn" onClick={handleClearFilters}>
            Clear All
          </button>
        )}
      </div>

      {/* Sort */}
      <div className="filter-section">
        <label className="filter-label">Sort By</label>
        <select
          className="filter-select"
          value={filters.sort}
          onChange={handleSortChange}
        >
          {sortOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Categories */}
      {categories && categories.length > 0 && (
        <div className="filter-section">
          <label className="filter-label">Category</label>
          <div className="filter-options">
            <button
              className={`filter-option ${!filters.category ? 'active' : ''}`}
              onClick={() => handleCategoryChange('')}
            >
              All Categories
            </button>
            {categories.map((category) => (
              <button
                key={category.id || category.name}
                className={`filter-option ${filters.category === category.name ? 'active' : ''}`}
                onClick={() => handleCategoryChange(category.name)}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Price Range */}
      <div className="filter-section">
        <label className="filter-label">Price Range</label>
        <div className="price-inputs">
          <input
            type="number"
            className="price-input"
            placeholder="Min"
            value={localMinPrice}
            onChange={(e) => setLocalMinPrice(e.target.value)}
            min="0"
          />
          <span>-</span>
          <input
            type="number"
            className="price-input"
            placeholder="Max"
            value={localMaxPrice}
            onChange={(e) => setLocalMaxPrice(e.target.value)}
            min="0"
          />
        </div>
        <button className="apply-price-btn" onClick={handlePriceFilter}>
          Apply
        </button>
      </div>

      {/* Availability */}
      <div className="filter-section">
        <label className="filter-checkbox">
          <input
            type="checkbox"
            checked={filters.inStock}
            onChange={handleInStockChange}
          />
          <span>In Stock Only</span>
        </label>
      </div>
    </div>
  );
};

export default FilterPanel;