"""Soccer client for fetching and displaying soccer data."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import requests
from tqdm import tqdm
import re
import json
import csv
import sys

from .config import (
    API_CONFIG,
    LEAGUE_SIZE,
    LEAGUE_NAMES,
    POINTS,
    DATE_FORMAT,
    LEAGUE_CONFIG,
    DEFAULT_LEAGUE_CONFIG,
    TEAM_NAME_MAPPING
)
from .models import Match, TeamRecord, League
from .utils import (
    to_local_time,
    format_datetime,
    cached_api_call,
    to_json,
    to_csv,
    format_score,
    to_markdown
)

logger = logging.getLogger(__name__)

class SoccerClient:
    """Client for interacting with soccer data API."""
    
    def __init__(self, league: str = 'eng.1', team: Optional[str] = None):
        """Initialize soccer client.
        
        Args:
            league: League identifier
            team: Team name to filter results
        """
        self.league = league
        self.team = team.lower().replace('_', ' ').split(',') if team else None
        self._session = requests.Session()
        self._session.headers.update(API_CONFIG['HEADERS'])
        
        # Initialize team cities
        from .cities import CITY_DATA
        self.team_cities = CITY_DATA.get(self.league, {})
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with error handling and timeout."""
        try:
            endpoint = endpoint.replace(':', '')
            # Special handling for standings endpoint
            if endpoint == 'leagues/standings':
                url = f"{API_CONFIG['BASE_URL'].replace('site/v2', 'v2')}/{self.league}/standings"
            else:
                url = f"{API_CONFIG['BASE_URL']}/{endpoint}"
            
            logger.debug(f"Making request to: {url}")
            response = self._session.get(
                url,
                params=params,
                timeout=API_CONFIG['TIMEOUT']
            )
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response data: {data}")
            return data
        except requests.Timeout:
            logger.error(f"Timeout fetching data from {endpoint}")
            return {}
        except requests.RequestException as e:
            logger.error(f"Error fetching data from {endpoint}: {str(e)}")
            return {}
    
    @cached_api_call
    def get_matches(self, days: int) -> List[Match]:
        """Get matches for specified day offset."""
        date = datetime.now() + timedelta(days=days)
        params = {
            'league': self.league,
            'dates': date.strftime(DATE_FORMAT['API'])
        }
        
        data = self._make_request('leagues/scoreboard', params)
        matches = []
        
        if 'events' not in data:
            logger.debug(f"No events found in response: {data}")
            return matches
            
        for event in data['events']:
            try:
                match = self._parse_match(event)
                if self._should_include_match(match):
                    matches.append(match)
            except Exception as e:
                logger.error(f"Error parsing match: {str(e)}")
                continue
                
        return matches
    
    def _parse_match(self, event: Dict) -> Match:
        """Parse match data from API response."""
        competition = event['competitions'][0]
        home_team = away_team = None
        
        for competitor in competition['competitors']:
            team_name = competitor['team']['name']
            # Apply team name mapping if available
            if self.league in TEAM_NAME_MAPPING:
                team_name = TEAM_NAME_MAPPING[self.league].get(team_name, team_name)
            
            # Handle special cases for team names
            if team_name == "1. FC Union Berlin":
                team_name = "Union Berlin"
            elif team_name == "1. FC Köln":
                team_name = "FC Köln"
            elif team_name == "1. FC Heidenheim 1846":
                team_name = "FC Heidenheim"
            elif team_name == "1. FC Magdeburg":
                team_name = "FC Magdeburg"
            elif team_name == "1. FC Nürnberg":
                team_name = "FC Nürnberg"
            elif team_name == "Borussia Monchengladbach":
                team_name = "Borussia Mönchengladbach"
            elif team_name == "Mainz":
                team_name = "FSV Mainz 05"
            elif team_name == "FC Cologne":
                team_name = "FC Köln"
            elif team_name == "Hamburg SV":
                team_name = "Hamburger SV"
            elif team_name == "Hertha Berlin":
                team_name = "Hertha BSC"
            elif team_name == "SpVgg Greuther Furth":
                team_name = "Greuther Fürth"
            elif team_name == "TSV Eintracht Braunschweig":
                team_name = "Eintracht Braunschweig"
            # Strip out "1." from team names for German leagues
            elif self.league in ['ger.1', 'ger.2']:
                team_name = re.sub(r'^1\.\s*', '', team_name)
            
            team_data = {
                'name': team_name,
                'score': int(competitor.get('score', 0)),
                'shootout_score': int(competitor.get('shootoutScore', 0)) if 'shootoutScore' in competitor else None
            }
            
            if competitor['homeAway'] == 'home':
                home_team = team_data
            else:
                away_team = team_data
        
        return Match(
            home_team=home_team['name'],
            away_team=away_team['name'],
            date=to_local_time(event['date']),
            score_home=home_team['score'],
            score_away=away_team['score'],
            status=event['status']['type']['state'],
            competition=self.league,
            details=competition.get('details', [])
        )
    
    def _should_include_match(self, match: Match) -> bool:
        """Check if match should be included based on team filter."""
        if not self.team:
            return True
        return any(
            team_name in match.home_team.lower() or team_name in match.away_team.lower()
            for team_name in self.team
        )
    
    def get_standings(self) -> List[TeamRecord]:
        """Get current standings for the league."""
        data = self._make_request('leagues/standings')
        standings = []
        
        try:
            if not data or 'children' not in data:
                logger.debug(f"No standings found in response: {data}")
                return standings

            # Get the first season's standings
            season_data = data['children'][0]
            if 'standings' not in season_data:
                logger.debug(f"No standings found in season data: {season_data}")
                return standings

            standings_data = season_data['standings']
            if not standings_data.get('entries'):
                logger.debug(f"No entries found in standings data: {standings_data}")
                return standings

            for team_entry in standings_data['entries']:
                try:
                    team = team_entry['team']
                    stats = {}
                    for stat in team_entry['stats']:
                        if 'value' in stat:
                            try:
                                stats[stat['name']] = int(stat['value'])
                            except (ValueError, TypeError):
                                logger.debug(f"Could not convert stat value to int: {stat}")
                                stats[stat['name']] = 0
                    
                    team_record = TeamRecord(
                        name=team['displayName'],
                        wins=stats.get('wins', 0),
                        draws=stats.get('ties', 0),
                        losses=stats.get('losses', 0),
                        points=stats.get('points', 0),
                        goals_for=stats.get('pointsFor', 0),
                        goals_against=stats.get('pointsAgainst', 0)
                    )
                    standings.append(team_record)
                except Exception as e:
                    logger.error(f"Error parsing team record: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing standings data: {str(e)}")
            logger.debug(f"Raw data: {data}")
        
        return sorted(
            standings,
            key=lambda x: (x.points, x.goal_difference, x.goals_for),
            reverse=True
        )
    
    def _should_include_team(self, team: TeamRecord) -> bool:
        """Check if team should be included based on team filter."""
        if not self.team:
            return True
        return any(team_name in team.name.lower() for team_name in self.team)
    
    def display_matches(self, start: int, end: int, format: str = 'text', show_city: bool = False) -> None:
        """Display matches within date range."""
        matches = []
        for days in range(start, end + 1):
            matches.extend(self.get_matches(days))
        
        if not matches:
            print(f"No matches found for {LEAGUE_NAMES.get(self.league, self.league)}")
            return
            
        if format == 'json':
            print(to_json(matches))
        elif format == 'csv':
            to_csv([match.__dict__ for match in matches], 'matches.csv')
        elif format == 'md':
            print(to_markdown(
                matches,
                f"{LEAGUE_NAMES.get(self.league, self.league)} Fixtures",
                show_city=show_city,
                city_data=self.team_cities
            ))
        else:
            current_date = None
            for match in matches:
                match_date = match.date.strftime(DATE_FORMAT['DISPLAY'])
                if match_date != current_date:
                    print(f"\n{match_date}")
                    current_date = match_date
                
                time_str = match.date.strftime(DATE_FORMAT['TIME'])
                score_str = (
                    f"{format_score(match.score_home)} - {format_score(match.score_away)}"
                    if match.status != 'pre'
                    else time_str
                )
                print(f"{match.home_team} vs {match.away_team} {score_str}")
    
    def display_standings(self, format: str = 'text', show_city: bool = False) -> None:
        """Display current standings."""
        logger.debug(f"Fetching standings for league: {self.league}")
        standings = self.get_standings()
        
        if not standings:
            logger.debug("No standings available")
            print(f"No standings available for {LEAGUE_NAMES.get(self.league, self.league)}")
            return

        # Check if league is on break by looking at upcoming matches
        next_matches = []
        found_matches = False
        logger.debug("Looking for upcoming matches")
        for days in range(0, 90):  # Look ahead 90 days instead of 30 to catch season starts
            matches = self.get_matches(days)
            logger.debug(f"Day {days}: Found {len(matches)} matches")
            if matches:
                found_matches = True
                next_matches.extend(matches)
                if len(next_matches) >= 2:  # Found enough matches to determine if league is active
                    break

        if found_matches and next_matches:
            next_match_date = min(match.date for match in next_matches)
            current_time = datetime.now(next_match_date.tzinfo)
            days_until_next = (next_match_date - current_time).days
            logger.debug(f"Days until next match: {days_until_next}")
            if days_until_next > 7:  # If no matches for over a week, consider it a break
                print(f"\n{LEAGUE_NAMES.get(self.league, self.league)} is currently on break")
                print(f"League resumes on {next_match_date.strftime(DATE_FORMAT['DISPLAY'])}")
        elif not found_matches:
            logger.debug("No matches found in the next 90 days")
            print(f"\n{LEAGUE_NAMES.get(self.league, self.league)} season has not started yet")
            print("Check back later for the season start date")
        
        if format == 'json':
            print(to_json(standings))
        elif format == 'csv':
            to_csv([team.__dict__ for team in standings], 'standings.csv')
        elif format == 'md':
            print(to_markdown(
                standings,
                f"{LEAGUE_NAMES.get(self.league, self.league)} Standings",
                show_city=show_city,
                city_data=self.team_cities
            ))
        else:
            # Get league configuration
            league_config = LEAGUE_CONFIG.get(self.league, DEFAULT_LEAGUE_CONFIG)
            
            print(f"\n{LEAGUE_NAMES.get(self.league, self.league)} Standings")
            # Header with abbreviations
            print("Pos = Position, MP = Matches Played, W = Wins, D = Draws, L = Losses")
            print("GF = Goals For, GA = Goals Against, GD = Goal Difference, Pts = Points")
            
            # Adjust header width if showing city
            team_header = "Team"
            team_width = 28  # Base width for team name
            if show_city:
                team_header = "Team (City)"
                team_width = 48  # Increased width for team name with city
            
            # Print header with consistent width
            print(f"{'Pos':>3} {team_header:<{team_width}} {'MP':>3} {'W':>3} {'D':>3} {'L':>3} {'GF':>3} {'GA':>3} {'GD':>4} {'Pts':>3}")
            print("-" * (team_width + 45))  # Adjust line length based on team width
            
            # ANSI color codes
            GREEN = "\033[92m"
            RED = "\033[91m"
            RESET = "\033[0m"
            
            total_teams = len(standings)
            for pos, team in enumerate(standings, 1):
                # Determine team's status for coloring
                status = ""
                color = ""
                
                if self.league == 'usa.1':
                    if pos <= league_config.get('tournament', 0):
                        status = "* "  # MLS Cup Playoffs
                        color = GREEN
                else:
                    if pos <= league_config.get('champions_league', 0):
                        status = "* "  # Champions League
                        color = GREEN
                    elif pos <= league_config.get('champions_league', 0) + league_config.get('europa_league', 0):
                        status = "† "  # Europa League
                        color = GREEN
                    elif pos <= league_config.get('champions_league', 0) + league_config.get('europa_league', 0) + league_config.get('europa_conference', 0):
                        status = "‡ "  # Europa Conference League
                        color = GREEN
                    # Add promotion spots
                    elif league_config.get('promotion', 0) > 0 and pos <= league_config.get('promotion', 0):
                        status = "↑ "  # Automatic promotion
                        color = GREEN
                    elif league_config.get('promotion_playoff', 0) > 0 and pos <= league_config.get('promotion', 0) + league_config.get('promotion_playoff', 0):
                        status = "⚡"  # Promotion playoff (no space)
                        color = GREEN
                    elif total_teams - pos < league_config.get('relegation_zone', 0):
                        status = "↓ "  # Relegation
                        color = RED
                    elif league_config.get('relegation_playoff') and total_teams - pos == league_config.get('relegation_zone', 0):
                        status = "⚠ "  # Relegation playoff
                        color = RED
                
                # Calculate padding needed for consistent alignment
                team_width = 28
                city = ""  # Initialize city variable
                
                if show_city:
                    team_width = 48  # 40 - status_width for city display
                    # First remove any parentheses and their contents from team name
                    base_name = re.sub(r'\s*\([^)]*\)', '', team.name).strip()
                    # Normalize team name to match CITY_DATA keys
                    normalized_name = self._normalize_team_name(base_name)
                    team_display = f"{base_name} ({city})" if city else base_name
                else:
                    base_name = re.sub(r'\s*\([^)]*\)', '', team.name).strip()
                    # Handle special cases for team names
                    if base_name == "1. FC Union Berlin":
                        base_name = "Union Berlin"
                    elif base_name == "1. FC Köln":
                        base_name = "FC Köln"
                    elif base_name == "1. FC Heidenheim 1846":
                        base_name = "FC Heidenheim"
                    elif base_name == "1. FC Magdeburg":
                        base_name = "FC Magdeburg"
                    elif base_name == "1. FC Nürnberg":
                        base_name = "FC Nürnberg"
                    elif base_name == "FC Cologne":
                        base_name = "FC Köln"
                    elif base_name == "Hamburg SV":
                        base_name = "Hamburger SV"
                    elif base_name == "Hertha Berlin":
                        base_name = "Hertha BSC"
                    elif base_name == "SpVgg Greuther Furth":
                        base_name = "Greuther Fürth"
                    elif base_name == "TSV Eintracht Braunschweig":
                        base_name = "Eintracht Braunschweig"
                    # Strip out "1." from team names for German leagues
                    elif self.league in ['ger.1', 'ger.2']:
                        base_name = re.sub(r'^1\.\s*', '', base_name)
                    team_display = base_name
                
                # If no status, add padding to maintain alignment
                if not status:
                    status = "  "  # Two spaces for alignment with two-character symbols
                
                print(
                    f"{pos:3} {color}{status}{team_display:<{team_width}}{RESET} {team.games_played:3} {team.wins:3} {team.draws:3} "
                    f"{team.losses:3} {team.goals_for:3} {team.goals_against:3} "
                    f"{team.goal_difference:4} {team.points:3}"
                )
            
            # Print legend
            if self.league == 'usa.1' and league_config.get('tournament', 0):
                print("\nLegend:")
                print(f"{GREEN}* = MLS Cup Playoffs{RESET}")
            elif any(league_config.get(key, 0) > 0 for key in ['champions_league', 'europa_league', 'europa_conference', 'relegation_zone', 'promotion', 'promotion_playoff']) or league_config.get('relegation_playoff'):
                print("\nLegend:")
                if league_config.get('champions_league', 0):
                    print(f"{GREEN}* = UEFA Champions League{RESET}")
                if league_config.get('europa_league', 0):
                    print(f"{GREEN}† = UEFA Europa League{RESET}")
                if league_config.get('europa_conference', 0):
                    print(f"{GREEN}‡ = UEFA Europa Conference League{RESET}")
                if league_config.get('promotion', 0):
                    print(f"{GREEN}↑ = Automatic Promotion{RESET}")
                if league_config.get('promotion_playoff', 0):
                    print(f"{GREEN}⚡= Promotion Playoff{RESET}")
                if league_config.get('relegation_playoff'):
                    print(f"{RED}⚠ = Relegation Playoff{RESET}")
                if league_config.get('relegation_zone', 0):
                    print(f"{RED}↓ = Relegation Zone{RESET}")
    
    def _normalize_team_name(self, team_name):
        """Normalize team name for consistent lookup."""
        # Special case for German teams
        if self.league in ['ger.1', 'ger.2']:
            # Handle special cases first
            if team_name == "1. FC Union Berlin":
                return "Union Berlin"
            if team_name == "1. FC Köln":
                return "FC Köln"
            if team_name == "Borussia Monchengladbach":
                return "Borussia Mönchengladbach"
            if team_name == "1. FC Heidenheim 1846":
                return "FC Heidenheim"
            if team_name == "1. FC Magdeburg":
                return "FC Magdeburg"
            if team_name == "1. FC Nürnberg":
                return "FC Nürnberg"
            if team_name == "FC Cologne":
                return "FC Köln"
            if team_name == "Hamburg SV":
                return "Hamburger SV"
            if team_name == "Hertha Berlin":
                return "Hertha BSC"
            if team_name == "SV 07 Elversberg":
                return "SV Elversberg"
            if team_name == "SpVgg Greuther Furth":
                return "Greuther Fürth"
            if team_name == "TSV Eintracht Braunschweig":
                return "Eintracht Braunschweig"
            if team_name == "FC Kaiserslautern":
                return "Kaiserslautern"
            if team_name == "FC Schalke 04":
                return "Schalke 04"
            
            # Strip out "1." prefix from team names
            normalized_name = re.sub(r'^1\.\s*', '', team_name)
            
            # Handle common variations
            if normalized_name == "FC Cologne":
                return "FC Köln"
            if normalized_name == "Hamburg SV":
                return "Hamburger SV"
            if normalized_name == "Hertha Berlin":
                return "Hertha BSC"
            if normalized_name == "SV 07 Elversberg":
                return "SV Elversberg"
            if normalized_name == "SpVgg Greuther Furth":
                return "Greuther Fürth"
            if normalized_name == "TSV Eintracht Braunschweig":
                return "Eintracht Braunschweig"
            
            return normalized_name
            
        return team_name 