import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { ChatMessage, ChatState } from '../types/chat';

const initialState: ChatState = {
  messages: [],
  isProcessing: false,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload);
    },
    updateMessage: (state, action: PayloadAction<{ id: string; updates: Partial<ChatMessage> }>) => {
      const { id, updates } = action.payload;
      const message = state.messages.find((msg) => msg.id === id);
      if (message) {
        Object.assign(message, updates);
      }
    },
    removeMessage: (state, action: PayloadAction<string>) => {
      state.messages = state.messages.filter((msg) => msg.id !== action.payload);
    },
    setProcessing: (state, action: PayloadAction<boolean>) => {
      state.isProcessing = action.payload;
    },
    clearChat: (state) => {
      state.messages = [];
      state.isProcessing = false;
    },
  },
});

export const { addMessage, updateMessage, removeMessage, setProcessing, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
