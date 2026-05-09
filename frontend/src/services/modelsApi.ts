import api from './api';

export interface ModelInfo {
  id: number;
  provider: string;
  model_name: string | null;
  is_default: boolean;
}

export interface ModelsByType {
  ocr: ModelInfo[];
  llm: ModelInfo[];
  tts: ModelInfo[];
}

export const modelsApi = {
  getAvailableModels: async (): Promise<ModelsByType> => {
    const response = await api.get('/users/models');
    return response.data;
  },
};
