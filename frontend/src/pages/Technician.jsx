import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { getTechnicianOrders, getTechnician } from '../api/technicians';
import { updateOrderStatus, addOrderParts, logOrderHours, getOrderParts } from '../api/orders';
import { getParts } from '../api/parts';

export default function Technician() {
  const { user, logout } = useContext(AuthContext);
  const [tab, setTab] = useState('orders');
  const [orders, setOrders] = useState([]);
  const [parts, setParts] = useState([]);
  const [error, setError] = useState(null);
  const [partSelection, setPartSelection] = useState({});
  const [hoursInput, setHoursInput] = useState({});
  const [hourlyRate, setHourlyRate] = useState(null);
  const [orderParts, setOrderParts] = useState({});

  const refreshOrderParts = async (orderList) => {
    const entries = await Promise.all(
      orderList.map(o =>
        getOrderParts(o.ro_repairkey)
          .then(res => [o.ro_repairkey, res.data])
          .catch(() => [o.ro_repairkey, []])
      )
    );
    setOrderParts(Object.fromEntries(entries));
  };

  const refreshOrders = async () => {
    const res = await getTechnicianOrders(user.techkey);
    setOrders(res.data);
    await refreshOrderParts(res.data);
  };
  const refreshParts = () => getParts().then(res => setParts(res.data));

  useEffect(() => {
    refreshOrders().catch(() => setError('Failed to load orders'));
    refreshParts().catch(() => setError('Failed to load parts'));
    getTechnician(user.techkey)
      .then(res => setHourlyRate(res.data.t_hourlyrate))
      .catch(() => {});
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

  const handleAddPart = async (repairkey) => {
    const sel = partSelection[repairkey] || {};
    const partkey = parseInt(sel.partkey);
    const qty = parseInt(sel.qty);
    if (!partkey || !qty || qty <= 0) {
      setError('Pick a part and a positive quantity');
      return;
    }
    try {
      await addOrderParts(repairkey, { p_partkey: partkey, o_qtyused: qty });
      setPartSelection({ ...partSelection, [repairkey]: { partkey: '', qty: '' } });
      setError(null);
      await Promise.all([refreshOrders(), refreshParts()]);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add part');
    }
  };

  const handleLogHours = async (repairkey) => {
    const hours = parseFloat(hoursInput[repairkey]);
    if (!hours || hours <= 0) {
      setError('Enter a positive number of hours');
      return;
    }
    try {
      await logOrderHours(repairkey, hours);
      setHoursInput({ ...hoursInput, [repairkey]: '' });
      setError(null);
      await refreshOrders();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to log hours');
    }
  };

  const updateSelection = (repairkey, field, value) => {
    setPartSelection({
      ...partSelection,
      [repairkey]: { ...(partSelection[repairkey] || {}), [field]: value },
    });
  };

  return (
    <div className="tech-dashboard">
      <div className="dashboard-header">
        <h1>Technician Dashboard</h1>
        <button type="button" onClick={logout}>Sign Out</button>
      </div>
      {error && <p className="error">{error}</p>}

      <div className="tabs">
        <button
          type="button"
          className={`tab ${tab === 'orders' ? 'active' : ''}`}
          onClick={() => setTab('orders')}
        >
          My Orders
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
          <h2>Your Orders</h2>
          {orders.length === 0 && <p>No orders assigned.</p>}
          {orders.map(order => {
            const sel = partSelection[order.ro_repairkey] || {};
            const used = orderParts[order.ro_repairkey] || [];
            return (
              <div key={order.ro_repairkey} className="order-card">
                <p>Order #: {order.ro_repairkey}</p>
                <p>Status: {order.ro_status}</p>
                <p>Issue: {order.ro_issuedecription}</p>
                <p>Cost: ${order.ro_totalcost}</p>
                <p>Date Started: {order.ro_datestarted}</p>

                <div className="parts-used">
                  <strong>Parts Used:</strong>
                  {used.length === 0 ? (
                    <span className="muted"> none yet</span>
                  ) : (
                    <ul>
                      {used.map(u => {
                        const p = parts.find(pp => pp.p_partkey === u.o_partkey);
                        const name = p?.p_name ?? `Part #${u.o_partkey}`;
                        const lineCost = p ? (p.p_unitprice * u.o_qtyused).toFixed(2) : null;
                        return (
                          <li key={u.o_partkey}>
                            {name} × {u.o_qtyused}
                            {lineCost !== null && ` ($${lineCost})`}
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </div>

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

                {order.ro_status !== 'completed' && (
                  <>
                    <div className="add-part">
                      <label>Log hours{hourlyRate != null && ` @ $${hourlyRate}/hr`}:</label>
                      <input
                        type="number"
                        min="0"
                        step="0.25"
                        placeholder="hours"
                        value={hoursInput[order.ro_repairkey] || ''}
                        onChange={e => setHoursInput({ ...hoursInput, [order.ro_repairkey]: e.target.value })}
                      />
                      <button type="button" onClick={() => handleLogHours(order.ro_repairkey)}>
                        Add Hours
                      </button>
                    </div>
                    <div className="add-part">
                      <select
                        value={sel.partkey || ''}
                        onChange={e => updateSelection(order.ro_repairkey, 'partkey', e.target.value)}
                      >
                        <option value="">-- select part --</option>
                        {parts.map(p => (
                          <option key={p.p_partkey} value={p.p_partkey} disabled={p.p_stockqty <= 0}>
                            {p.p_name} (${p.p_unitprice}, stock: {p.p_stockqty})
                          </option>
                        ))}
                      </select>
                      <input
                        type="number"
                        min="1"
                        placeholder="qty"
                        value={sel.qty || ''}
                        onChange={e => updateSelection(order.ro_repairkey, 'qty', e.target.value)}
                      />
                      <button type="button" onClick={() => handleAddPart(order.ro_repairkey)}>
                        Add Part
                      </button>
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}

      {tab === 'inventory' && (
        <div className="tab-panel">
          <h2>Inventory</h2>
          {parts.length === 0 && <p>No parts in inventory.</p>}
          {parts.length > 0 && (
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
          )}
        </div>
      )}
    </div>
  );
}
