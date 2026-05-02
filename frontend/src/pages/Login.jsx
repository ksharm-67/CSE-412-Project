import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function Login() {
  const [username, setUsername] = useState('');
  const [role, setRole] = useState('');
  const [techkey, setTechkey] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogin = () => {
    login({ username, role, techkey: parseInt(techkey) });
    navigate('/' + role);
  };

  return (
    <div>
      <div className="logo"><img src="./public/repair-matrix.png" />
      <h1 className="login-heading" >Login</h1>
      </div>
        <div className="login-form">
          <form>
            <label htmlFor="username">Username: &emsp;&emsp;&emsp;</label>
            <input type="text" id="fname" name="fname" onChange={e => setUsername(e.target.value)} />
            <br /><br />
            <label htmlFor="password">Password: &nbsp;&emsp;&emsp;&emsp;</label>
            <input type="password" id="lname" name="lname"></input>            
            <br /><br /><br />
            <label htmlFor="user-type">Customer</label>
            <input type="radio" id="cus" name="type" onChange={() => setRole('customer')} />
            &emsp;&emsp;
            <label htmlFor="user-type">Manager</label>
            <input type="radio" id="mgr" name="type" onChange={() => setRole('manager')} />
            &emsp;&emsp;
            <label htmlFor="user-type">Technician</label>
            <input type="radio" id="tch" name="type" onChange={() => setRole('technician')} />
            <br /><br /><br />
            <input type="button" id="signin" value="Sign In" onClick={handleLogin} />
            {role === 'technician' && (
            <div>
              <label>Technician ID:</label>
              <input type="number" value={techkey} onChange={e => setTechkey(e.target.value)} />
            </div>
            )}
          </form>
        </div>
    </div>
  )
}