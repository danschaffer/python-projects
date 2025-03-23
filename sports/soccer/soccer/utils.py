"""Utility functions for the soccer module."""

import json
import csv
import logging
from datetime import datetime
from typing import Any, Dict, List
from functools import lru_cache
import time
import pytz
import tzlocal
from .config import DATE_FORMAT, CACHE_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def format_datetime(dt: datetime, fmt: str = DATE_FORMAT['DISPLAY']) -> str:
    """Format datetime object according to specified format."""
    return dt.strftime(fmt)

def to_local_time(utc_time: str) -> datetime:
    """Convert UTC time string to local datetime."""
    try:
        local_timezone = tzlocal.get_localzone()
        dt = datetime.strptime(utc_time, '%Y-%m-%dT%H:%MZ')
        return dt.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    except (ValueError, AttributeError) as e:
        logger.error(f"Error converting time: {e}")
        return datetime.now()

def to_json(data: Any) -> str:
    """Convert data to JSON string."""
    return json.dumps(data, default=str, indent=2)

def to_csv(data: List[Dict], filename: str) -> None:
    """Write data to CSV file."""
    if not data:
        return
    
    fieldnames = data[0].keys()
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def cached_api_call(func):
    """Cache API calls with timeout."""
    @lru_cache(maxsize=CACHE_CONFIG['MAX_SIZE'])
    def wrapper(*args, **kwargs):
        current_time = int(time.time())
        # Include current time block in cache key
        cache_key = f"{func.__name__}_{args}_{kwargs}_{current_time // CACHE_CONFIG['TIMEOUT']}"
        return func(*args, **kwargs)
    return wrapper

def validate_league_id(league_id: str) -> bool:
    """Validate league ID format."""
    parts = league_id.split('.')
    return len(parts) == 2 and parts[1].isdigit()

def format_score(score: int, shootout_score: int = None) -> str:
    """Format match score with optional shootout score."""
    if shootout_score is not None:
        return f"{score} ({shootout_score})"
    return str(score)

def to_markdown(data: Any, title: str = None, show_city: bool = False, city_data: Dict = None) -> str:
    """Convert data to markdown format."""
    if not data:
        return "No data available"
        
    md = []
    if title:
        md.append(f"# {title}\n")
    
    if isinstance(data, list) and data and hasattr(data[0], 'name'):
        # Standings table
        headers = ["Team"]
        if show_city:
            headers.append("City")
        headers.extend(["MP", "W", "D", "L", "GF", "GA", "GD", "Pts"])
        
        md.append("| " + " | ".join(headers) + " |")
        md.append("|" + "|".join(["---" for _ in headers]) + "|")
        
        for team in data:
            row = [team.name]
            if show_city and city_data:
                row.append(city_data.get(team.name, ''))
            row.extend([
                str(team.games_played),
                str(team.wins),
                str(team.draws),
                str(team.losses),
                str(team.goals_for),
                str(team.goals_against),
                str(team.goal_difference),
                str(team.points)
            ])
            md.append("| " + " | ".join(row) + " |")
    
    elif isinstance(data, list) and data and hasattr(data[0], 'home_team'):
        # Matches
        headers = ["Date", "Home", "Away", "Score/Time"]
        if show_city:
            headers.append("City")
        md.append("| " + " | ".join(headers) + " |")
        md.append("|" + "|".join(["---" for _ in headers]) + "|")
        
        current_date = None
        for match in data:
            match_date = match.date.strftime(DATE_FORMAT['DISPLAY'])
            if match_date != current_date:
                if current_date is not None:
                    md.append("")  # Add blank line between dates
                md.append(f"**{match_date}**")
                current_date = match_date
            
            time_str = match.date.strftime(DATE_FORMAT['TIME'])
            if match.status == 'pre':
                row = [
                    "",  # Empty date cell
                    match.home_team,
                    match.away_team,
                    time_str
                ]
                if show_city and city_data:
                    row.append(city_data.get(match.home_team, ''))
            else:
                score = f"{match.score_home} - {match.score_away}"
                row = [
                    "",  # Empty date cell
                    match.home_team,
                    match.away_team,
                    score
                ]
                if show_city and city_data:
                    row.append(city_data.get(match.home_team, ''))
            md.append("| " + " | ".join(row) + " |")
    
    return "\n".join(md) 