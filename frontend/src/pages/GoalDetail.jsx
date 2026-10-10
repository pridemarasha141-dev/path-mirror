import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api, { getErrorMessage } from "../api/client";
import {
  cardClass,
  dangerBtn,
  inputClass,
  labelClass,
  primaryBtn,
} from "../components/ui";
import { todayISO } from "../utils/dates";

const PRIORITY_LABELS = { 1: "High", 2: "Medium", 3: "Low" };
const toHours = (minutes) => (minutes / 60).toFixed(1);
const emptyTopic = { name: "", priority: "2", planned_hours: "", deadline: "" };

export default function GoalDetail() {
  const { goalId } = useParams();
  const [goal, setGoal] = useState(null);
  const [topics, setTopics] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [topicForm, setTopicForm] = useState(emptyTopic);
  const [topicError, setTopicError] = useState("");
  const [sessionForm, setSessionForm] = useState({
    topic_id: "",
    session_date: todayISO(),
    minutes: "",
    note: "",
  });
  const [sessionError, setSessionError] = useState("");

  const loadAll = useCallback(async () => {
    try {
      const [g, t, s] = await Promise.all([
        api.get(`/goals/${goalId}`),
        api.get(`/goals/${goalId}/topics`),
        api.get(`/goals/${goalId}/sessions`),
      ]);
      setGoal(g.data);
      setTopics(t.data);
      setSessions(s.data);
      setError("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [goalId]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const loggedByTopic = useMemo(() => {
    const totals = {};
    sessions.forEach((s) => {
      totals[s.topic_id] = (totals[s.topic_id] || 0) + s.minutes;
    });
    return totals;
  }, [sessions]);

  const topicNames = useMemo(
    () => Object.fromEntries(topics.map((t) => [t.id, t.name])),
    [topics]
  );

  const selectedTopicId = sessionForm.topic_id || String(topics[0]?.id ?? "");

  const addTopic = async (e) => {
    e.preventDefault();
    setTopicError("");
    try {
      await api.post(`/goals/${goalId}/topics`, {
        name: topicForm.name.trim(),
        priority: Number(topicForm.priority),
        planned_hours: Number(topicForm.planned_hours),
        deadline: topicForm.deadline,
      });
      setTopicForm(emptyTopic);
      await loadAll();
    } catch (err) {
      setTopicError(getErrorMessage(err));
    }
  };

  const removeTopic = async (topic) => {
    if (!window.confirm(`Delete "${topic.name}" and its logged sessions?`)) return;
    try {
      await api.delete(`/topics/${topic.id}`);
      await loadAll();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const logSession = async (e) => {
    e.preventDefault();
    setSessionError("");
    try {
      await api.post(`/topics/${selectedTopicId}/sessions`, {
        session_date: sessionForm.session_date,
        minutes: Number(sessionForm.minutes),
        note: sessionForm.note.trim() || null,
      });
      setSessionForm((f) => ({ ...f, minutes: "", note: "" }));
      await loadAll();
    } catch (err) {
      setSessionError(getErrorMessage(err));
    }
  };

  const removeSession = async (session) => {
    try {
      await api.delete(`/sessions/${session.id}`);
      await loadAll();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  if (loading) return <p className="text-gray-500">Loading...</p>;
  if (!goal) {
    return (
      <div>
        <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
        <Link to="/goals" className="mt-3 inline-block text-green-700 hover:underline">
          ← Back to goals
        </Link>
      </div>
    );
  }

  const setTopicField = (name) => (e) =>
    setTopicForm((f) => ({ ...f, [name]: e.target.value }));
  const setSessionField = (name) => (e) =>
    setSessionForm((f) => ({ ...f, [name]: e.target.value }));

  return (
    <div className="space-y-6">
      <div>
        <Link to="/goals" className="text-sm text-green-700 hover:underline">
          ← Back to goals
        </Link>
        <h1 className="mt-2 text-2xl font-bold text-gray-900">{goal.title}</h1>
        {goal.description && <p className="mt-1 text-gray-600">{goal.description}</p>}
        <p className="mt-1 text-sm text-gray-500">
          {goal.start_date} → {goal.target_date}
        </p>
        {error && (
          <p className="mt-3 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
        )}
      </div>

      {/* Topics */}
      <section className={`${cardClass} space-y-4`}>
        <h2 className="text-lg font-semibold text-gray-900">Topics</h2>

        {topics.length === 0 ? (
          <p className="text-gray-500">No topics yet. Add your first one below.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-gray-200 text-gray-500">
                <tr>
                  <th className="py-2 pr-4">Topic</th>
                  <th className="py-2 pr-4">Priority</th>
                  <th className="py-2 pr-4">Planned (h)</th>
                  <th className="py-2 pr-4">Logged (h)</th>
                  <th className="py-2 pr-4">Deadline</th>
                  <th className="py-2" />
                </tr>
              </thead>
              <tbody>
                {topics.map((t) => (
                  <tr key={t.id} className="border-b border-gray-100">
                    <td className="py-2 pr-4 font-medium text-gray-900">{t.name}</td>
                    <td className="py-2 pr-4">{PRIORITY_LABELS[t.priority]}</td>
                    <td className="py-2 pr-4">{t.planned_hours}</td>
                    <td className="py-2 pr-4">{toHours(loggedByTopic[t.id] || 0)}</td>
                    <td className="py-2 pr-4">{t.deadline}</td>
                    <td className="py-2 text-right">
                      <button onClick={() => removeTopic(t)} className={dangerBtn}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <form onSubmit={addTopic} className="space-y-3 border-t border-gray-100 pt-4">
          <h3 className="text-sm font-semibold text-gray-700">Add a topic</h3>
          {topicError && (
            <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{topicError}</p>
          )}
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <label className={labelClass}>Name</label>
              <input
                required
                maxLength={200}
                value={topicForm.name}
                onChange={setTopicField("name")}
                className={inputClass}
                placeholder="e.g. Python"
              />
            </div>
            <div>
              <label className={labelClass}>Priority</label>
              <select
                value={topicForm.priority}
                onChange={setTopicField("priority")}
                className={inputClass}
              >
                <option value="1">High</option>
                <option value="2">Medium</option>
                <option value="3">Low</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Planned hours</label>
              <input
                type="number"
                required
                min="0.1"
                step="any"
                value={topicForm.planned_hours}
                onChange={setTopicField("planned_hours")}
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Deadline</label>
              <input
                type="date"
                required
                min={goal.start_date}
                value={topicForm.deadline}
                onChange={setTopicField("deadline")}
                className={inputClass}
              />
            </div>
          </div>
          <button type="submit" className={primaryBtn}>
            Add topic
          </button>
        </form>
      </section>

      {/* Log a session */}
      <section className={`${cardClass} space-y-3`}>
        <h2 className="text-lg font-semibold text-gray-900">Log a study session</h2>
        {topics.length === 0 ? (
          <p className="text-gray-500">Add a topic first, then you can log sessions.</p>
        ) : (
          <form onSubmit={logSession} className="space-y-3">
            {sessionError && (
              <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
                {sessionError}
              </p>
            )}
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <label className={labelClass}>Topic</label>
                <select
                  value={selectedTopicId}
                  onChange={setSessionField("topic_id")}
                  className={inputClass}
                >
                  {topics.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className={labelClass}>Date</label>
                <input
                  type="date"
                  required
                  max={todayISO()}
                  value={sessionForm.session_date}
                  onChange={setSessionField("session_date")}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Minutes</label>
                <input
                  type="number"
                  required
                  min="1"
                  max="1440"
                  step="1"
                  value={sessionForm.minutes}
                  onChange={setSessionField("minutes")}
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Note (optional)</label>
                <input
                  maxLength={500}
                  value={sessionForm.note}
                  onChange={setSessionField("note")}
                  className={inputClass}
                />
              </div>
            </div>
            <button type="submit" className={primaryBtn}>
              Log session
            </button>
          </form>
        )}
      </section>

      {/* History */}
      <section className={`${cardClass} space-y-3`}>
        <h2 className="text-lg font-semibold text-gray-900">Session history</h2>
        {sessions.length === 0 ? (
          <p className="text-gray-500">No sessions logged yet.</p>
        ) : (
          <ul className="divide-y divide-gray-100">
            {sessions.map((s) => (
              <li key={s.id} className="flex items-center justify-between gap-4 py-2 text-sm">
                <div>
                  <span className="font-medium text-gray-900">{topicNames[s.topic_id]}</span>
                  <span className="ml-2 text-gray-500">
                    {s.session_date} · {s.minutes} min
                  </span>
                  {s.note && <p className="text-gray-600">{s.note}</p>}
                </div>
                <button onClick={() => removeSession(s)} className={dangerBtn}>
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}