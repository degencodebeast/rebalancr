import { createApi } from '@reduxjs/toolkit/query/react'
import { createSelector } from '@reduxjs/toolkit'
import { RootState, store } from '../index'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'
const RECONNECT_INTERVAL = 5000
const MAX_RECONNECT_ATTEMPTS = 5

// Global WebSocket reference
let globalWsConnection: WebSocket | null = null;

// Message type definition
export interface Message {
  id: string
  sender: 'user' | 'assistant'
  content: string
  timestamp: Date
}

// WebSocket status interface
export interface WebSocketStatus {
  connected: boolean
  authenticated: boolean
  authenticating: boolean
  error: string | null
}

export const websocketApi = createApi({
  reducerPath: 'websocketApi',
  baseQuery: () => ({ data: null }),
  tagTypes: ['WebSocketStatus', 'Messages'],
  endpoints: (builder) => ({
    // Query to manage WebSocket connection and status
    getWebSocketStatus: builder.query<WebSocketStatus, void>({
      queryFn: () => ({ 
        data: {
          connected: false,
          authenticated: false,
          authenticating: false,
          error: null
        }
      }),
      async onCacheEntryAdded(
        _arg,
        { 
          updateCachedData,
          cacheDataLoaded, 
          cacheEntryRemoved, 
          dispatch,
          getState
        },
      ) {
        let retryTimeout: NodeJS.Timeout | undefined
        let reconnectAttempts = 0

        // Function to create WebSocket connection
        const createWebSocketConnection = () => {
          try {
            const state = getState() as RootState;
            const authToken = state.websocket.authToken;
            const userId = state.websocket.userId;
            const shouldConnect = state.websocket.shouldConnect;

            // Only connect if we should
            if (!shouldConnect) {
              return;
            }

            // Update status to connecting
            updateCachedData((draft) => {
              draft.authenticating = true;
              draft.error = null;
              return draft;
            });
            
            // Close existing connection if any
            if (globalWsConnection) {
              globalWsConnection.close();
            }
            
            // Create new WebSocket connection
            const ws = new WebSocket(WS_URL);
            globalWsConnection = ws;

            ws.onopen = () => {
              console.log('WebSocket connected');
              
              // Update connected state
              updateCachedData((draft) => {
                draft.connected = true;
                return draft;
              });
              
              // Send authentication message if we have a token
              if (authToken) {
                ws.send(JSON.stringify({ 
                  type: 'auth',
                  token: authToken,
                  userId
                }));
              }
            };

            ws.onmessage = (event) => {
              try {
                const data = JSON.parse(event.data);
                
                // Handle authentication responses
                if (data.type === 'auth_success') {
                  console.log('Authentication successful');
                  updateCachedData((draft) => {
                    draft.authenticated = true;
                    draft.authenticating = false;
                    draft.error = null;
                    return draft;
                  });
                  reconnectAttempts = 0;
                } 
                else if (data.type === 'auth_failed') {
                  console.error('Authentication failed:', data.error);
                  updateCachedData((draft) => {
                    draft.authenticated = false;
                    draft.authenticating = false;
                    draft.error = data.error || 'Authentication failed';
                    return draft;
                  });
                }
                // Other message handling is in the getMessages endpoint
              } catch (error) {
                console.error('Error parsing message:', error);
              }
            };

            ws.onclose = (event) => {
              console.log('WebSocket closed:', event.reason);
              
              // Update connection state
              updateCachedData((draft) => {
                draft.connected = false;
                draft.authenticated = false;
                draft.authenticating = false;
                draft.error = event.code === 1000 ? null : 'Connection closed';
                return draft;
              });
              
              // Try to reconnect with backoff if needed
              const state = getState() as RootState;
              const shouldReconnect = state.websocket.shouldConnect;
              
              if (shouldReconnect && event.code !== 1000 && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                const backoffTime = RECONNECT_INTERVAL * Math.pow(1.5, reconnectAttempts);
                console.log(`Reconnecting in ${backoffTime}ms (attempt ${reconnectAttempts + 1})`);
                
                reconnectAttempts++;
                retryTimeout = setTimeout(() => {
                  createWebSocketConnection();
                }, backoffTime);
              }
            };

            ws.onerror = (error) => {
              console.error('WebSocket error:', error);
              updateCachedData((draft) => {
                draft.error = 'Connection error';
                return draft;
              });
            };
          } catch (error) {
            console.error('Failed to establish connection:', error);
            updateCachedData((draft) => {
              draft.authenticating = false;
              draft.error = 'Failed to establish connection';
              return draft;
            });
          }
        };

        try {
          await cacheDataLoaded;
          
          // Set up state change listener to reconnect when auth token changes
          const handleStateChange = () => {
            const state = getState() as RootState;
            const shouldConnect = state.websocket.shouldConnect;
            
            if (shouldConnect) {
              createWebSocketConnection();
            } else if (globalWsConnection) {
              globalWsConnection.close();
            }
          };
          
          // Initial connection if needed
          handleStateChange();
          
          // Subscribe to store changes to watch for auth token updates
          const unsubscribe = store.subscribe(() => {
            handleStateChange();
          });

          // Cleanup function
          await cacheEntryRemoved;
          clearTimeout(retryTimeout);
          unsubscribe();
          if (globalWsConnection) {
            globalWsConnection.close();
            globalWsConnection = null;
          }
        } catch (err) {
          console.error('WebSocket setup error:', err);
        }
      },
    }),
    
    // Query to manage messages
    getMessages: builder.query<Message[], void>({
      queryFn: () => ({ data: [] }),
      providesTags: ['Messages'],
      async onCacheEntryAdded(
        _arg,
        { updateCachedData, cacheDataLoaded, cacheEntryRemoved }
      ) {
        try {
          await cacheDataLoaded;
          
          // Message handler function
          const handleMessage = (event: MessageEvent) => {
            try {
              const data = JSON.parse(event.data);
              
              // Skip auth messages, they're handled in getWebSocketStatus
              if (data.type === 'auth_success' || data.type === 'auth_failed') {
                return;
              }
              
              // If data.content exists, treat it as a chat message
              if (data.content) {
                updateCachedData((draft) => {
                  draft.push({
                    id: `assistant-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
                    sender: 'assistant',
                    content: data.content,
                    timestamp: new Date(),
                  });
                  return draft;
                });
              }
            } catch (error) {
              console.error('Error handling message:', error);
              
              // Handle plain text messages if needed
              updateCachedData((draft) => {
                draft.push({
                  id: `assistant-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
                  sender: 'assistant',
                  content: event.data,
                  timestamp: new Date(),
                });
                return draft;
              });
            }
          };
          
          // Add event listener if WebSocket is available
          const handleWebSocketMessage = (event: MessageEvent) => {
            handleMessage(event);
          };
          
          if (globalWsConnection) {
            globalWsConnection.addEventListener('message', handleWebSocketMessage);
          }
          
          // Clean up
          await cacheEntryRemoved;
          if (globalWsConnection) {
            globalWsConnection.removeEventListener('message', handleWebSocketMessage);
          }
        } catch (err) {
          console.error('Error in getMessages:', err);
        }
      }
    }),
    
    // Mutation to send messages
    sendMessage: builder.mutation<boolean, { content: string }>({
      queryFn: async ({ content }, { getState }) => {
        if (!globalWsConnection || globalWsConnection.readyState !== WebSocket.OPEN) {
          return { error: 'WebSocket not connected' };
        }
        
        try {
          const state = getState() as RootState;
          const userId = state.websocket.userId;
          
          globalWsConnection.send(JSON.stringify({
            type: 'chat_message',
            content,
            userId
          }));
          
          return { data: true };
        } catch (error) {
          console.error('Error sending message:', error);
          return { error: 'Failed to send message' };
        }
      },
      // This invalidates the Messages tag to trigger a refetch
      invalidatesTags: ['Messages']
    }),
    
    // Mutation to add a local message (for user messages)
    addLocalMessage: builder.mutation<boolean, Message>({
      queryFn: async (message) => {
        return { data: true };
      },
      // Update the messages cache directly
      async onQueryStarted(message, { dispatch, queryFulfilled }) {
        const patchResult = dispatch(
          websocketApi.util.updateQueryData('getMessages', undefined, (draft) => {
            draft.push(message);
          })
        );
        
        try {
          await queryFulfilled;
        } catch {
          patchResult.undo();
        }
      }
    })
  }),
})

// Create selectors for WebSocket status
export const selectWebSocketConnected = createSelector(
  [(state: RootState) => state[websocketApi.reducerPath].queries['getWebSocketStatus(undefined)']?.data],
  (data) => data?.connected || false
);

export const selectWebSocketAuthenticated = createSelector(
  [(state: RootState) => state[websocketApi.reducerPath].queries['getWebSocketStatus(undefined)']?.data],
  (data) => data?.authenticated || false
);

export const selectWebSocketAuthenticating = createSelector(
  [(state: RootState) => state[websocketApi.reducerPath].queries['getWebSocketStatus(undefined)']?.data],
  (data) => data?.authenticating || false
);

export const selectWebSocketError = createSelector(
  [(state: RootState) => state[websocketApi.reducerPath].queries['getWebSocketStatus(undefined)']?.data],
  (data) => data?.error || null
);

export const selectMessages = createSelector(
  [(state: RootState) => state[websocketApi.reducerPath].queries['getMessages(undefined)']?.data],
  (data) => data || []
);

export const { 
  useGetWebSocketStatusQuery,
  useGetMessagesQuery,
  useSendMessageMutation,
  useAddLocalMessageMutation
} = websocketApi;
