import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { getTechnicianOrders } from '../api/technicians';
import { updateOrderStatus } from '../api/orders';
import { getParts } from '../api/parts';

export default function Technician() {
  const { user, logout } = useContext(AuthContext);
  const [orders, setOrders] = useState([]);
  const [parts, setParts] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getTechnicianOrders(user.techkey)
      .then(res => setOrders(res.data))
      .catch(() => setError('Failed to load orders'));
    getParts()
      .then(res => setParts(res.data))
      .catch(() => setError('Failed to load parts'));
  }, []);

  const handleStatusUpdate = async (repairkey, newStatus) => {
    try {
      await updateOrderStatus(repairkey, newStatus);
      setOrders(orders.map(o => 
        o.ro_repairkey === repairkey ? { ...o, ro_status: newStatus } : o
      ));
    } catch (err) {
      setError('Failed to update status');
    }
  };

  return (
    <div>
      <button type="button" onClick={logout}>Sign Out</button>
      <div className="tech-dashboard">
        <h1>Technician Dashboard</h1>
        {error && <p>{error}</p>}

        <h2>Your Orders</h2>
        {orders.length === 0 && <p>No orders assigned.</p>}
        {orders.map(order => (
          <div key={order.ro_repairkey} className="order-card">
            <p>Order #: {order.ro_repairkey}</p>
            <p>Status: {order.ro_status}</p>
            <p>Issue: {order.ro_issuedecription}</p>
            <p>Cost: ${order.ro_totalcost}</p>
            <p>Date Started: {order.ro_datestarted}</p>
            {order.ro_status === 'received' && (
              <button type="button" onClick={() => handleStatusUpdate(order.ro_repairkey, 'pending')}>
                Mark as Pending
              </button>
            )}
            {order.ro_status === 'pending' && (
              <button type="button" onClick={() => handleStatusUpdate(order.ro_repairkey, 'completed')}>
                Mark as Completed
              </button>
            )}
          </div>
        ))}

        <h2>Inventory</h2>
        {parts.length === 0 && <p>No parts in inventory.</p>}
        <table>
          <thead>
            <tr>
              <th>Part Key</th>
              <th>Name</th>
              <th>Stock</th>
              <th>Unit Price</th>
            </tr>
          </thead>
          <tbody>
            {parts.map(part => (
              <tr key={part.p_partkey}>
                <td>{part.p_partkey}</td>
                <td>{part.p_name}</td>
                <td>{part.p_stockqty}</td>
                <td>${part.p_unitprice}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}