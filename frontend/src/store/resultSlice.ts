import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

interface ResultState {
  processedText: string;
  detectedEmotion: string;
  audioUrl: string | null;
  loading: boolean;
  error: string | null;
}

const initialState: ResultState = {
  processedText: '',
  detectedEmotion: '',
  audioUrl: null,
  loading: false,
  error: null,
};

const resultSlice = createSlice({
  name: 'result',
  initialState,
  reducers: {
    setProcessedText: (state, action: PayloadAction<string>) => {
      state.processedText = action.payload;
    },
    setDetectedEmotion: (state, action: PayloadAction<string>) => {
      state.detectedEmotion = action.payload;
    },
    setAudioUrl: (state, action: PayloadAction<string | null>) => {
      state.audioUrl = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    resetResult: (state) => {
      state.processedText = '';
      state.detectedEmotion = '';
      state.audioUrl = null;
      state.error = null;
    },
  },
});

export const {
  setProcessedText,
  setDetectedEmotion,
  setAudioUrl,
  setLoading,
  setError,
  resetResult,
} = resultSlice.actions;
export default resultSlice.reducer;
