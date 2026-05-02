import api from './axiosInstance.js'

function getOrder(id) {
    return api.get(`/orders/${id}`);
}

function getAllOrders() {
    return api.get('/orders/');
}

function createOrder(data) {
    return api.post('/orders/', data);
}

function updateOrderStatus(id, status) {
    return api.patch(`/orders/${id}/status`, { status });
}

function getOrderParts(id) {
    return api.get(`/orders/${id}/parts`);
}

function addOrderParts(id, data) {
    return api.post(`/orders/${id}/parts`, data);
}

function removeOrderPart(id, partId) {
    return api.delete(`/orders/${id}/parts/${partId}`);
}

function logOrderHours(id, hours) {
    return api.post(`/orders/${id}/hours`, { hours });
}

export { updateOrderStatus, getOrderParts, addOrderParts, removeOrderPart, getOrder, getAllOrders, createOrder, logOrderHours };