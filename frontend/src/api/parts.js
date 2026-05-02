import api from './axiosInstance.js'

function getParts() {
    return api.get('/parts');
}

function updatePart(id, data) {
    return api.put(`/parts/${id}`, data);
}

function restockPart(id, qty) {
    return api.patch(`/parts/${id}/restock`, qty);
}

export { getParts, updatePart, restockPart };