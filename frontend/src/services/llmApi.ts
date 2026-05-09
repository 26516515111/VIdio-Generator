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

  processDirector: async (
    text: string,
    scene: string,
    character: string,
    direction: string,
    provider?: string
  ) => {
    const response = await api.post('/llm/director', {
      text,
      scene,
      character,
      direction,
      provider,
    });
    return response.data;
  },

  polishText: async (text: string, scene: string, provider?: string) => {
    const response = await api.post('/llm/process', {
      text,
      scene,
      processing_type: 'polish',
      provider: provider || 'xiaomi-tokenplan',
    });
    return response.data;
  },

  sceneToStyle: async (scene: string, provider?: string) => {
    const response = await api.post('/llm/scene-to-style', {
      scene,
      provider,
    });
    return response.data;
  },
};
