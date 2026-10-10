import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../api/client";
import {
  cardClass,
  dangerBtn,
  inputClass,
  labelClass,
  primaryBtn,
} from "../components/ui";
import { todayISO } from "../utils/dates";

export default function Goals() {
  const navigate = useNavigate();
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    title: "",
    description: "",
    start_date: todayISO(),
    target_date: "",
  });

  useEffect(() => {
    api
      .get("/goals")
      .then((res) => setGoals(res.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  const setField = (name) => (e) =>
    setForm((f) => ({ ...f, [name]: e.target.value }));

  const handleCreate = async (e) => {
    e.preventDefault();
    setFormError("");
    setSubmitting(true);
    try {
      const { data } = await api.post("/goals", {
        title: form.title.trim(),
        description: form.description.trim() || null,
        start_date: form.start_date,
        target_date: form.target_date,
      });
      navigate(`/goals/${data.id}`);
    } catch (err) {
      setFormError(getErrorMessage(err));
      setSubmitting(false);
    }
  };

  const handleDelete = async (goal) => {
    if (!window.confirm(`Delete "${goal.title}" and all its topics and sessions?`)) {
      return;
    }
    try {
      await api.delete(`/goals/${goal.id}`);
      setGoals((prev) => prev.filter((g) => g.id !== goal.id));
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div className="grid gap-6 md:grid-cols-3">
      <form onSubmit={handleCreate} className={`${cardClass} space-y-3 md:col-span-1`}>
        <h2 className="text-lg font-semibold text-gray-900">New goal</h2>
        {formError && (
          <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{formError}</p>
        )}
        <div>
          <label className={labelClass}>Title</label>
          <input
            required
            maxLength={200}
            value={form.title}
            onChange={setField("title")}
            className={inputClass}
            placeholder="e.g. Learn Data Science"
          />
        </div>
        <div>
          <label className={labelClass}>Description (optional)</label>
          <textarea
            rows={2}
            value={form.description}
            onChange={setField("description")}
            className={inputClass}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Start date</label>
            <input
              type="date"
              required
              value={form.start_date}
              onChange={setField("start_date")}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Target date</label>
            <input
              type="date"
              required
              min={form.start_date}
              value={form.target_date}
              onChange={setField("target_date")}
              className={inputClass}
            />
          </div>
        </div>
        <button type="submit" disabled={submitting} className={`${primaryBtn} w-full`}>
          {submitting ? "Creating..." : "Create goal"}
        </button>
      </form>

      <div className="space-y-3 md:col-span-2">
        <h2 className="text-lg font-semibold text-gray-900">Your goals</h2>
        {error && (
          <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
        )}
        {loading && <p className="text-gray-500">Loading...</p>}
        {!loading && goals.length === 0 && (
          <p className="text-gray-500">No goals yet. Create your first one.</p>
        )}
        {goals.map((goal) => (
          <div key={goal.id} className={`${cardClass} flex items-start justify-between gap-4`}>
            <Link to={`/goals/${goal.id}`} className="flex-1">
              <h3 className="font-semibold text-green-800 hover:underline">{goal.title}</h3>
              {goal.description && (
                <p className="mt-1 text-sm text-gray-600">{goal.description}</p>
              )}
              <p className="mt-2 text-xs text-gray-500">
                {goal.start_date} → {goal.target_date}
              </p>
            </Link>
            <button onClick={() => handleDelete(goal)} className={dangerBtn}>
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}