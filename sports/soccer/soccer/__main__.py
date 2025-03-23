"""Main entry point for soccer module."""

import argparse
import logging
import sys
from typing import List
from datetime import datetime
from .client import SoccerClient
from .config import LEAGUE_NAMES
from .cities import CITY_DATA

def parse_args(args: List[str] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Soccer Schedule and Standings Viewer")
    
    # League selection as positional argument
    parser.add_argument(
        'league',
        nargs='?',
        default="eng.1",
        help="League ID (defaults to English Premier League)"
    )
    
    # Team filtering
    parser.add_argument(
        '--team',
        help="Filter results by team name"
    )
    
    # Team search
    parser.add_argument(
        '--search',
        help="Search for teams by partial name and display league and city"
    )
    
    # Date range
    parser.add_argument(
        '--start',
        type=int,
        default=-2,
        help="Start number of days from today (negative for past)"
    )
    parser.add_argument(
        '--end',
        type=int,
        default=3,
        help="End number of days from today"
    )
    
    # Display options
    parser.add_argument(
        '--format',
        choices=['text', 'json', 'csv', 'md'],
        default='text',
        help="Output format (text, JSON, CSV, or Markdown)"
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed match information'
    )
    parser.add_argument(
        '--show-city',
        action='store_true',
        help='Show team city locations in output'
    )
    
    # What to show
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--fixtures-only',
        action='store_true',
        help='Show only fixtures'
    )
    group.add_argument(
        '--standings-only',
        action='store_true',
        help='Show only standings'
    )
    group.add_argument(
        '--list-leagues',
        action='store_true',
        help='List available leagues'
    )
    
    # Debug options
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args(args)

def search_teams(search_term: str) -> None:
    """Search for teams by partial name and display league and city information."""
    search_term = search_term.lower()
    found_teams = []
    
    # Search through all leagues
    for league_id, teams in CITY_DATA.items():
        league_name = LEAGUE_NAMES.get(league_id, league_id)
        
        # Search through teams in this league
        for team_name, city in teams.items():
            if search_term in team_name.lower():
                found_teams.append((team_name, league_name, city))
    
    # Sort results by team name
    found_teams.sort(key=lambda x: x[0])
    
    if found_teams:
        print(f"\nFound {len(found_teams)} teams matching '{search_term}':")
        print(f"{'Team':<40} {'League':<40} {'City':<30}")
        print("-" * 110)
        
        for team_name, league_name, city in found_teams:
            print(f"{team_name:<40} {league_name:<40} {city:<30}")
    else:
        print(f"\nNo teams found matching '{search_term}'")

def list_leagues() -> None:
    """Display available leagues grouped by geographical areas."""
    # Define league regions
    regions = {
        'Europe - Major Leagues': [
            'eng.1', 'esp.1', 'ger.1', 'ita.1', 'fra.1', 'ned.1', 'por.1'
        ],
        'Europe - Other Leagues': [
            'bel.1', 'bel.2', 'den.1', 'gre.1', 'nor.1', 'pol.1', 'rus.1',
            'sco.1', 'sco.2', 'sui.1', 'swe.1', 'tur.1', 'tur.2', 'ukr.1'
        ],
        'England - Other Competitions': [
            'eng.2', 'eng.3', 'eng.fa', 'eng.league_cup'
        ],
        'Spain - Other Competitions': [
            'esp.2', 'esp.copa_del_ray'
        ],
        'European Cups': [
            'uefa.champions', 'uefa.europa'
        ],
        'North America': [
            'usa.1', 'usa.2', 'mex.1', 'mex.2'
        ],
        'South America': [
            'arg.1', 'arg.2', 'bra.1', 'bra.2'
        ],
        'Asia': [
            'jpn.1', 'jpn.2', 'chn.1', 'kor.1'
        ],
        'Oceania': [
            'aus.1'
        ],
        'Africa & Middle East': [
            'egy.1', 'rsa.1', 'mar.1'
        ]
    }
    
    print("\nAvailable Leagues:")
    print(f"{'ID':<15} {'Name':<40}")
    print("-" * 55)
    
    for region, league_ids in regions.items():
        print(f"\n{region}:")
        # Sort leagues in this region alphabetically by name
        region_leagues = [(lid, LEAGUE_NAMES[lid]) for lid in league_ids]
        region_leagues.sort(key=lambda x: x[1])
        
        for league_id, league_name in region_leagues:
            print(f"  {league_id:<13} {league_name:<40}")

def main():
    """Main entry point."""
    args = parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    
    logger = logging.getLogger(__name__)
    logger.debug(f"Starting soccer client with args: {args}")
    
    try:
        if args.list_leagues:
            list_leagues()
            return
            
        if args.search:
            search_teams(args.search)
            return
            
        client = SoccerClient(args.league, args.team)
        
        # Show both fixtures and standings by default unless specified otherwise
        if args.standings_only:
            client.display_standings(args.format, args.show_city)
        elif args.fixtures_only:
            client.display_matches(args.start, args.end, args.format, args.show_city)
        else:
            # Show both fixtures and standings
            print("\n=== Standings ===")
            client.display_standings(args.format, args.show_city)
            print("\n=== Fixtures ===")
            client.display_matches(args.start, args.end, args.format, args.show_city)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=args.debug)
        sys.exit(1)

if __name__ == '__main__':
    main() 