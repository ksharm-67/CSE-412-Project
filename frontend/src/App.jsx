import { Routes, Route, createBrowserRouter, Navigate, Outlet, RouterProvider } from "react-router-dom";
import { useContext } from "react";
import ProtectedRoute from "./pages/ProtectedRoute.jsx";
import Login from "./pages/Login.jsx";
import Customer from "./pages/Customer.jsx";
import Technician from "./pages/Technician.jsx";
import Manager from "./pages/Manager.jsx";
import NotFound from "./pages/NotFound.jsx";

const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/login" />,
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/customer',
    element: <ProtectedRoute role="customer"><Customer /></ProtectedRoute>,
  },
  {
    path: '/technician',
    element: <ProtectedRoute role="technician"><Technician /></ProtectedRoute>,
  },
  {
    path: '/manager',
    element: <ProtectedRoute role="manager"><Manager /></ProtectedRoute>,
  },
  {
    path: '*',
    element: <NotFound />
  }
]);

export default function App() {
  return <RouterProvider router={router} />
}