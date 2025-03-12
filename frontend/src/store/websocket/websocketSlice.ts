import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { RootState } from '../index'

export interface WebSocketState {
  authToken: string | null;
  userId: string | null;
  shouldConnect: boolean;
}

const initialState: WebSocketState = {
  authToken: null,
  userId: null,
  shouldConnect: false
}

export const websocketSlice = createSlice({
  name: 'websocket',
  initialState,
  reducers: {
    setAuthToken: (state, action: PayloadAction<string>) => {
      state.authToken = action.payload;
    },
    setUserId: (state, action: PayloadAction<string>) => {
      state.userId = action.payload;
    },
    setShouldConnect: (state, action: PayloadAction<boolean>) => {
      state.shouldConnect = action.payload;
    },
    resetWebSocketState: (state) => {
      state.authToken = null;
      state.userId = null;
      state.shouldConnect = false;
    }
  }
})

// Selectors
export const selectAuthToken = (state: RootState) => state.websocket.authToken;
export const selectUserId = (state: RootState) => state.websocket.userId;
export const selectShouldConnect = (state: RootState) => state.websocket.shouldConnect;

export const { setAuthToken, setUserId, setShouldConnect, resetWebSocketState } = websocketSlice.actions;

export default websocketSlice.reducer; 