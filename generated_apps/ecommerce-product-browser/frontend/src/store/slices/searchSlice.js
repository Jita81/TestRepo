import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import * as searchAPI from '../../services/searchAPI';

export const searchProducts = createAsyncThunk(
  'search/searchProducts',
  async (params, { rejectWithValue }) => {
    try {
      const response = await searchAPI.searchProducts(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const fetchSuggestions = createAsyncThunk(
  'search/fetchSuggestions',
  async (query, { rejectWithValue }) => {
    try {
      const response = await searchAPI.getSuggestions(query);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const fetchAggregations = createAsyncThunk(
  'search/fetchAggregations',
  async (params, { rejectWithValue }) => {
    try {
      const response = await searchAPI.getAggregations(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

const initialState = {
  query: '',
  results: [],
  suggestions: [],
  aggregations: null,
  total: 0,
  loading: false,
  error: null,
  isSearchMode: false,
};

const searchSlice = createSlice({
  name: 'search',
  initialState,
  reducers: {
    setQuery: (state, action) => {
      state.query = action.payload;
    },
    clearSearch: (state) => {
      state.query = '';
      state.results = [];
      state.suggestions = [];
      state.total = 0;
      state.isSearchMode = false;
    },
    clearSuggestions: (state) => {
      state.suggestions = [];
    },
    setSearchMode: (state, action) => {
      state.isSearchMode = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Search products
      .addCase(searchProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.results = action.payload.results || [];
        state.total = action.payload.total || 0;
        state.isSearchMode = true;
      })
      .addCase(searchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Search failed';
      })
      // Fetch suggestions
      .addCase(fetchSuggestions.fulfilled, (state, action) => {
        state.suggestions = action.payload.suggestions || [];
      })
      // Fetch aggregations
      .addCase(fetchAggregations.fulfilled, (state, action) => {
        state.aggregations = action.payload;
      });
  },
});

export const { setQuery, clearSearch, clearSuggestions, setSearchMode } = searchSlice.actions;
export default searchSlice.reducer;