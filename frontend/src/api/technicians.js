import api from './axiosInstance.js'

function getTechnicianOrders(id) {
    return api.get(`/technicians/${id}/orders`);
}

function getBusiestTechnician(){
    return api.get('/technicians/busiest');
}

export { getTechnicianOrders, getBusiestTechnician };