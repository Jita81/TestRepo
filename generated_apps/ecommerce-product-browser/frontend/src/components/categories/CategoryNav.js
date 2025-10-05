import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchCategoryTree } from '../../store/slices/categoriesSlice';
import { setCategory } from '../../store/slices/filtersSlice';
import './CategoryNav.css';

const CategoryNav = ({ onCategorySelect }) => {
  const dispatch = useDispatch();
  const { tree, loading } = useSelector((state) => state.categories);
  const selectedCategory = useSelector((state) => state.filters.category);

  useEffect(() => {
    dispatch(fetchCategoryTree());
  }, [dispatch]);

  const handleCategoryClick = (categoryName) => {
    dispatch(setCategory(categoryName));
    if (onCategorySelect) {
      onCategorySelect(categoryName);
    }
  };

  const renderCategoryTree = (categories, level = 0) => {
    return (
      <ul className={`category-list level-${level}`}>
        {categories.map((category) => (
          <li key={category.id} className="category-item">
            <button
              className={`category-button ${
                selectedCategory === category.name ? 'active' : ''
              }`}
              onClick={() => handleCategoryClick(category.name)}
            >
              {category.name}
            </button>
            {category.children && category.children.length > 0 && (
              <div className="category-children">
                {renderCategoryTree(category.children, level + 1)}
              </div>
            )}
          </li>
        ))}
      </ul>
    );
  };

  if (loading) {
    return (
      <div className="category-nav">
        <div className="category-skeleton">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton-category skeleton" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="category-nav">
      <h3 className="category-nav-title">Categories</h3>
      <button
        className={`category-button all-categories ${
          !selectedCategory ? 'active' : ''
        }`}
        onClick={() => handleCategoryClick('')}
      >
        All Products
      </button>
      {tree && tree.length > 0 && renderCategoryTree(tree)}
    </div>
  );
};

export default CategoryNav;