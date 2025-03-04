import { createAsyncThunk } from '@reduxjs/toolkit';
import type { RootState, AppDispatch } from './index';

// Create typed version of createAsyncThunk
export const createAppAsyncThunk = createAsyncThunk.withTypes<{
  state: RootState;
  dispatch: AppDispatch;
  rejectValue: string;
}>(); 