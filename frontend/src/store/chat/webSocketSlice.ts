import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { createAppAsyncThunk } from '../createAppAsyncThunk';

interface WebSocketState {
  connected: boolean;
  messages: any[];
  error: string | null;
  isLoading: boolean;
}

const initialState: WebSocketState = {
  connected: false,
  messages: [],
  error: null,
  isLoading: false,
};

// Create async thunks
export const connectWebSocket = createAppAsyncThunk(
  'webSocket/connect',
  async (userId: string, { dispatch }) => {
    try {
      //const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/${userId}`;
      const wsUrl = `ws://localhost:8000/ws/`;
      const socket = new WebSocket(wsUrl);
      
      socket.onopen = () => {
        dispatch(connectSuccess());
      };
      
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          dispatch(messageReceived(data));
        } catch (err) {
          console.error('Failed to parse message:', err);
        }
      };
      
      socket.onerror = (error) => {
        dispatch(connectFailed('WebSocket connection error'));
        console.error('WebSocket error:', error);
      };
      
      socket.onclose = () => {
        dispatch(disconnected());
      };
      
      // Store socket in window for global access
      (window as any).chatSocket = socket;
      
      return true;
    } catch (error) {
      dispatch(connectFailed('Failed to connect to WebSocket'));
      console.error('WebSocket connection failed:', error);
      return false;
    }
  }
);

export const sendWebSocketMessage = createAppAsyncThunk(
  'webSocket/sendMessage',
  async (message: string) => {
    const socket = (window as any).chatSocket;
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'chat_message',
        message
      }));
      return true;
    } else {
      console.error('WebSocket is not connected');
      return false;
    }
  }
);

const webSocketSlice = createSlice({
  name: 'webSocket',
  initialState,
  reducers: {
    connectStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    connectSuccess: (state) => {
      state.connected = true;
      state.isLoading = false;
    },
    connectFailed: (state, action: PayloadAction<string>) => {
      state.connected = false;
      state.isLoading = false;
      state.error = action.payload;
    },
    messageReceived: (state, action: PayloadAction<any>) => {
      state.messages.push(action.payload);
    },
    disconnected: (state) => {
      state.connected = false;
    },
    clearMessages: (state) => {
      state.messages = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(connectWebSocket.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(connectWebSocket.fulfilled, (state) => {
        // Actual connection status is handled by the onopen event
        state.isLoading = false;
      })
      .addCase(connectWebSocket.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to connect';
      })
      .addCase(sendWebSocketMessage.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(sendWebSocketMessage.fulfilled, (state) => {
        state.isLoading = false;
      })
      .addCase(sendWebSocketMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to send message';
      });
  },
});

export const {
  connectStart,
  connectSuccess,
  connectFailed,
  messageReceived,
  disconnected,
  clearMessages,
} = webSocketSlice.actions;

export default webSocketSlice.reducer; 