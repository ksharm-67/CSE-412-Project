import api from './axiosInstance.js'

function createCustomer(data) {
    return api.post('/customers', data);
}

function getCustomerOrders(id) {
    return api.get('/customers/${id}/orders');
}

function getCustomerDevices(id) {
    return api.get('/customers/${id}/devices');
}

export { createCustomer, getCustomerOrders, getCustomerOrders }; 