import React, { useState, useEffect, useRef } from 'react';
import './ProductCard.css';

const ProductCard = ({ product, onQuickView }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const cardRef = useRef(null);

  const {
    id,
    name,
    description,
    price,
    category,
    images,
    inventory,
  } = product;

  const thumbnailUrl = images?.thumbnail || 'https://via.placeholder.com/300x300?text=No+Image';

  // Intersection Observer for lazy loading
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true);
            observer.unobserve(entry.target);
          }
        });
      },
      {
        rootMargin: '50px',
      }
    );

    if (cardRef.current) {
      observer.observe(cardRef.current);
    }

    return () => {
      if (cardRef.current) {
        observer.unobserve(cardRef.current);
      }
    };
  }, []);

  const getStockBadge = () => {
    const status = inventory?.status;
    if (status === 'OUT_OF_STOCK') {
      return <span className="stock-badge out-of-stock">Out of Stock</span>;
    }
    if (status === 'LOW_STOCK') {
      return <span className="stock-badge low-stock">Low Stock</span>;
    }
    return <span className="stock-badge in-stock">In Stock</span>;
  };

  const handleImageLoad = () => {
    setImageLoaded(true);
  };

  const highlightSearchTerm = (text, highlights) => {
    if (!highlights) return text;
    return <span dangerouslySetInnerHTML={{ __html: highlights[0] }} />;
  };

  return (
    <div className="product-card" ref={cardRef}>
      <div className="product-image-container">
        {!imageLoaded && <div className="image-skeleton skeleton" />}
        {isVisible && (
          <img
            src={thumbnailUrl}
            alt={name}
            className={`product-image ${imageLoaded ? 'loaded' : 'loading'}`}
            onLoad={handleImageLoad}
            loading="lazy"
          />
        )}
        <div className="product-overlay">
          <button
            className="quick-view-btn"
            onClick={() => onQuickView && onQuickView(product)}
          >
            Quick View
          </button>
        </div>
        {getStockBadge()}
      </div>

      <div className="product-info">
        <span className="product-category">{category}</span>
        <h3 className="product-name" title={name}>
          {product._highlights?.name
            ? highlightSearchTerm(name, product._highlights.name)
            : name}
        </h3>
        <p className="product-description">
          {product._highlights?.description
            ? highlightSearchTerm(description, product._highlights.description)
            : description?.substring(0, 80) + (description?.length > 80 ? '...' : '')}
        </p>
        <div className="product-footer">
          <span className="product-price">${parseFloat(price).toFixed(2)}</span>
          <button
            className="add-to-cart-btn"
            disabled={inventory?.status === 'OUT_OF_STOCK'}
          >
            {inventory?.status === 'OUT_OF_STOCK' ? 'Out of Stock' : 'Add to Cart'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;