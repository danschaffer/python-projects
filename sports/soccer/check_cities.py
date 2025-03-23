import logging
from soccer.client import SoccerClient
from soccer.config import LEAGUE_NAMES
from soccer.cities import CITY_DATA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_league_cities(league_id):
    """Check each league for teams without city information."""
    client = SoccerClient(league_id)
    standings = client.get_standings()
    
    if not standings:
        logger.warning(f"No standings found for league {league_id}")
        return
    
    missing_cities = []
    for team in standings:
        if team.name not in CITY_DATA.get(league_id, {}):
            missing_cities.append(team.name)
    
    if missing_cities:
        print(f"\nTeams missing city information in {league_id}:")
        for team in sorted(missing_cities):
            print(f"- {team}")

def main():
    """Check all leagues for teams without city information."""
    print("Checking for teams without city information...")
    
    for league_id in CITY_DATA.keys():
        try:
            check_league_cities(league_id)
        except Exception as e:
            logger.error(f"Error checking league {league_id}: {str(e)}")

if __name__ == "__main__":
    main() 