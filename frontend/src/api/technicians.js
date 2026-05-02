import api from './axiosInstance.js'

function getTechnicians() {
    return api.get('/technicians/');
}

function getTechnician(id) {
    return api.get(`/technicians/${id}`);
}

function getTechnicianOrders(id) {
    return api.get(`/technicians/${id}/orders`);
}

function getBusiestTechnician(){
    return api.get('/technicians/busiest');
}

export { getTechnicians, getTechnician, getTechnicianOrders, getBusiestTechnician };