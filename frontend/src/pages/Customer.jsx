import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { createCustomer } from "../api/customers";
import { createOrder } from "../api/orders";
import { createDevice } from '../api/devices.js';
import { getOrder } from '../api/orders.js';

export default function Customer() {
  const { user, logout } = useContext(AuthContext);
  const [step, setStep] = useState(1);
  const [personalInfo, setPersonalInfo] = useState({
    firstName: '', lastName: '', phone: '', email: ''
  });
  const [deviceInfo, setDeviceInfo] = useState({
    device_type: '', brand: '', model: '', serial_number: '', issue: ''
  });
  const [quote, setQuote] = useState(null);
  const [orderKey, setOrderKey] = useState(null);
  const [statusKey, setStatusKey] = useState('');
  const [orderStatus, setOrderStatus] = useState(null);

  const handlePersonalNext = () => {
    if (!personalInfo.firstName || !personalInfo.lastName || !personalInfo.phone || !personalInfo.email) return;
    setStep(2);
  };

  const handleDeviceNext = async () => {
    if (!deviceInfo.device_type || !deviceInfo.brand || !deviceInfo.model || !deviceInfo.issue) return;
    // Fake quote for now until backend confirms quote endpoint
    setQuote(150);
    setStep(3);
  };

  const handleAccept = async () => {
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
      ro_totalcost: quote,
      ro_issuedecription: deviceInfo.issue,
      ro_datestarted: new Date().toISOString().split('T')[0]
    });

    setOrderKey(localOrderKey); // use order key for lookup
    setStep(4);
  } catch (err) {
    console.error(err);
  }
  };

  const handleDecline = () => {
    setStep(1);
    setDeviceInfo({ device_type: '', brand: '', model: '', serial_number: '', issue: '' });
    setQuote(null);
  };

  const handleStatusCheck = async () => {
    try {
      const res = await getOrder(statusKey);
      setOrderStatus(res.data);
    } catch (err) {
      setOrderStatus({ error: 'Order not found' });
    }
  };

  return (
    <div>
      <button id="signout" type="button" onClick={logout}>Sign Out</button>
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
            <button type="button" onClick={handlePersonalNext}>Next</button>
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
            <button type="button" onClick={handleDeviceNext}>Get Quote</button>
          </>
        )}

        {step >= 3 && (
          <>
            <h2>Your Quote</h2>
            <p>Estimated repair cost: <strong>${quote}</strong></p>
            <button type="button" onClick={handleAccept}>Accept</button>
            <button type="button" onClick={handleDecline}>Decline</button>
          </>
        )}

        {step >= 4 && (
          <>
            <h2>Order Placed</h2>
            <p>Your order number is: <strong>{orderKey}</strong></p>
            <p>Save this number to track your repair.</p>
          </>
        )}

        <hr />
        <h2>Check Order Status</h2>
        <input type="text" placeholder="Enter your Order Number" value={statusKey} onChange={e => setStatusKey(e.target.value)} />
        <button type="button" onClick={handleStatusCheck}>Check Status</button>
        {orderStatus && !orderStatus.error && (
          <div>
            <p>Status: <strong>{orderStatus.status}</strong></p>
            <p>Device: {orderStatus.device?.brand} {orderStatus.device?.model}</p>
            <p>Issue: {orderStatus.issuedescription}</p>
            <p>Total Cost: ${orderStatus.totalcost}</p>
          </div>
        )}
        {orderStatus?.error && <p>{orderStatus.error}</p>}

      </div>
    </div>
  );
}