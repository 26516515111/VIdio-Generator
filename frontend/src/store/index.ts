import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import inputReducer from './inputSlice';
import resultReducer from './resultSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    input: inputReducer,
    result: resultReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
