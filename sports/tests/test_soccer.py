"""Tests for the soccer module."""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from soccer.models import Match, TeamRecord, League
from soccer.utils import format_datetime, to_local_time, validate_league_id, format_score

def test_match_creation():
    """Test Match class creation and defaults."""
    match = Match(
        home_team="Arsenal",
        away_team="Chelsea",
        date=datetime.now()
    )
    assert match.home_team == "Arsenal"
    assert match.away_team == "Chelsea"
    assert match.score_home == 0
    assert match.score_away == 0
    assert match.details == []

def test_team_record_properties():
    """Test TeamRecord class properties."""
    record = TeamRecord(
        name="Arsenal",
        wins=10,
        draws=5,
        losses=3,
        points=35,
        goals_for=30,
        goals_against=15
    )
    assert record.games_played == 18
    assert record.goal_difference == 15
    assert record.record_string == "10-5-3"

def test_league_standings():
    """Test League standings sorting."""
    teams = [
        TeamRecord("Team A", 10, 2, 3, 32, 25, 15),
        TeamRecord("Team B", 10, 2, 3, 32, 30, 15),
        TeamRecord("Team C", 9, 2, 4, 29, 20, 15)
    ]
    league = League(
        id="test.1",
        name="Test League",
        country="Test",
        teams=teams,
        matches=[]
    )
    standings = league.get_standings()
    assert standings[0].name == "Team B"  # Higher goal difference
    assert standings[1].name == "Team A"
    assert standings[2].name == "Team C"

def test_format_datetime():
    """Test datetime formatting."""
    dt = datetime(2024, 3, 15, 12, 30)
    formatted = format_datetime(dt, "%Y-%m-%d %H:%M")
    assert formatted == "2024-03-15 12:30"

@patch('tzlocal.get_localzone')
def test_to_local_time(mock_get_localzone):
    """Test UTC to local time conversion."""
    mock_timezone = MagicMock()
    mock_get_localzone.return_value = mock_timezone
    utc_time = "2024-03-15T12:30Z"
    local_time = to_local_time(utc_time)
    assert isinstance(local_time, datetime)

def test_validate_league_id():
    """Test league ID validation."""
    assert validate_league_id("eng.1") is True
    assert validate_league_id("eng") is False
    assert validate_league_id("eng.abc") is False

def test_format_score():
    """Test score formatting."""
    assert format_score(2) == "2"
    assert format_score(2, 5) == "2 (5)" 