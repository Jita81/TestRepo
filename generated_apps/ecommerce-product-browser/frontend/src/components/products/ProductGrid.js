import React, { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import ProductCard from './ProductCard';
import ProductQuickView from './ProductQuickView';
import { fetchProducts, incrementPage } from '../../store/slices/productsSlice';
import './ProductGrid.css';

const ProductGrid = () => {
  const dispatch = useDispatch();
  const { items, loading, error, hasMore, pagination } = useSelector((state) => state.products);
  const { isSearchMode, results } = useSelector((state) => state.search);
  const filters = useSelector((state) => state.filters);
  
  const [selectedProduct, setSelectedProduct] = useState(null);
  const loaderRef = useRef(null);

  const displayProducts = isSearchMode ? results : items;

  // Intersection Observer for infinite scroll
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const target = entries[0];
        if (target.isIntersecting && hasMore && !loading && !isSearchMode) {
          dispatch(incrementPage());
          dispatch(fetchProducts({ ...filters, page: pagination.page + 1 }));
        }
      },
      {
        root: null,
        rootMargin: '100px',
        threshold: 0.1,
      }
    );

    if (loaderRef.current) {
      observer.observe(loaderRef.current);
    }

    return () => {
      if (loaderRef.current) {
        observer.unobserve(loaderRef.current);
      }
    };
  }, [dispatch, hasMore, loading, filters, pagination.page, isSearchMode]);

  const handleQuickView = (product) => {
    setSelectedProduct(product);
  };

  const handleCloseQuickView = () => {
    setSelectedProduct(null);
  };

  if (error) {
    return (
      <div className="grid-error">
        <p>Error: {error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  if (!loading && displayProducts.length === 0) {
    return (
      <div className="grid-empty">
        <h3>No products found</h3>
        <p>Try adjusting your filters or search terms</p>
      </div>
    );
  }

  return (
    <>
      <div className="product-grid">
        {displayProducts.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            onQuickView={handleQuickView}
          />
        ))}
        
        {loading && pagination.page === 1 && (
          <>
            {[...Array(8)].map((_, index) => (
              <div key={`skeleton-${index}`} className="product-card-skeleton">
                <div className="skeleton-image skeleton" />
                <div className="skeleton-content">
                  <div className="skeleton-line skeleton" style={{ width: '40%' }} />
                  <div className="skeleton-line skeleton" style={{ width: '90%' }} />
                  <div className="skeleton-line skeleton" style={{ width: '75%' }} />
                  <div className="skeleton-footer">
                    <div className="skeleton-line skeleton" style={{ width: '30%' }} />
                    <div className="skeleton-line skeleton" style={{ width: '40%' }} />
                  </div>
                </div>
              </div>
            ))}
          </>
        )}
      </div>

      {/* Infinite scroll loader */}
      <div ref={loaderRef} className="scroll-loader">
        {loading && pagination.page > 1 && <div className="loader-spinner">Loading more...</div>}
      </div>

      {/* Quick view modal */}
      {selectedProduct && (
        <ProductQuickView
          product={selectedProduct}
          onClose={handleCloseQuickView}
        />
      )}
    </>
  );
};

export default ProductGrid;