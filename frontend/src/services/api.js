import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadDocument = async (file, template = 'gost_vkr') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('template', template);

  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getDocumentStatus = async (documentId) => {
  const response = await api.get(`/documents/documents/${documentId}`);
  return response.data;
};

export const downloadDocument = async (documentId) => {
  const response = await api.get(`/documents/documents/${documentId}/download`, {
    responseType: 'blob',
  });
  return response.data;
};

export const getDocuments = async (skip = 0, limit = 100) => {
  const response = await api.get('/documents/documents', {
    params: { skip, limit },
  });
  return response.data;
};

export const getTemplates = async () => {
  const response = await api.get('/documents/templates');
  return response.data;
};

export default api;
