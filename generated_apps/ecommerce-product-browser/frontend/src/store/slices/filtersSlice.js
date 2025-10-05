import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  category: '',
  minPrice: null,
  maxPrice: null,
  sort: 'newest',
  inStock: false,
  priceRange: [0, 1000],
};

const filtersSlice = createSlice({
  name: 'filters',
  initialState,
  reducers: {
    setCategory: (state, action) => {
      state.category = action.payload;
    },
    setPriceRange: (state, action) => {
      const [min, max] = action.payload;
      state.minPrice = min;
      state.maxPrice = max;
      state.priceRange = action.payload;
    },
    setSort: (state, action) => {
      state.sort = action.payload;
    },
    setInStock: (state, action) => {
      state.inStock = action.payload;
    },
    clearFilters: (state) => {
      state.category = '';
      state.minPrice = null;
      state.maxPrice = null;
      state.sort = 'newest';
      state.inStock = false;
      state.priceRange = [0, 1000];
    },
    setFilters: (state, action) => {
      return { ...state, ...action.payload };
    },
  },
});

export const {
  setCategory,
  setPriceRange,
  setSort,
  setInStock,
  clearFilters,
  setFilters,
} = filtersSlice.actions;

export default filtersSlice.reducer;