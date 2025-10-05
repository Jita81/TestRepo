import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import * as categoryAPI from '../../services/categoryAPI';

export const fetchCategories = createAsyncThunk(
  'categories/fetchCategories',
  async (params, { rejectWithValue }) => {
    try {
      const response = await categoryAPI.getCategories(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const fetchCategoryTree = createAsyncThunk(
  'categories/fetchCategoryTree',
  async (_, { rejectWithValue }) => {
    try {
      const response = await categoryAPI.getCategoryTree();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const fetchBreadcrumb = createAsyncThunk(
  'categories/fetchBreadcrumb',
  async (categoryId, { rejectWithValue }) => {
    try {
      const response = await categoryAPI.getBreadcrumb(categoryId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

const initialState = {
  list: [],
  tree: [],
  breadcrumb: [],
  loading: false,
  error: null,
};

const categoriesSlice = createSlice({
  name: 'categories',
  initialState,
  reducers: {
    clearBreadcrumb: (state) => {
      state.breadcrumb = [];
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch categories
      .addCase(fetchCategories.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchCategories.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch categories';
      })
      // Fetch category tree
      .addCase(fetchCategoryTree.fulfilled, (state, action) => {
        state.tree = action.payload;
      })
      // Fetch breadcrumb
      .addCase(fetchBreadcrumb.fulfilled, (state, action) => {
        state.breadcrumb = action.payload;
      });
  },
});

export const { clearBreadcrumb } = categoriesSlice.actions;
export default categoriesSlice.reducer;