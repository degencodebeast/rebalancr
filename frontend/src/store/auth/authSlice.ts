import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { RootState } from '../index'

interface AuthState {
  isVerifying: boolean;
  error: string | null;
  hasVerified: boolean;
}

const initialState: AuthState = {
  isVerifying: false,
  error: null,
  hasVerified: false
}

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    startVerifying: (state) => {
      state.isVerifying = true;
      state.error = null;
    },
    verificationSuccess: (state) => {
      state.isVerifying = false;
      state.error = null;
      state.hasVerified = true;
    },
    verificationFailed: (state, action: PayloadAction<string>) => {
      state.isVerifying = false;
      state.error = action.payload;
      state.hasVerified = false;
    },
    resetVerification: (state) => {
      state.isVerifying = false;
      state.error = null;
      state.hasVerified = false;
    }
  }
})

export const { 
  startVerifying, 
  verificationSuccess, 
  verificationFailed,
  resetVerification
} = authSlice.actions

export const selectIsVerifying = (state: RootState) => state.auth.isVerifying
export const selectVerificationError = (state: RootState) => state.auth.error
export const selectHasVerified = (state: RootState) => state.auth.hasVerified

export default authSlice.reducer