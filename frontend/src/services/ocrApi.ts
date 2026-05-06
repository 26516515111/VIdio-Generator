import api from './api';

export const ocrApi = {
  extractText: async (file: File, provider?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (provider) {
      formData.append('provider', provider);
    }

    const response = await api.post('/ocr/extract', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};
