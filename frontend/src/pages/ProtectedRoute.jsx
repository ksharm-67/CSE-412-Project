import { createContext, useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext.jsx";

const ProtectedRoute = ({ role, children }) => {
  const { user } = useContext(AuthContext)

  if(!user) return <Navigate to="/login" />;
  if(user.role !== role) return <Navigate to="/login" />;
  else return children;
}

export default ProtectedRoute;