import api from './axiosInstance.js';

export const createDevice = (data) => api.post('/devices/', data);
export const getDevice = (id) => api.get(`/devices/${id}`);
export const updateDevice = (id, data) => api.put(`/devices/${id}`, data);
export const deleteDevice = (id) => api.delete(`/devices/${id}`);