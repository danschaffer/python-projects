#!/usr/bin/env python

import argparse
import datetime
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import pytz
import requests
import tzlocal
from requests.exceptions import RequestException

# Configuration
CONFIG = {
    'API_URL': 'http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard',
    'POINTS': {
        'WIN': 2,
        'DRAW': 1
    },
    'DATE_FORMAT': {
        'API': '%Y%m%d',
        'DISPLAY': '%a %b %-d',
        'TIME': '%-I:%M',
    }
}

@dataclass
class TeamRecord:
    """Data class for team record information."""
    name: str
    wins: int
    losses: int
    draws: int
    points: int
    record_string: str

class NhlApiClient:
    """Handles all API interactions with the ESPN NHL API."""
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_schedule(self, date: datetime.datetime) -> dict:
        """Fetch schedule data from ESPN API.
        
        Args:
            date: The date to fetch schedule for
            
        Returns:
            dict: JSON response from API
            
        Raises:
            RequestException: If the API request fails
        """
        try:
            response = self.session.get(
                CONFIG['API_URL'],
                params={'dates': date.strftime(CONFIG['DATE_FORMAT']['API'])}
            )
            response.raise_for_status()
            return response.json()
        except (RequestException, ValueError) as e:
            raise RequestException(f"Failed to fetch NHL schedule: {str(e)}")

class NhlFormatter:
    """Handles formatting of NHL data for display."""
    
    @staticmethod
    def format_game_time(utc_time: str) -> str:
        """Convert UTC time string to local time string."""
        try:
            local_timezone = tzlocal.get_localzone()
            utc_time = datetime.datetime.strptime(utc_time, '%Y-%m-%dT%H:%MZ')
            local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
            return local_time.strftime(CONFIG['DATE_FORMAT']['TIME']) + local_time.strftime("%p")[0].lower()
        except (ValueError, AttributeError) as e:
            return "Time N/A"

class Nhl:
    """A class to fetch and display NHL schedules and standings using the ESPN API."""
    
    def __init__(self, debug: bool = False):
        """Initialize the NHL class with team divisions and empty records.
        
        Args:
            debug (bool): Enable debug output if True
        """
        self.records: Dict[str, TeamRecord] = {}
        self.debug = debug
        self.api_client = NhlApiClient()
        self.formatter = NhlFormatter()
        
        # NHL divisions and their teams as of 2024-25 season
        self.divisions: Dict[str, List[str]] = {
            'Eastern/Atlantic': ['Bruins','Maple Leafs','Red Wings','Lightning','Canadiens','Panthers','Sabres','Senators'],
            'Eastern/Metropolitan': ['Devils','Islanders','Penguins','Hurricanes','Rangers','Capitals','Flyers','Blue Jackets'],
            'Western/Central': ['Stars','Jets','Avalanche','Blues','Predators','Wild','Utah HC','Blackhawks'],
            'Western/Pacific': ['Golden Knights','Kraken','Kings','Flames','Oilers','Canucks','Sharks','Ducks']
        }

    def get_schedule(self, days: int, verbose: bool = False, silent: bool = False) -> None:
        """Fetch and display NHL schedule for a specific day."""
        try:
            _date = datetime.datetime.now() + datetime.timedelta(days=days)
            data = self.api_client.get_schedule(_date)
            
            if not data.get('events'):
                if self.debug:
                    print(f"No games scheduled for {_date.strftime(CONFIG['DATE_FORMAT']['DISPLAY'])}")
                return

            if not silent:
                print(_date.strftime(CONFIG['DATE_FORMAT']['DISPLAY']))

            for event in data['events']:
                self._process_game(event, verbose, silent)
                
        except Exception as e:
            print(f"Error fetching schedule: {str(e)}")

    def _process_game(self, event: dict, verbose: bool, silent: bool) -> None:
        """Process a single game event."""
        try:
            clock = '' if event['status']['type']['completed'] else event['status']['displayClock']
            game_time = self.formatter.format_game_time(event['date'])
            
            competition = event['competitions'][0]
            teams: Dict[str, str] = {}
            
            for team in competition['competitors']:
                if self.debug:
                    print(f"Found team: {team['team']['shortDisplayName']}")
                
                self._process_team(team, competition, teams, clock, game_time, verbose, silent)
                
        except KeyError as e:
            if self.debug:
                print(f"Error processing game data: {str(e)}")

    def _process_team(self, team: dict, competition: dict, teams: dict,
                     clock: str, game_time: str, verbose: bool, silent: bool) -> None:
        """Process team data within a game."""
        try:
            team_name = team['team']['shortDisplayName']
            record = team['records'][0]['summary']
            score = team.get('score', '')
            
            # Add team record
            self._add_record(team_name, record)
            teams[team['id']] = team['team']['abbreviation']
            
            if not silent:
                if team['homeAway'] == 'home':
                    home = f"{team_name}({record}) {score}"
                    away = f"{competition['competitors'][1]['team']['shortDisplayName']}({competition['competitors'][1]['records'][0]['summary']}) {competition['competitors'][1].get('score', '')}"
                    print(f"{away} at {home} {clock or game_time}")
                
            if verbose and 'leaders' in team:
                self._display_team_leaders(team, teams)
                
        except KeyError as e:
            if self.debug:
                print(f"Error processing team data: {str(e)}")

    def _add_record(self, team: str, record: str) -> None:
        """Add or update a team's record."""
        if team in self.records:
            return
            
        try:
            if self.debug:
                print(f"Adding record for {team}: {record}")
            
            # Remove parentheses if present
            if record.startswith('('):
                record = record[1:-1]
            
            # Parse record
            wins, losses, draws = map(int, record.split('-'))
            points = wins * CONFIG['POINTS']['WIN'] + draws * CONFIG['POINTS']['DRAW']
            
            self.records[team] = TeamRecord(
                name=team,
                wins=wins,
                losses=losses,
                draws=draws,
                points=points,
                record_string=record
            )
        except (ValueError, IndexError) as e:
            if self.debug:
                print(f"Error parsing record '{record}' for team {team}: {str(e)}")

    def _display_team_leaders(self, team: dict, teams: dict) -> None:
        """Display team leaders statistics."""
        try:
            for leader in team['leaders']:
                print(f"  {teams[leader['leaders'][0]['athlete']['team']['id']]} {leader['shortDisplayName']} {leader['leaders'][0]['athlete']['displayName']} {leader['leaders'][0]['displayValue']}")
        except (KeyError, IndexError) as e:
            if self.debug:
                print(f"Error displaying team leaders: {str(e)}")

    def schedules(self, start, end, verbose, silent=False):
        """Fetch schedules for a range of days.
        
        Args:
            start (int): Start day offset from today
            end (int): End day offset from today
            verbose (bool): Show detailed stats if True
            silent (bool): Suppress regular output if True
        """
        for count in range(start, end):
            self.get_schedule(count, verbose, silent)

    def standings(self, start: int) -> None:
        """Display current standings by division."""
        # Keep fetching schedules until we have all 32 teams
        while len(self.records) < 32:
            start -= 1
            self.schedules(start, start+1, verbose=False, silent=True)
        
        for division in self.divisions:
            print(division)
            teams = []
            for team in self.divisions[division]:
                if team in self.records:
                    teams.append(self.records[team])
            
            # Sort by points (descending)
            teams.sort(key=lambda x: (x.points, x.wins), reverse=True)
            
            for team in teams:
                print(f"{team.name:15} {team.record_string:10} {team.points:3}")

def main():
    """Main entry point for the NHL schedule and standings program."""
    parser = argparse.ArgumentParser(description="NHL Schedule and Standings Viewer")
    parser.add_argument('--start', type=int, default=-1, help="start number of days")
    parser.add_argument('--end', type=int, default=1, help="end number of days")
    parser.add_argument('--verbose', action='store_true', help='increase verbosity')
    parser.add_argument('--schedule', action='store_true', help='show schedule')
    parser.add_argument('--standings', action='store_true', help='show standings')
    parser.add_argument('--debug', action='store_true', help='enable debug output')
    
    pargs = parser.parse_args()
    
    # Default to showing both schedule and standings if neither specified
    if not pargs.schedule and not pargs.standings:
        pargs.schedule = pargs.standings = True
    
    try:
        hockey = Nhl(debug=pargs.debug)
        if pargs.schedule:
            hockey.schedules(pargs.start, pargs.end, pargs.verbose)
        if pargs.standings:
            hockey.standings(pargs.start)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 1
    return 0

if __name__ == '__main__':
    exit(main())
