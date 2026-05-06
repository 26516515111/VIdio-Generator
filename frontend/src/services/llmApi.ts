import api from './api';

export const llmApi = {
  processText: async (
    text: string,
    scene: string,
    emotion?: string,
    processingType?: string,
    provider?: string
  ) => {
    const response = await api.post('/llm/process', {
      text,
      scene,
      emotion,
      processing_type: processingType,
      provider,
    });
    return response.data;
  },
};
