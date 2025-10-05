import { configureStore } from '@reduxjs/toolkit';
import productsReducer from './slices/productsSlice';
import filtersReducer from './slices/filtersSlice';
import searchReducer from './slices/searchSlice';
import categoriesReducer from './slices/categoriesSlice';
import cartReducer, { loadFromLocalStorage } from './slices/cartSlice';

const store = configureStore({
  reducer: {
    products: productsReducer,
    filters: filtersReducer,
    search: searchReducer,
    categories: categoriesReducer,
    cart: cartReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

// Load cart from localStorage on initialization
store.dispatch(loadFromLocalStorage());

export default store;