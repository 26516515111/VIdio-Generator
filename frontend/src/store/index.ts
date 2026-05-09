import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import inputReducer from './inputSlice';
import resultReducer from './resultSlice';
import chatReducer from './chatSlice';
import settingsReducer from './settingsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    input: inputReducer,
    result: resultReducer,
    chat: chatReducer,
    settings: settingsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
