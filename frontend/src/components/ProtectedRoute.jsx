import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/auth-context";

export default function ProtectedRoute() {
  const { user, loading } = useAuth();
  if (loading) return <p className="p-6 text-gray-500">Loading...</p>;
  return user ? <Outlet /> : <Navigate to="/login" replace />;
}