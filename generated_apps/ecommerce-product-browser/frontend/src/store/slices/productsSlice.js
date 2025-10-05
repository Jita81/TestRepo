import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import * as productAPI from '../../services/productAPI';

export const fetchProducts = createAsyncThunk(
  'products/fetchProducts',
  async (params, { rejectWithValue }) => {
    try {
      const response = await productAPI.getProducts(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const fetchProductById = createAsyncThunk(
  'products/fetchProductById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await productAPI.getProductById(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

const initialState = {
  items: [],
  selectedProduct: null,
  pagination: {
    total: 0,
    page: 1,
    limit: 20,
    totalPages: 0,
  },
  loading: false,
  error: null,
  hasMore: true,
};

const productsSlice = createSlice({
  name: 'products',
  initialState,
  reducers: {
    clearProducts: (state) => {
      state.items = [];
      state.pagination.page = 1;
      state.hasMore = true;
    },
    clearError: (state) => {
      state.error = null;
    },
    incrementPage: (state) => {
      state.pagination.page += 1;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch products
      .addCase(fetchProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false;
        const { items, pagination } = action.payload;
        
        // Append items for infinite scroll or replace for new search
        if (pagination.page === 1) {
          state.items = items;
        } else {
          state.items = [...state.items, ...items];
        }
        
        state.pagination = pagination;
        state.hasMore = pagination.page < pagination.totalPages;
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch products';
      })
      // Fetch product by ID
      .addCase(fetchProductById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProductById.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedProduct = action.payload;
      })
      .addCase(fetchProductById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch product';
      });
  },
});

export const { clearProducts, clearError, incrementPage } = productsSlice.actions;
export default productsSlice.reducer;