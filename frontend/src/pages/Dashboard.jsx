import { useAuth } from "../context/auth-context";

export default function Dashboard() {
  const { user } = useAuth();
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Welcome, {user?.name}</h1>
      <p className="mt-2 text-gray-600">Your dashboard will appear here.</p>
    </div>
  );
}