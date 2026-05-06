import api from './api';

export const ttsApi = {
  synthesize: async (text: string, voice?: string, emotion?: string, provider?: string) => {
    const response = await api.post('/tts/synthesize', {
      text,
      voice: voice || 'default',
      emotion: emotion || 'neutral',
      provider,
    });
    return response.data;
  },

  getAudioUrl: (filename: string) => {
    return `/api/tts/audio/${filename}`;
  },
};
