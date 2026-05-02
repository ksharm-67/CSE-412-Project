import api from './axiosInstance.js'

function getParts() {
    return api.get('/parts');
}

function createPart(data) {
    return api.post('/parts/', data);
}

function updatePart(id, data) {
    return api.put(`/parts/${id}`, data);
}

function restockPart(id, qty) {
    return api.post(`/parts/${id}/restock`, qty);
}

export { getParts, createPart, updatePart, restockPart };