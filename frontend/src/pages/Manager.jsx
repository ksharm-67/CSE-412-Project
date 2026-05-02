import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { getAllOrders, updateOrderStatus } from '../api/orders';
import { getParts, createPart, restockPart } from '../api/parts';

export default function Manager() {
  const { logout } = useContext(AuthContext);
  const [tab, setTab] = useState('orders');
  const [orders, setOrders] = useState([]);
  const [parts, setParts] = useState([]);
  const [error, setError] = useState(null);
  const [restockQty, setRestockQty] = useState({});
  const [newPart, setNewPart] = useState({ name: '', serialnum: '', stockqty: '', unitprice: '' });

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

  const handleCreatePart = async () => {
    const stockqty = parseInt(newPart.stockqty);
    const unitprice = parseFloat(newPart.unitprice);
    if (!newPart.name || !newPart.serialnum || !stockqty || stockqty < 0 || isNaN(unitprice) || unitprice < 0) {
      setError('Fill in all fields with valid values');
      return;
    }
    try {
      await createPart({
        p_partkey: Math.floor(Math.random() * 900000) + 100000,
        p_name: newPart.name,
        p_serialnum: newPart.serialnum,
        p_stockqty: stockqty,
        p_unitprice: unitprice,
      });
      setNewPart({ name: '', serialnum: '', stockqty: '', unitprice: '' });
      setError(null);
      getParts().then(res => setParts(res.data));
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add part');
    }
  };

  return (
    <div className="manager-dashboard">
      <div className="dashboard-header">
        <h1>Manager Dashboard</h1>
        <button type="button" onClick={logout}>Sign Out</button>
      </div>
      {error && <p>{error}</p>}

      <div className="tabs">
        <button
          type="button"
          className={`tab ${tab === 'orders' ? 'active' : ''}`}
          onClick={() => setTab('orders')}
        >
          Orders
        </button>
        <button
          type="button"
          className={`tab ${tab === 'inventory' ? 'active' : ''}`}
          onClick={() => setTab('inventory')}
        >
          Inventory
        </button>
      </div>

      {tab === 'orders' && (
        <div className="tab-panel">
          <h2>All Orders</h2>
          {orders.length === 0 && <p>No orders found.</p>}
          {orders.length > 0 && (
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
          )}
        </div>
      )}

      {tab === 'inventory' && (
        <div className="tab-panel">
          <h2>Inventory</h2>

          <div className="new-part-form">
            <h3>Add New Part</h3>
            <input
              type="text"
              placeholder="Name"
              value={newPart.name}
              onChange={e => setNewPart({ ...newPart, name: e.target.value })}
            />
            <input
              type="text"
              placeholder="Serial #"
              value={newPart.serialnum}
              onChange={e => setNewPart({ ...newPart, serialnum: e.target.value })}
            />
            <input
              type="number"
              min="0"
              placeholder="Stock qty"
              value={newPart.stockqty}
              onChange={e => setNewPart({ ...newPart, stockqty: e.target.value })}
            />
            <input
              type="number"
              min="0"
              step="0.01"
              placeholder="Unit price"
              value={newPart.unitprice}
              onChange={e => setNewPart({ ...newPart, unitprice: e.target.value })}
            />
            <button type="button" onClick={handleCreatePart}>Add Part</button>
          </div>

          {parts.length === 0 && <p>No parts in inventory.</p>}
          {parts.length > 0 && (
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
          )}
        </div>
      )}
    </div>
  );
}
