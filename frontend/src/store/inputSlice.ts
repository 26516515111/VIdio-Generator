import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

interface InputState {
  text: string;
  scene: string;
  imageUrl: string | null;
  inputType: 'text' | 'image';
}

const initialState: InputState = {
  text: '',
  scene: '',
  imageUrl: null,
  inputType: 'text',
};

const inputSlice = createSlice({
  name: 'input',
  initialState,
  reducers: {
    setText: (state, action: PayloadAction<string>) => {
      state.text = action.payload;
    },
    setScene: (state, action: PayloadAction<string>) => {
      state.scene = action.payload;
    },
    setImageUrl: (state, action: PayloadAction<string | null>) => {
      state.imageUrl = action.payload;
    },
    setInputType: (state, action: PayloadAction<'text' | 'image'>) => {
      state.inputType = action.payload;
    },
    resetInput: (state) => {
      state.text = '';
      state.scene = '';
      state.imageUrl = null;
    },
  },
});

export const { setText, setScene, setImageUrl, setInputType, resetInput } = inputSlice.actions;
export default inputSlice.reducer;
