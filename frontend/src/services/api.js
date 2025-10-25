import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5501';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 10000,
});

export const audioAPI = {
  // Get list of all audio files
  getAudioFiles: async () => {
    const response = await api.get('/audio-files');
    return response.data;
  },

  // Get audio file URL for streaming
  getAudioUrl: (filename) => {
    return `${API_BASE_URL}/api/audio/${encodeURIComponent(filename)}`;
  },

  // Trigger transcription
  transcribeAudio: async (filename) => {
    const response = await api.post(`/transcribe/${encodeURIComponent(filename)}`);
    return response.data;
  },

  // Get transcript for audio file
  getTranscript: async (filename) => {
    const response = await api.get(`/transcript/${encodeURIComponent(filename)}`);
    return response.data;
  },

  // Get processing status
  getStatus: async (filename) => {
    const response = await api.get(`/status/${encodeURIComponent(filename)}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;

