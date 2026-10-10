import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/auth-context";

const linkClass = ({ isActive }) =>
  `rounded-md px-3 py-2 text-sm font-medium ${
    isActive ? "bg-green-100 text-green-800" : "text-gray-600 hover:text-gray-900"
  }`;

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <span className="text-lg font-bold text-green-700">Path Mirror</span>
            <nav className="flex gap-1">
              <NavLink to="/" end className={linkClass}>
                Dashboard
              </NavLink>
              <NavLink to="/goals" className={linkClass}>
                Goals
              </NavLink>
            </nav>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-gray-600">{user?.name}</span>
            <button
              onClick={handleLogout}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-gray-700 hover:bg-gray-100"
            >
              Log out
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}