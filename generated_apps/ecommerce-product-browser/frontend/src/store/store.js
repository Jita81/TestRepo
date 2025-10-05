import { configureStore } from '@reduxjs/toolkit';
import productsReducer from './slices/productsSlice';
import filtersReducer from './slices/filtersSlice';
import searchReducer from './slices/searchSlice';
import categoriesReducer from './slices/categoriesSlice';

const store = configureStore({
  reducer: {
    products: productsReducer,
    filters: filtersReducer,
    search: searchReducer,
    categories: categoriesReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export default store;