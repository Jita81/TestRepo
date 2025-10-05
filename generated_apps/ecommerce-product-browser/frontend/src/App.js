import React, { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import Header from './components/layout/Header';
import ProductListingPage from './pages/ProductListingPage';
import CartPage from './components/cart/CartPage';
import AddToCartNotification from './components/cart/AddToCartNotification';
import { fetchCart } from './store/slices/cartSlice';
import './App.css';

function App() {
  const dispatch = useDispatch();

  useEffect(() => {
    // Fetch cart on app load
    dispatch(fetchCart());
  }, [dispatch]);

  return (
    <div className="app">
      <Header />
      <AddToCartNotification />
      <Routes>
        <Route path="/" element={<ProductListingPage />} />
        <Route path="/category/:category" element={<ProductListingPage />} />
        <Route path="/cart" element={<CartPage />} />
      </Routes>
    </div>
  );
}

export default App;