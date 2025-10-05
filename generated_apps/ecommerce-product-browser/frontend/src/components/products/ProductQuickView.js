import React, { useEffect } from 'react';
import './ProductQuickView.css';

const ProductQuickView = ({ product, onClose }) => {
  const {
    name,
    description,
    price,
    category,
    images,
    inventory,
    attributes,
  } = product;

  useEffect(() => {
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
    
    // Close on Escape key
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    
    document.addEventListener('keydown', handleEscape);
    
    return () => {
      document.body.style.overflow = 'unset';
      document.removeEventListener('keydown', handleEscape);
    };
  }, [onClose]);

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const mainImage = images?.main?.[0] || images?.thumbnail || 'https://via.placeholder.com/600x600?text=No+Image';

  return (
    <div className="quick-view-overlay" onClick={handleBackdropClick}>
      <div className="quick-view-modal">
        <button className="close-button" onClick={onClose} aria-label="Close">
          ✕
        </button>
        
        <div className="quick-view-content">
          <div className="quick-view-image">
            <img src={mainImage} alt={name} />
          </div>
          
          <div className="quick-view-details">
            <span className="quick-view-category">{category}</span>
            <h2 className="quick-view-title">{name}</h2>
            
            <div className="quick-view-price">
              ${parseFloat(price).toFixed(2)}
            </div>
            
            <div className="quick-view-stock">
              {inventory?.status === 'IN_STOCK' && (
                <span className="stock-badge in-stock">✓ In Stock</span>
              )}
              {inventory?.status === 'LOW_STOCK' && (
                <span className="stock-badge low-stock">⚠ Low Stock</span>
              )}
              {inventory?.status === 'OUT_OF_STOCK' && (
                <span className="stock-badge out-of-stock">✕ Out of Stock</span>
              )}
              {inventory?.quantity && inventory.status !== 'OUT_OF_STOCK' && (
                <span className="stock-quantity">({inventory.quantity} available)</span>
              )}
            </div>
            
            <p className="quick-view-description">{description}</p>
            
            {attributes && Object.keys(attributes).length > 0 && (
              <div className="quick-view-attributes">
                <h3>Details</h3>
                <ul>
                  {Object.entries(attributes).map(([key, value]) => (
                    <li key={key}>
                      <strong>{key}:</strong> {value}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <div className="quick-view-actions">
              <button
                className="btn btn-primary add-to-cart"
                disabled={inventory?.status === 'OUT_OF_STOCK'}
              >
                {inventory?.status === 'OUT_OF_STOCK' ? 'Out of Stock' : 'Add to Cart'}
              </button>
              <button className="btn btn-secondary view-details">
                View Full Details
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductQuickView;