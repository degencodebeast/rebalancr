import { configureStore } from '@reduxjs/toolkit'
import { setupListeners } from '@reduxjs/toolkit/query'
import { websocketApi } from './websocket/websocketApi'
import websocketReducer from './websocket/websocketSlice'

export const store = configureStore({
  reducer: {
    [websocketApi.reducerPath]: websocketApi.reducer,
    websocket: websocketReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(websocketApi.middleware),
})

setupListeners(store.dispatch)

export type AppDispatch = typeof store.dispatch
export type RootState = ReturnType<typeof store.getState>
