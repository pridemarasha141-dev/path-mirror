from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

MIN_SESSIONS = 3
ON_TRACK = 0.9
SLIGHTLY_BEHIND = 0.6
GAP_THRESHOLD_PCT = 10.0


def pace_status(ratio: float | None) -> str:
    """pace ratio = logged hours / hours expected by today."""
    if ratio is None:
        return "not_started"
    if ratio >= ON_TRACK:
        return "on_track"
    if ratio >= SLIGHTLY_BEHIND:
        return "slightly_behind"
    return "behind"


def _empty_result(goal: Any, days_elapsed: int, days_remaining: int) -> dict:
    return {
        "goal_id": goal.id,
        "goal_title": goal.title,
        "overall": {
            "total_planned_hours": 0.0,
            "total_logged_hours": 0.0,
            "total_expected_hours": 0.0,
            "pace_ratio": None,
            "status": "not_enough_data",
            "progress_pct": 0.0,
            "session_count": 0,
            "days_elapsed": days_elapsed,
            "days_remaining": days_remaining,
        },
        "topics": [],
        "insights": ["Add topics to this goal to see your analysis."],
    }


def _build_insights(topics: list[dict], enough_data: bool) -> list[str]:
    if not enough_data:
        return ["Not enough data yet: log at least 3 study sessions to see insights."]

    insights: list[str] = []
    for t in topics:
        planned, actual = t["planned_share_pct"], t["actual_share_pct"]
        if t["gap_pct"] <= -GAP_THRESHOLD_PCT:
            insights.append(
                f"You planned {planned:.0f}% of your time for {t['name']} "
                f"but logged only {actual:.0f}%."
            )
        elif t["gap_pct"] >= GAP_THRESHOLD_PCT:
            insights.append(
                f"You planned {planned:.0f}% of your time for {t['name']} "
                f"but logged {actual:.0f}%, more than planned."
            )

        if t["expected_hours"] > 0 and t["logged_hours"] == 0:
            insights.append(f"You haven't logged any time on {t['name']} yet.")
        elif t["status"] in ("slightly_behind", "behind"):
            label = "slightly behind" if t["status"] == "slightly_behind" else "behind"
            insights.append(
                f"{t['name']} is {label} schedule: {t['logged_hours']:.1f}h logged "
                f"vs about {t['expected_hours']:.1f}h expected by today."
            )

    if all(t["status"] == "on_track" for t in topics):
        insights.append("You're on track across all topics. Keep it up!")
    elif not insights:
        insights.append("Your time is split close to your plan.")
    return insights


def analyze_goal(goal: Any, today: date | None = None) -> dict:
    today = today or date.today()
    days_elapsed = max((today - goal.start_date).days, 0)
    days_remaining = max((goal.target_date - today).days, 0)

    if not goal.topics:
        return _empty_result(goal, days_elapsed, days_remaining)

    # --- 1. Build DataFrames from the ORM objects ---
    topics_df = pd.DataFrame(
        [
            {
                "topic_id": t.id,
                "name": t.name,
                "priority": t.priority,
                "planned_hours": float(t.planned_hours),
                "deadline": t.deadline,
            }
            for t in goal.topics
        ]
    )
    sessions_df = pd.DataFrame(
        [
            {"topic_id": s.topic_id, "minutes": s.minutes}
            for t in goal.topics
            for s in t.sessions
        ],
        columns=["topic_id", "minutes"],
    )
    sessions_df["minutes"] = sessions_df["minutes"].astype(float)
    session_count = len(sessions_df)
    enough_data = session_count >= MIN_SESSIONS

    # --- 2. Logged hours per topic ---
    logged = sessions_df.groupby("topic_id")["minutes"].sum() / 60
    topics_df["logged_hours"] = (
        topics_df["topic_id"].map(logged).fillna(0.0).astype(float)
    )

    # --- 3. Expected hours by today (linear plan from goal start to topic deadline) ---
    total_days = topics_df["deadline"].apply(
        lambda d: max((d - goal.start_date).days, 1)
    )
    topics_df["expected_hours"] = (
        topics_df["planned_hours"] * days_elapsed / total_days
    ).clip(upper=topics_df["planned_hours"])
    topics_df["time_elapsed_pct"] = (days_elapsed / total_days * 100).clip(upper=100)

    # --- 4. Planned vs actual share of effort ---
    total_planned = topics_df["planned_hours"].sum()
    total_logged = topics_df["logged_hours"].sum()
    total_expected = topics_df["expected_hours"].sum()

    topics_df["planned_share_pct"] = topics_df["planned_hours"] / total_planned * 100
    if total_logged > 0:
        topics_df["actual_share_pct"] = topics_df["logged_hours"] / total_logged * 100
    else:
        topics_df["actual_share_pct"] = 0.0
    topics_df["gap_pct"] = topics_df["actual_share_pct"] - topics_df["planned_share_pct"]
    topics_df["progress_pct"] = topics_df["logged_hours"] / topics_df["planned_hours"] * 100

    # --- 5. Pace ratio and status per topic ---
    topics: list[dict] = []
    for row in topics_df.itertuples(index=False):
        ratio = row.logged_hours / row.expected_hours if row.expected_hours > 0 else None
        topics.append(
            {
                "topic_id": int(row.topic_id),
                "name": row.name,
                "priority": int(row.priority),
                "deadline": row.deadline,
                "planned_hours": round(float(row.planned_hours), 2),
                "logged_hours": round(float(row.logged_hours), 2),
                "expected_hours": round(float(row.expected_hours), 2),
                "planned_share_pct": round(float(row.planned_share_pct), 1),
                "actual_share_pct": round(float(row.actual_share_pct), 1),
                "gap_pct": round(float(row.gap_pct), 1),
                "pace_ratio": round(float(ratio), 2) if ratio is not None else None,
                "status": pace_status(ratio) if enough_data else "not_enough_data",
                "progress_pct": round(float(row.progress_pct), 1),
                "time_elapsed_pct": round(float(row.time_elapsed_pct), 1),
            }
        )

    # --- 6. Overall summary ---
    overall_ratio = total_logged / total_expected if total_expected > 0 else None
    overall = {
        "total_planned_hours": round(float(total_planned), 2),
        "total_logged_hours": round(float(total_logged), 2),
        "total_expected_hours": round(float(total_expected), 2),
        "pace_ratio": round(float(overall_ratio), 2) if overall_ratio is not None else None,
        "status": pace_status(overall_ratio) if enough_data else "not_enough_data",
        "progress_pct": round(float(total_logged / total_planned * 100), 1),
        "session_count": session_count,
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
    }

    return {
        "goal_id": goal.id,
        "goal_title": goal.title,
        "overall": overall,
        "topics": topics,
        "insights": _build_insights(topics, enough_data),
    }