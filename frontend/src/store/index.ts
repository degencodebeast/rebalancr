import { configureStore } from '@reduxjs/toolkit'
import { setupListeners } from '@reduxjs/toolkit/query'
import { websocketApi } from './websocket/websocketApi'
//import { chatApi } from './chat/chatApi'
import webSocketReducer from './chat/webSocketSlice'

export const store = configureStore({
  reducer: {
    [websocketApi.reducerPath]: websocketApi.reducer,
    //[chatApi.reducerPath]: chatApi.reducer,
    // webSocket: webSocketReducer, // Comment this out if using the RTK Query approach
  },
  middleware: (getDefaultMiddleware) =>
    // getDefaultMiddleware({
    //   serializableCheck: {
    //     // Ignore these action types
    //     ignoredActions: ['webSocket/connect/fulfilled'],
    //     // Ignore these field paths in all actions
    //     ignoredActionPaths: ['payload.socket'],
    //   },
    // }).concat(
    //   websocketApi.middleware,
    //   //chatApi.middleware
    // ),
    getDefaultMiddleware().concat(websocketApi.middleware),
})

setupListeners(store.dispatch)

export type AppDispatch = typeof store.dispatch
export type RootState = ReturnType<typeof store.getState>
