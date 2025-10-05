import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import App from './App';
import productsReducer from './store/slices/productsSlice';
import filtersReducer from './store/slices/filtersSlice';
import searchReducer from './store/slices/searchSlice';
import categoriesReducer from './store/slices/categoriesSlice';

// Create a test store
const createTestStore = () => {
  return configureStore({
    reducer: {
      products: productsReducer,
      filters: filtersReducer,
      search: searchReducer,
      categories: categoriesReducer,
    },
  });
};

describe('App Component', () => {
  it('renders without crashing', () => {
    const store = createTestStore();
    render(
      <Provider store={store}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Provider>
    );
    
    // Check if header is rendered
    expect(screen.getByText('E-Shop')).toBeInTheDocument();
  });

  it('renders search bar in header', () => {
    const store = createTestStore();
    render(
      <Provider store={store}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Provider>
    );
    
    // Check if search input is rendered
    const searchInput = screen.getByPlaceholderText(/search for products/i);
    expect(searchInput).toBeInTheDocument();
  });
});