from datetime import date
from types import SimpleNamespace as NS

from app.services.analysis import analyze_goal

TODAY = date(2026, 10, 15)  # 14 days after the goal starts


def make_goal(python_minutes, sql_minutes):
    python = NS(
        id=1, name="Python", priority=1, planned_hours=30.0,
        deadline=date(2026, 11, 30),
        sessions=[NS(topic_id=1, minutes=m) for m in python_minutes],
    )
    sql = NS(
        id=2, name="SQL", priority=2, planned_hours=20.0,
        deadline=date(2026, 11, 15),
        sessions=[NS(topic_id=2, minutes=m) for m in sql_minutes],
    )
    return NS(
        id=1, title="Data Science",
        start_date=date(2026, 10, 1), target_date=date(2026, 12, 31),
        topics=[python, sql],
    )


def test_not_enough_data_with_fewer_than_3_sessions():
    result = analyze_goal(make_goal([60], [60]), TODAY)
    assert result["overall"]["status"] == "not_enough_data"
    assert "Not enough data" in result["insights"][0]


def test_detects_behind_topic_and_gap_insight():
    result = analyze_goal(make_goal([240, 180], [60]), TODAY)
    by_name = {t["name"]: t for t in result["topics"]}
    assert by_name["Python"]["expected_hours"] == 7.0
    assert by_name["Python"]["status"] == "on_track"
    assert by_name["SQL"]["status"] == "behind"
    assert any("SQL" in i and "planned 40%" in i for i in result["insights"])


def test_goal_without_topics():
    goal = NS(
        id=1, title="Empty",
        start_date=date(2026, 10, 1), target_date=date(2026, 12, 31), topics=[],
    )
    result = analyze_goal(goal, TODAY)
    assert result["topics"] == []
    assert result["overall"]["status"] == "not_enough_data"