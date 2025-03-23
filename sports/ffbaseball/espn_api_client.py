from espn_api.baseball import League
import os
from typing import Optional, Dict, List
import pandas as pd
import requests

class ESPNFantasyBaseball:
    def __init__(self, league_id: int = 87636, espn_s2: Optional[str] = None, swid: Optional[str] = None):
        """
        Initialize the ESPN Fantasy Baseball client
        
        Args:
            league_id: ESPN league ID (default: 87636)
            espn_s2: ESPN S2 cookie for private leagues
            swid: ESPN SWID cookie for private leagues
        """
        self.league_id = league_id
        self.espn_s2 = espn_s2 or os.getenv('ESPN_S2')
        self.swid = swid or os.getenv('SWID')
        self.league = League(league_id=league_id, espn_s2=self.espn_s2, swid=self.swid, year=2025)

    def get_current_matchup(self) -> List[Dict]:
        """Get current matchup data for all teams"""
        matchups = []
        
        if not hasattr(self.league, 'current_matchup') or not self.league.current_matchup:
            return []
            
        for matchup in self.league.current_matchup:
            if not matchup or not hasattr(matchup, 'home_team') or not hasattr(matchup, 'away_team'):
                continue
                
            home_team = matchup.home_team
            away_team = matchup.away_team
            
            # Get detailed stats for both teams
            home_stats = self._get_team_matchup_stats(home_team)
            away_stats = self._get_team_matchup_stats(away_team)
            
            matchups.append({
                'home_team': home_team.team_name,
                'away_team': away_team.team_name,
                'home_score': matchup.home_score,
                'away_score': matchup.away_score,
                'home_stats': home_stats,
                'away_stats': away_stats
            })
        return matchups

    def _get_team_matchup_stats(self, team) -> Dict:
        """Get detailed baseball statistics for a team in current matchup"""
        stats = {}
        if hasattr(team, 'stats'):
            for category, value in team.stats.items():
                # Convert stats to readable format
                if isinstance(value, float):
                    # Format percentages and ratios to 3 decimal places
                    if category.lower() in ['avg', 'obp', 'slg', 'ops', 'era', 'whip']:
                        stats[category] = f"{value:.3f}"
                    else:
                        stats[category] = f"{value:.1f}"
                else:
                    stats[category] = value
        return stats

    def _find_team_by_id(self, team_id: int):
        """Find a team by its ID"""
        for team in self.league.teams:
            if team.team_id == team_id:
                return team
        return None

    def get_team_stats(self, team_id: Optional[int] = None) -> pd.DataFrame:
        """Get team statistics for the season"""
        if team_id is not None:
            team = self._find_team_by_id(team_id)
            teams = [team] if team else []
        else:
            teams = self.league.teams

        stats = []
        for team in teams:
            print(f"Debug - Team: {team.team_name}, ID: {team.team_id}")  # Debug print
            team_stats = {
                'Team': team.team_name,
                'Standing': team.standing,
                'Wins': getattr(team, 'wins', 0),
                'Losses': getattr(team, 'losses', 0),
                'Ties': getattr(team, 'ties', 0),
            }
            
            # Add team stats if available
            if hasattr(team, 'stats'):
                for category, value in team.stats.items():
                    if isinstance(value, float):
                        if category.lower() in ['avg', 'obp', 'slg', 'ops', 'era', 'whip']:
                            team_stats[category] = f"{value:.3f}"
                        else:
                            team_stats[category] = f"{value:.1f}"
                    else:
                        team_stats[category] = value
            
            stats.append(team_stats)
        
        return pd.DataFrame(stats)

    def get_player_stats(self, team_id: Optional[int] = None) -> pd.DataFrame:
        """Get player statistics for a team or all teams"""
        if team_id is not None:
            team = self._find_team_by_id(team_id)
            teams = [team] if team else []
        else:
            teams = self.league.teams

        stats = []
        for team in teams:
            for player in team.roster:
                if hasattr(player, 'stats') and player.stats:
                    # Get the most recent stats (usually at index 0)
                    recent_stats = player.stats.get(0, {})
                    
                    # Get the breakdown of stats if available
                    breakdown = recent_stats.get('breakdown', {})
                    
                    # Map slot IDs to position names
                    slot_map = {
                        0: "C", 1: "1B", 2: "2B", 3: "3B", 4: "SS", 5: "OF",
                        6: "2B/SS", 7: "1B/3B", 8: "LF", 9: "CF", 10: "RF",
                        11: "DH", 12: "UTIL", 13: "P", 14: "SP", 15: "RP"
                    }
                    
                    # Convert eligible slots to position names, excluding BE/IL/NA/UTIL
                    eligible_positions = []
                    if hasattr(player, 'eligibleSlots'):
                        eligible_positions = [slot_map.get(slot, '') for slot in player.eligibleSlots 
                                           if slot in slot_map]
                        eligible_positions = [pos for pos in eligible_positions if pos]  # Remove empty strings
                    
                    # Determine if player is a pitcher
                    is_pitcher = any(pos in ['P', 'SP', 'RP'] for pos in eligible_positions)
                    
                    # Base player info
                    player_dict = {
                        'Team': team.team_name,
                        'Player': player.name,
                        'Position': player.position,
                        'Pro Team': player.proTeam,
                        'Eligible Positions': ', '.join(eligible_positions),
                        'Injured': getattr(player, 'injured', False),
                        'Injury Status': getattr(player, 'injuryStatus', '')
                    }
                    
                    if is_pitcher:
                        # Pitching stats
                        player_dict.update({
                            'ERA': breakdown.get('ERA', 0.0),
                            'WHIP': breakdown.get('WHIP', 0.0),
                            'W': breakdown.get('W', 0),
                            'L': breakdown.get('L', 0),
                            'SV': breakdown.get('SV', 0),
                            'HLD': breakdown.get('HLD', 0),
                            'K': breakdown.get('K', 0),
                            'K/9': breakdown.get('K/9', 0.0),
                            'K/BB': breakdown.get('K/BB', 0.0),
                            'QS': breakdown.get('QS', 0)
                        })
                    else:
                        # Batting stats
                        player_dict.update({
                            'AVG': breakdown.get('AVG', 0.0),
                            'HR': breakdown.get('HR', 0),
                            'RBI': breakdown.get('RBI', 0),
                            'R': breakdown.get('R', 0),
                            'SB': breakdown.get('SB', 0),
                            'OBP': breakdown.get('OBP', 0.0),
                            'SLG': breakdown.get('SLG', 0.0),
                            'OPS': breakdown.get('OPS', 0.0)
                        })
                    
                    stats.append(player_dict)
        
        # Convert to DataFrame
        if stats:
            df = pd.DataFrame(stats)
            # Reorder columns for better readability
            column_order = [
                'Team', 'Player', 'Position', 'Pro Team', 'Eligible Positions', 'Injured', 'Injury Status'
            ]
            # Add stats columns based on whether they exist
            pitching_stats = ['ERA', 'WHIP', 'W', 'L', 'SV', 'HLD', 'K', 'K/9', 'K/BB', 'QS']
            batting_stats = ['AVG', 'HR', 'RBI', 'R', 'SB', 'OBP', 'SLG', 'OPS']
            
            # Only include columns that exist in the DataFrame
            column_order.extend([col for col in pitching_stats if col in df.columns])
            column_order.extend([col for col in batting_stats if col in df.columns])
            existing_columns = [col for col in column_order if col in df.columns]
            return df[existing_columns]
        
        return pd.DataFrame()

    def get_season_schedule(self) -> List[Dict]:
        """Get the full season schedule of matchups"""
        schedule = []
        
        if not hasattr(self.league, 'schedule'):
            return []
            
        for week, matchups in enumerate(self.league.schedule, 1):
            week_matchups = []
            for matchup in matchups:
                if not matchup or not hasattr(matchup, 'home_team') or not hasattr(matchup, 'away_team'):
                    continue
                    
                week_matchups.append({
                    'week': week,
                    'home_team': matchup.home_team.team_name,
                    'away_team': matchup.away_team.team_name,
                    'home_score': getattr(matchup, 'home_score', 0),
                    'away_score': getattr(matchup, 'away_score', 0)
                })
            if week_matchups:
                schedule.extend(week_matchups)
        
        return schedule 

    def get_free_agents(self, position=None, season=2025):
        """
        Get list of free agents.
        
        Args:
            position: Filter by position (e.g., 'SP', '1B', etc.)
            season: Season year (2024 or 2025)
        """
        # Create a new league instance for the specified season
        league = League(league_id=self.league_id, espn_s2=self.espn_s2, swid=self.swid, year=season)
        if not league.free_agents():
            return pd.DataFrame()

        players = []
        free_agents = league.free_agents()

        # Map slot IDs to position names
        slot_map = {
            0: "C", 1: "1B", 2: "2B", 3: "3B", 4: "SS", 5: "OF",
            6: "2B/SS", 7: "1B/3B", 8: "LF", 9: "CF", 10: "RF",
            11: "DH", 12: "UTIL", 13: "P", 14: "SP", 15: "RP",
            16: "BE", 17: "IL", 19: "NA"
        }

        for player in free_agents:
            # Get player stats
            stats = player.stats or {}
            
            # Determine player position(s)
            eligible_slots = []
            if hasattr(player, 'eligibleSlots'):
                eligible_slots = [slot_map.get(slot, str(slot)) for slot in player.eligibleSlots]
                # Filter out bench, IL, NA, and UTIL positions
                eligible_slots = [pos for pos in eligible_slots if pos not in ['BE', 'IL', 'NA', 'UTIL']]
            
            # Determine primary position
            if 'SP' in eligible_slots:
                position_str = 'SP'
            elif 'RP' in eligible_slots:
                position_str = 'RP'
            elif 'P' in eligible_slots:
                position_str = 'P'
            elif eligible_slots:
                position_str = eligible_slots[0]  # Use first eligible position
            else:
                position_str = str(player.position).upper()  # Fallback to raw position

            # Base player info
            player_dict = {
                "Player": player.name,
                "Position": position_str,
                "Pro Team": player.proTeam,
                "Injured": player.injured,
                "Injury Status": player.injuryStatus,
            }

            # Add stats based on player type
            if any(pos in position_str for pos in ['SP', 'RP', 'P']):
                # Pitching stats
                player_dict.update({
                    "ERA": stats.get("ERA", 0.0),
                    "WHIP": stats.get("WHIP", 0.0),
                    "W": stats.get("W", 0),
                    "L": stats.get("L", 0),
                    "SV": stats.get("SV", 0),
                    "HLD": stats.get("HLD", 0),
                    "K": stats.get("K", 0),
                    "K/9": stats.get("K/9", 0.0),
                    "K/BB": stats.get("K/BB", 0.0),
                    "QS": stats.get("QS", 0)
                })
            else:
                # Batting stats
                player_dict.update({
                    "AVG": stats.get("AVG", 0.0),
                    "HR": stats.get("HR", 0),
                    "RBI": stats.get("RBI", 0),
                    "R": stats.get("R", 0),
                    "SB": stats.get("SB", 0),
                    "OBP": stats.get("OBP", 0.0),
                    "SLG": stats.get("SLG", 0.0),
                    "OPS": stats.get("OPS", 0.0)
                })

            players.append(player_dict)

        df = pd.DataFrame(players)
        
        if position:
            df = df[df["Position"].str.contains(position, case=False)]
        
        # Sort based on position type
        if not df.empty:
            if position and any(pos in position.upper() for pos in ['SP', 'RP', 'P']):
                df = df.sort_values(by=["ERA", "WHIP", "K"], ascending=[True, True, False])
            else:
                df = df.sort_values(by=["AVG", "HR", "RBI"], ascending=[False, False, False])
        
        return df