"""Tests for city data coverage and accuracy."""

import pytest
from soccer.cities import CITY_DATA
from soccer.config import LEAGUE_NAMES, LEAGUE_SIZE
import requests

def test_all_leagues_have_city_data():
    """Verify that all leagues in config have corresponding city data."""
    missing_leagues = []
    for league_id in LEAGUE_NAMES.keys():
        if league_id not in CITY_DATA:
            missing_leagues.append(league_id)
    
    assert not missing_leagues, f"Missing city data for leagues: {missing_leagues}"

def test_city_data_matches_api_teams():
    """Verify that city data matches actual team names from the API."""
    base_url = "https://site.api.espn.com/apis/site/v2/sports/soccer/:league/teams"
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; SoccerStats/1.0)',
        'Accept': 'application/json'
    }
    
    issues = []
    
    # List of placeholder team names to ignore
    placeholder_teams = {
        'Highest Ranked Week 1 Winner',
        'Lowest Ranked Week 1 Winner',
        '1st Place',
        '2nd Place',
        '3rd Place',
        '4th Place',
        '5th Place',
        '6th Place',
        'Auckland FC'
    }
    
    for league_id in LEAGUE_NAMES.keys():
        if league_id in ['uefa.champions', 'uefa.europa', 'eng.fa', 'eng.league_cup', 'esp.copa_del_ray']:
            continue  # Skip cup competitions as they have variable teams
            
        try:
            url = base_url.replace(':league', league_id)
            response = requests.get(
                url,
                headers=headers,
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            if 'sports' not in data or not data['sports']:
                issues.append(f"No data found for league {league_id}")
                continue
                
            api_teams = set()
            for team in data['sports'][0]['leagues'][0]['teams']:
                team_name = team['team']['name']
                if team_name not in placeholder_teams:  # Skip placeholder teams
                    api_teams.add(team_name)
            
            if league_id not in CITY_DATA:
                issues.append(f"No city data for league {league_id}")
                continue
            
            city_data_teams = set(CITY_DATA[league_id].keys())
            
            # Find teams in API but missing from city data
            missing_teams = api_teams - city_data_teams
            if missing_teams:
                issues.append(f"League {league_id} missing city data for teams: {missing_teams}")
            
            # Find teams in city data but not in API (possibly outdated)
            extra_teams = city_data_teams - api_teams
            if extra_teams:
                issues.append(f"League {league_id} has extra teams in city data: {extra_teams}")
                
        except requests.RequestException as e:
            issues.append(f"Error fetching data for league {league_id}: {str(e)}")
            continue
            
    assert not issues, "\n".join(issues)

def test_league_size_matches_city_data():
    """Verify that league sizes roughly match the number of teams with city data."""
    issues = []
    
    for league_id, size in LEAGUE_SIZE.items():
        if league_id in ['uefa.champions', 'uefa.europa', 'eng.fa', 'eng.league_cup', 'esp.copa_del_ray']:
            continue  # Skip cup competitions
            
        if league_id not in CITY_DATA:
            issues.append(f"No city data for league {league_id}")
            continue
            
        city_data_size = len(CITY_DATA[league_id])
        # Allow for some variation due to promotion/relegation
        if abs(city_data_size - size) > 4:  # Allow 4 team difference for promotions/relegations
            issues.append(
                f"League {league_id} size mismatch: "
                f"config has {size} teams but city data has {city_data_size} teams"
            )
            
    assert not issues, "\n".join(issues)

def test_standings_data_available():
    """Verify that standings data can be retrieved from the API."""
    base_url = "https://site.api.espn.com/apis/site/v2/sports/soccer/:league/standings"
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; SoccerStats/1.0)',
        'Accept': 'application/json'
    }
    
    # Test with a major league that should always have standings
    league_id = "eng.1"  # English Premier League
    url = base_url.replace(':league', league_id)
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Verify the response contains standings data
        assert 'standings' in data, "No standings data in API response"
        assert len(data['standings']) > 0, "Empty standings data in API response"
        
        # Verify the standings contain expected fields
        standings = data['standings'][0]['entries']
        assert len(standings) > 0, "No team entries in standings"
        
        first_team = standings[0]
        required_fields = ['stats', 'team']
        for field in required_fields:
            assert field in first_team, f"Missing required field '{field}' in standings data"
            
        # Verify stats contain basic standings information
        stats = {stat['name']: stat['value'] for stat in first_team['stats']}
        required_stats = ['gamesPlayed', 'points', 'rank']
        for stat in required_stats:
            assert stat in stats, f"Missing required stat '{stat}' in standings data"
            
    except requests.RequestException as e:
        pytest.fail(f"Failed to retrieve standings data: {str(e)}")
    except KeyError as e:
        pytest.fail(f"Unexpected API response structure: {str(e)}") 