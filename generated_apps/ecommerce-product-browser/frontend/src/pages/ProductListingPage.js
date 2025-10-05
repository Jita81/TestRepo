import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useSearchParams, useParams } from 'react-router-dom';
import ProductGrid from '../components/products/ProductGrid';
import FilterPanel from '../components/filters/FilterPanel';
import CategoryNav from '../components/categories/CategoryNav';
import Breadcrumb from '../components/common/Breadcrumb';
import {
  fetchProducts,
  clearProducts,
} from '../store/slices/productsSlice';
import {
  searchProducts,
  setQuery,
  clearSearch,
} from '../store/slices/searchSlice';
import { fetchCategories } from '../store/slices/categoriesSlice';
import { setCategory } from '../store/slices/filtersSlice';
import './ProductListingPage.css';

const ProductListingPage = () => {
  const dispatch = useDispatch();
  const [searchParams] = useSearchParams();
  const { category: categoryParam } = useParams();
  
  const filters = useSelector((state) => state.filters);
  const { list: categories } = useSelector((state) => state.categories);
  const { query, isSearchMode } = useSelector((state) => state.search);
  const { pagination } = useSelector((state) => state.products);

  useEffect(() => {
    // Fetch categories on mount
    dispatch(fetchCategories());
  }, [dispatch]);

  useEffect(() => {
    // Handle URL search param
    const searchQuery = searchParams.get('search');
    if (searchQuery && searchQuery !== query) {
      dispatch(setQuery(searchQuery));
      dispatch(searchProducts({ query: searchQuery }));
    } else if (!searchQuery && isSearchMode) {
      dispatch(clearSearch());
      dispatch(clearProducts());
      loadProducts();
    }
  }, [searchParams]);

  useEffect(() => {
    // Handle category from URL
    if (categoryParam && categoryParam !== filters.category) {
      dispatch(setCategory(categoryParam));
    }
  }, [categoryParam]);

  useEffect(() => {
    // Load products when filters change
    if (!isSearchMode) {
      loadProducts();
    }
  }, [filters, isSearchMode]);

  const loadProducts = () => {
    dispatch(clearProducts());
    dispatch(fetchProducts({ ...filters, page: 1 }));
  };

  const handleApplyFilters = () => {
    loadProducts();
  };

  const handleCategorySelect = () => {
    loadProducts();
  };

  // Build breadcrumb
  const breadcrumbItems = [];
  if (filters.category) {
    breadcrumbItems.push({ name: filters.category });
  }

  return (
    <div className="product-listing-page">
      <div className="container">
        <Breadcrumb items={breadcrumbItems} />
        
        <div className="page-header">
          <div>
            <h1 className="page-title">
              {isSearchMode
                ? `Search Results for "${query}"`
                : filters.category
                ? filters.category
                : 'All Products'}
            </h1>
            <p className="page-subtitle">
              {isSearchMode
                ? `Found ${pagination.total} products`
                : `Showing ${pagination.total} products`}
            </p>
          </div>
        </div>

        <div className="page-content">
          <aside className="sidebar">
            <CategoryNav onCategorySelect={handleCategorySelect} />
            {!isSearchMode && (
              <FilterPanel
                categories={categories}
                onApplyFilters={handleApplyFilters}
              />
            )}
          </aside>

          <main className="main-content">
            <ProductGrid />
          </main>
        </div>
      </div>
    </div>
  );
};

export default ProductListingPage;