import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { getAllOrders, updateOrderStatus } from '../api/orders';
import { getParts, restockPart } from '../api/parts';

export default function Manager() {
  const { logout } = useContext(AuthContext);
  const [orders, setOrders] = useState([]);
  const [parts, setParts] = useState([]);
  const [error, setError] = useState(null);
  const [restockQty, setRestockQty] = useState({});

  useEffect(() => {
    getAllOrders()
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

  const handleRestock = async (partkey) => {
    try {
      await restockPart(partkey, { quantity: restockQty[partkey] });
      getParts().then(res => setParts(res.data));
    } catch (err) {
      setError('Failed to restock part');
    }
  };

  return (
    <div>
      <button type="button" onClick={logout}>Sign Out</button>
      <div className="manager-dashboard">
        <h1>Manager Dashboard</h1>
        {error && <p>{error}</p>}

        <h2>All Orders</h2>
        {orders.length === 0 && <p>No orders found.</p>}
        <table>
          <thead>
            <tr>
              <th>Order #</th>
              <th>Customer</th>
              <th>Status</th>
              <th>Issue</th>
              <th>Cost</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {orders.map(order => (
              <tr key={order.ro_repairkey}>
                <td>{order.ro_repairkey}</td>
                <td>{order.ro_custkey}</td>
                <td>{order.ro_status}</td>
                <td>{order.ro_issuedecription}</td>
                <td>${order.ro_totalcost}</td>
                <td>
                  {order.ro_status === 'received' && (
                    <button type="button" onClick={() => handleStatusUpdate(order.ro_repairkey, 'pending')}>
                      → Pending
                    </button>
                  )}
                  {order.ro_status === 'pending' && (
                    <>
                      <button type="button" onClick={() => handleStatusUpdate(order.ro_repairkey, 'completed')}>
                        → Completed
                      </button>
                      <button type="button" onClick={() => handleStatusUpdate(order.ro_repairkey, 'received')}>
                        → Received
                      </button>
                    </>
                  )}
                  {order.ro_status === 'completed' && (
                    <button type="button" onClick={() => handleStatusUpdate(order.ro_repairkey, 'pending')}>
                      → Pending
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <h2>Inventory</h2>
        {parts.length === 0 && <p>No parts in inventory.</p>}
        <table>
          <thead>
            <tr>
              <th>Part Key</th>
              <th>Name</th>
              <th>Stock</th>
              <th>Unit Price</th>
              <th>Restock</th>
            </tr>
          </thead>
          <tbody>
            {parts.map(part => (
              <tr key={part.p_partkey}>
                <td>{part.p_partkey}</td>
                <td>{part.p_name}</td>
                <td>{part.p_stockqty}</td>
                <td>${part.p_unitprice}</td>
                <td>
                  <input
                    type="number"
                    min="1"
                    value={restockQty[part.p_partkey] || ''}
                    onChange={e => setRestockQty({ ...restockQty, [part.p_partkey]: e.target.value })}
                  />
                  <button type="button" onClick={() => handleRestock(part.p_partkey)}>
                    Restock
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}