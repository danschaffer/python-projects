"""Data models for the soccer module."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict

@dataclass
class Match:
    """Represents a soccer match."""
    home_team: str
    away_team: str
    date: datetime
    score_home: int = 0
    score_away: int = 0
    status: str = ''
    competition: str = ''
    venue: Optional[str] = None
    details: List[Dict] = None

    def __post_init__(self):
        if self.details is None:
            self.details = []

@dataclass
class TeamRecord:
    """Represents a team's record in a competition."""
    name: str
    wins: int
    draws: int
    losses: int
    points: int
    goals_for: int = 0
    goals_against: int = 0
    position: int = 0
    
    @property
    def games_played(self) -> int:
        """Calculate total games played."""
        return self.wins + self.draws + self.losses
    
    @property
    def goal_difference(self) -> int:
        """Calculate goal difference."""
        return self.goals_for - self.goals_against
    
    @property
    def record_string(self) -> str:
        """Get record in W-D-L format."""
        return f"{self.wins}-{self.draws}-{self.losses}"

@dataclass
class League:
    """Represents a soccer league."""
    id: str
    name: str
    country: str
    teams: List[TeamRecord]
    matches: List[Match]
    season_year: Optional[int] = None
    
    def get_standings(self) -> List[TeamRecord]:
        """Get current league standings."""
        return sorted(
            self.teams,
            key=lambda x: (x.points, x.goal_difference, x.goals_for),
            reverse=True
        ) 