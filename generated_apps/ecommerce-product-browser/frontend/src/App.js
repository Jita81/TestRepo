import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header';
import ProductListingPage from './pages/ProductListingPage';
import './App.css';

function App() {
  return (
    <div className="app">
      <Header />
      <Routes>
        <Route path="/" element={<ProductListingPage />} />
        <Route path="/category/:category" element={<ProductListingPage />} />
      </Routes>
    </div>
  );
}

export default App;