import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { createCustomer } from "../api/customers";
import { createOrder } from "../api/orders";
import { createDevice, getDevice } from '../api/devices.js';
import { getOrder } from '../api/orders.js';

export default function Customer() {
  const { user, logout } = useContext(AuthContext);
  const [tab, setTab] = useState('new');
  const [step, setStep] = useState(1);
  const [personalInfo, setPersonalInfo] = useState({
    firstName: '', lastName: '', phone: '', email: ''
  });
  const [deviceInfo, setDeviceInfo] = useState({
    device_type: '', brand: '', model: '', serial_number: '', issue: ''
  });
  const [orderKey, setOrderKey] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [statusKey, setStatusKey] = useState('');
  const [orderStatus, setOrderStatus] = useState(null);

  const handlePersonalNext = () => {
    if (!personalInfo.firstName || !personalInfo.lastName || !personalInfo.phone || !personalInfo.email) return;
    setStep(2);
  };

  const handleSubmitOrder = async () => {
    if (!deviceInfo.device_type || !deviceInfo.brand || !deviceInfo.model || !deviceInfo.issue) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      const deviceKey = Math.floor(Math.random() * 900000) + 100000;
      const repairKey = Math.floor(Math.random() * 900000) + 100000;
      const localOrderKey = Math.floor(Math.random() * 900000) + 100000;

      const customerRes = await createCustomer({
        c_custkey: Math.floor(Math.random() * 900000) + 100000,
        c_name: personalInfo.firstName + ' ' + personalInfo.lastName,
        c_phone: personalInfo.phone,
        c_email: personalInfo.email
      });

      const custKey = customerRes.data.c_custkey;

      await createDevice({
        d_devicekey: deviceKey,
        d_custkey: custKey,
        d_brand: deviceInfo.brand,
        d_model: deviceInfo.model,
        d_devicetype: deviceInfo.device_type,
        d_serialnum: deviceInfo.serial_number
      });

      await createOrder({
        ro_repairkey: repairKey,
        ro_orderkey: localOrderKey,
        ro_custkey: custKey,
        ro_devicekey: deviceKey,
        ro_totalcost: 0,
        ro_issuedecription: deviceInfo.issue,
        ro_datestarted: new Date().toISOString().split('T')[0]
      });

      setOrderKey(repairKey);
      setStep(3);
    } catch (err) {
      console.error(err);
      setSubmitError('Failed to submit repair request. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleStatusCheck = async () => {
    try {
      const res = await getOrder(statusKey);
      const deviceRes = await getDevice(res.data.ro_devicekey);
      setOrderStatus({ ...res.data, device: deviceRes.data });
    } catch (err) {
      setOrderStatus({ error: 'Order not found' });
    }
  };

  const renderCost = (cost) => {
    const numeric = Number(cost);
    if (!numeric) return <em>Pending — your technician is preparing a quote.</em>;
    return `$${numeric}`;
  };

  return (
    <div className="cust-dashboard">
      <div className="dashboard-header">
        <h1>Customer Portal</h1>
        <button id="signout" type="button" onClick={logout}>Sign Out</button>
      </div>

      <div className="tabs">
        <button
          type="button"
          className={`tab ${tab === 'new' ? 'active' : ''}`}
          onClick={() => setTab('new')}
        >
          New Repair Order
        </button>
        <button
          type="button"
          className={`tab ${tab === 'status' ? 'active' : ''}`}
          onClick={() => setTab('status')}
        >
          Check Status
        </button>
      </div>

      {tab === 'new' && (
        <div className="tab-panel">
          <div className="cust-form">
            {step >= 1 && (
              <>
                <h2>Personal Information</h2>
                <form>
                  <label>First name:</label>
                  <input type="text" value={personalInfo.firstName} onChange={e => setPersonalInfo({...personalInfo, firstName: e.target.value})} />
                  <label>Last name:</label>
                  <input type="text" value={personalInfo.lastName} onChange={e => setPersonalInfo({...personalInfo, lastName: e.target.value})} />
                  <label>Phone:</label>
                  <input type="text" value={personalInfo.phone} onChange={e => setPersonalInfo({...personalInfo, phone: e.target.value})} />
                  <label>E-mail:</label>
                  <input type="text" value={personalInfo.email} onChange={e => setPersonalInfo({...personalInfo, email: e.target.value})} />
                </form>
                {step === 1 && <button type="button" onClick={handlePersonalNext}>Next</button>}
              </>
            )}

            {step >= 2 && (
              <>
                <h2>Device Information</h2>
                <form>
                  <label>Device type:</label>
                  <input type="text" value={deviceInfo.device_type} onChange={e => setDeviceInfo({...deviceInfo, device_type: e.target.value})} />
                  <label>Brand:</label>
                  <input type="text" value={deviceInfo.brand} onChange={e => setDeviceInfo({...deviceInfo, brand: e.target.value})} />
                  <label>Model:</label>
                  <input type="text" value={deviceInfo.model} onChange={e => setDeviceInfo({...deviceInfo, model: e.target.value})} />
                  <label>Serial Number:</label>
                  <input type="text" value={deviceInfo.serial_number} onChange={e => setDeviceInfo({...deviceInfo, serial_number: e.target.value})} />
                  <label>Describe issue:</label>
                  <textarea rows="5" value={deviceInfo.issue} onChange={e => setDeviceInfo({...deviceInfo, issue: e.target.value})}></textarea>
                </form>
                {step === 2 && (
                  <>
                    <button type="button" onClick={handleSubmitOrder} disabled={submitting}>
                      {submitting ? 'Submitting...' : 'Submit Repair Request'}
                    </button>
                    {submitError && <p className="error">{submitError}</p>}
                  </>
                )}
              </>
            )}

            {step >= 3 && (
              <>
                <h2>Repair Request Received</h2>
                <p>Thanks! A technician will review your device and provide a quote soon. You can check back here using your order number to see the latest status and price.</p>
                <p>Your order number is: <strong>{orderKey}</strong></p>
                <p>Save this number to track your repair.</p>
              </>
            )}
          </div>
        </div>
      )}

      {tab === 'status' && (
        <div className="tab-panel">
          <h2>Check Order Status</h2>
          <input type="text" placeholder="Enter your Order Number" value={statusKey} onChange={e => setStatusKey(e.target.value)} />
          <button type="button" onClick={handleStatusCheck}>Check Status</button>
          {orderStatus && !orderStatus.error && (
            <div className="order-card" style={{ marginTop: '1rem' }}>
              <p>Status: <strong>{orderStatus.ro_status}</strong></p>
              <p>Device: {orderStatus.device?.d_brand} {orderStatus.device?.d_model}</p>
              <p>Issue: {orderStatus.ro_issuedecription}</p>
              <p>Total Cost: {renderCost(orderStatus.ro_totalcost)}</p>
            </div>
          )}
          {orderStatus?.error && <p className="error">{orderStatus.error}</p>}
        </div>
      )}
    </div>
  );
}
