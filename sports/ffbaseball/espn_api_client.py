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
        print(f"Looking for team with ID: {team_id}")
        print("Available teams:")
        for team in self.league.teams:
            print(f"  - Team ID: {team.team_id}, Name: {team.team_name}")
            if team.team_id == team_id:
                print(f"Found team: {team.team_name}")
                return team
        print(f"No team found with ID: {team_id}")
        return None

    def get_team_stats(self, team_id: int = 7) -> pd.DataFrame:
        """Get team statistics for the season"""
        team = self._find_team_by_id(team_id)
        teams = [team] if team else []

        stats = []
        for team in teams:
            print(f"Debug - Team: {team.team_name}, ID: {team.team_id}")  # Debug print
            team_stats = {
                'Team': team.team_name or '',
                'Standing': team.standing if hasattr(team, 'standing') else '',
                'Wins': self._safe_int(getattr(team, 'wins', 0)),
                'Losses': self._safe_int(getattr(team, 'losses', 0)),
                'Ties': self._safe_int(getattr(team, 'ties', 0)),
            }
            
            # Add team stats if available
            if hasattr(team, 'stats'):
                for category, value in team.stats.items():
                    # Convert stats to readable format
                    if category.lower() in ['avg', 'obp', 'slg', 'ops', 'era', 'whip']:
                        # Format percentages and ratios to 3 decimal places as strings
                        team_stats[category] = f"{self._safe_float(value):.3f}"
                    elif isinstance(value, (int, float)):
                        # Format other numeric values to 1 decimal place as strings
                        team_stats[category] = f"{self._safe_float(value):.1f}"
                    else:
                        team_stats[category] = str(value) if value is not None else "0"
            
            stats.append(team_stats)
        
        # Create DataFrame and fill NaN values
        df = pd.DataFrame(stats)
        
        # Fill NaN values with appropriate defaults
        numeric_cols = ['Wins', 'Losses', 'Ties']
        percentage_cols = ['AVG', 'OBP', 'SLG', 'OPS', 'ERA', 'WHIP']
        
        # Fill numeric columns with '0'
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(0).astype(int)
        
        # Fill percentage columns with '0.000'
        for col in percentage_cols:
            if col in df.columns:
                df[col] = df[col].fillna('0.000')
        
        # Fill any remaining NaN values with empty string
        df = df.fillna('')
        
        return df

    def get_player_stats(self, team_id: int = 7) -> pd.DataFrame:
        """Get player statistics for a team or all teams, separating batters and pitchers"""
        # Define column orders first
        base_columns = ['Team', 'Player', 'Position', 'Pro Team', 'Slot', 'Injury Status']
        pitching_stat_cols = ['ERA', 'WHIP', 'W', 'L', 'SV', 'HLD', 'K', 'K/9', 'K/BB', 'QS']
        batting_stat_cols = ['AVG', 'OBP', 'SLG', 'OPS', 'HR', 'RBI', 'R', 'SB']
        pitching_cols = base_columns + ['Next Start'] + pitching_stat_cols
        batting_cols = base_columns + batting_stat_cols

        # Get all teams if team_id is None, otherwise get the specified team
        if team_id is not None:
            team = self._find_team_by_id(team_id)
            if not team:
                print(f"Warning: Team ID {team_id} not found")
                return pd.DataFrame()  # Return empty DataFrame if team not found
            teams = [team]
        else:
            teams = self.league.teams

        batting_stats = []
        pitching_stats = []
        
        for team in teams:
            if not hasattr(team, 'roster') or not team.roster:
                print(f"Warning: No roster found for team {team.team_name}")
                continue
                
            print(f"\nProcessing team: {team.team_name}")
            print(f"Total players in roster: {len(team.roster)}")
            
            for player in team.roster:
                print(f"\nProcessing player object: {getattr(player, 'name', 'NO NAME')}")
                print(f"Player attributes: {dir(player)}")
                
                # Skip players with no name
                if not player.name:
                    print(f"Skipping player with no name in team {team.team_name}")
                    continue
                    
                # Initialize stats even if player has no recent stats
                recent_stats = {}
                stats_to_use = {}
                
                print(f"Checking stats for {player.name}:")
                if hasattr(player, 'stats'):
                    print(f"Player has stats attribute")
                    if player.stats:
                        print(f"Stats available: {player.stats.keys()}")
                        recent_stats = player.stats.get(0, {})
                        print(f"Recent stats: {recent_stats}")
                        # Get the stats - try breakdown first, fall back to top-level stats
                        breakdown = recent_stats.get('breakdown', {})
                        stats_to_use = breakdown if breakdown else recent_stats
                        print(f"Stats to use: {stats_to_use}")
                    else:
                        print("Player stats is empty")
                else:
                    print("Player has no stats attribute")
                
                print(f"Processing player: {player.name} - Team: {team.team_name} - Pro Team: {getattr(player, 'proTeam', '')}")
                
                # Map slot IDs to position names
                slot_map = {
                    0: "C", 1: "1B", 2: "2B", 3: "3B", 4: "SS", 5: "OF",
                    6: "2B/SS", 7: "1B/3B", 8: "LF", 9: "CF", 10: "RF",
                    11: "DH", 12: "UTIL", 13: "P", 14: "SP", 15: "RP",
                    16: "BE", 17: "IL", 19: "NA"  # Added BE, IL, NA for filtering
                }

                # Define position priorities (lower number = higher priority)
                position_priority = {
                    'OF': 1, 'LF': 1, 'CF': 1, 'RF': 1,  # Outfield positions highest priority
                    'C': 2,  # Catcher next
                    '1B': 3, '2B': 3, '3B': 3, 'SS': 3,  # Infield positions
                    'DH': 4,  # DH after infield
                    '2B/SS': 5, '1B/3B': 5,  # Utility infield positions lowest priority
                    'UTIL': 6,
                    'SP': 1, 'RP': 1, 'P': 1  # Pitching positions high priority
                }
                
                # Convert eligible slots to position names, only excluding bench and injury slots
                eligible_positions = []
                raw_slots = []
                if hasattr(player, 'eligibleSlots'):
                    raw_slots = player.eligibleSlots
                    print(f"Raw eligible slots for {player.name}: {raw_slots}")
                    
                    # Map positions and filter out bench/injury slots
                    eligible_positions = []
                    for slot in raw_slots:
                        pos = slot_map.get(slot, '')
                        print(f"Mapping slot {slot} to position: {pos}")
                        if pos and pos not in ['BE', 'IL', 'NA']:  # Keep DH and UTIL
                            eligible_positions.append(pos)
                    
                    # Sort positions by priority
                    eligible_positions.sort(key=lambda x: position_priority.get(x, 99))
                    
                    # If any outfield position exists, remove utility infield positions
                    if any(pos in ['OF', 'LF', 'CF', 'RF'] for pos in eligible_positions):
                        eligible_positions = [pos for pos in eligible_positions if pos not in ['1B/3B', '2B/SS']]
                    
                    print(f"Mapped eligible positions for {player.name}: {eligible_positions}")
                else:
                    print(f"No eligibleSlots attribute for {player.name}")
                
                # Get default position and clean it
                default_position = str(getattr(player, 'position', '')).upper()
                print(f"Default position for {player.name}: {default_position}")
                
                # If no eligible positions but we have a default position, use that
                if not eligible_positions and default_position:
                    print(f"Using default position for {player.name}: {default_position}")
                    eligible_positions = [default_position]
                
                # Check if player is any type of pitcher
                is_sp = False
                is_rp = False
                is_p = False
                
                # Check multiple ways to identify a pitcher
                if hasattr(player, 'defaultPositionId'):
                    print(f"Default position ID for {player.name}: {player.defaultPositionId}")
                    if player.defaultPositionId == 1:  # 1 is pitcher in ESPN's system
                        is_p = True
                        print(f"{player.name} identified as pitcher by defaultPositionId")
                
                # Check eligible positions for pitcher roles
                if any(pos in ['SP', 'RP', 'P'] for pos in eligible_positions):
                    is_p = True
                    if 'SP' in eligible_positions:
                        is_sp = True
                    if 'RP' in eligible_positions:
                        is_rp = True
                    print(f"{player.name} identified as pitcher by eligible positions: SP={is_sp}, RP={is_rp}, P={is_p}")
                
                # Check default position as last resort
                if default_position in ['SP', 'RP', 'P']:
                    is_p = True
                    if default_position == 'SP':
                        is_sp = True
                    elif default_position == 'RP':
                        is_rp = True
                    print(f"{player.name} identified as pitcher by default position: {default_position}")
                
                # Determine final position(s)
                final_positions = []
                
                # First check for DH position
                if 'DH' in eligible_positions:
                    final_positions.append('DH')
                
                # Then add pitcher positions
                if is_sp:
                    final_positions.append('SP')
                if is_rp:
                    final_positions.append('RP')
                if is_p and not (is_sp or is_rp):
                    final_positions.append('P')
                
                # Only add non-pitcher positions if player is not identified as a pitcher
                if not (is_sp or is_rp or is_p):
                    # Include all non-pitcher positions except DH (already handled)
                    non_pitcher_positions = [pos for pos in eligible_positions 
                                          if pos not in ['SP', 'RP', 'P', 'DH']]
                    if non_pitcher_positions:
                        final_positions.extend(non_pitcher_positions)
                    elif default_position and default_position not in ['SP', 'RP', 'P', 'DH']:
                        final_positions.append(default_position)
                
                # Special case for Ohtani - ensure DH is included
                if player.name == "Shohei Ohtani" and 'DH' not in final_positions:
                    final_positions.append('DH')
                
                print(f"Final positions for {player.name}: {final_positions}")
                print(f"All eligible positions for {player.name}: {eligible_positions}")
                
                # Base player info with default values
                player_dict = {
                    'Team': team.team_name or '',
                    'Player': player.name,
                    'Position': ', '.join(sorted(set(final_positions), key=lambda x: ('DH' not in x, x))) or '',  # Sort positions but prioritize DH
                    'Pro Team': getattr(player, 'proTeam', ''),
                    'Slot': 'Bench' if any(slot_map.get(slot, '') == 'BE' for slot in raw_slots) else 'Starting',
                    'Injury Status': getattr(player, 'injuryStatus', ''),
                    'Next Start': 'Not Scheduled'
                }
                
                print(f"Created player dict: {player_dict}")
                
                # Add to pitching stats if player is any type of pitcher
                if is_sp or is_rp or is_p:
                    print(f"Processing {player.name} as pitcher")
                    pitcher_dict = player_dict.copy()
                    # Add Next Start info for Starting Pitchers
                    if is_sp:
                        next_start = None
                        if hasattr(player, 'nextStart'):
                            next_start = player.nextStart
                        elif hasattr(player, 'stats') and player.stats:
                            next_start = player.stats.get(0, {}).get('nextStart', None)
                        pitcher_dict['Next Start'] = next_start if next_start else 'Not Scheduled'
                    else:
                        pitcher_dict['Next Start'] = 'N/A'
                    
                    try:
                        pitcher_dict.update({
                            'ERA': f"{self._safe_float(stats_to_use.get('ERA', 0.0)):.3f}",
                            'WHIP': f"{self._safe_float(stats_to_use.get('WHIP', 0.0)):.3f}",
                            'W': self._safe_int(stats_to_use.get('W', 0)),
                            'L': self._safe_int(stats_to_use.get('L', 0)),
                            'SV': self._safe_int(stats_to_use.get('SV', 0)),
                            'HLD': self._safe_int(stats_to_use.get('HLD', 0)),
                            'K': self._safe_int(stats_to_use.get('K', 0)),
                            'K/9': f"{self._safe_float(stats_to_use.get('K/9', 0.0)):.1f}",
                            'K/BB': f"{self._safe_float(stats_to_use.get('K/BB', 0.0)):.1f}",
                            'QS': self._safe_int(stats_to_use.get('QS', 0))
                        })
                        print(f"Added pitcher {player.name} to pitching stats with ERA: {pitcher_dict['ERA']}")
                        pitching_stats.append(pitcher_dict)
                    except Exception as e:
                        print(f"Error converting pitching stats for {player.name}: {e}")
                        print(f"Raw stats: {stats_to_use}")
                
                # Add to batting stats if player is not exclusively a pitcher or has DH position
                if not (is_sp or is_rp or is_p) or 'DH' in eligible_positions or player.name == "Shohei Ohtani":
                    print(f"Processing {player.name} as batter")
                    batter_dict = player_dict.copy()
                    try:
                        batter_dict.update({
                            'AVG': f"{self._safe_float(stats_to_use.get('AVG', 0.0)):.3f}",
                            'HR': self._safe_int(stats_to_use.get('HR', 0)),
                            'RBI': self._safe_int(stats_to_use.get('RBI', 0)),
                            'R': self._safe_int(stats_to_use.get('R', 0)),
                            'SB': self._safe_int(stats_to_use.get('SB', 0)),
                            'OBP': f"{self._safe_float(stats_to_use.get('OBP', 0.0)):.3f}",
                            'SLG': f"{self._safe_float(stats_to_use.get('SLG', 0.0)):.3f}",
                            'OPS': f"{self._safe_float(stats_to_use.get('OPS', 0.0)):.3f}"
                        })
                        print(f"Added batter {player.name} to batting stats with AVG: {batter_dict['AVG']}")
                        batting_stats.append(batter_dict)
                    except Exception as e:
                        print(f"Error converting batting stats for {player.name}: {e}")
                        print(f"Raw stats: {stats_to_use}")
                
                print(f"Finished processing {player.name}\n")
        
        # Convert to DataFrames and handle NaN values immediately
        if batting_stats:
            batting_df = pd.DataFrame(batting_stats)
            # Ensure all columns are present and in correct order
            batting_df = batting_df.reindex(columns=batting_cols)
            # Fill NaN values appropriately
            for col in batting_cols:
                if col in ['AVG', 'OBP', 'SLG', 'OPS']:
                    batting_df[col] = batting_df[col].fillna('0.000')
                elif col in ['HR', 'RBI', 'R', 'SB']:
                    batting_df[col] = batting_df[col].fillna(0).astype(int)
                else:
                    batting_df[col] = batting_df[col].fillna('')
            
            batting_df = batting_df.sort_values('AVG', ascending=False)
        else:
            batting_df = pd.DataFrame()
            
        if pitching_stats:
            pitching_df = pd.DataFrame(pitching_stats)
            # Ensure all columns are present and in correct order
            pitching_df = pitching_df.reindex(columns=pitching_cols)
            # Fill NaN values appropriately
            for col in pitching_cols:
                if col in ['ERA', 'WHIP', 'K/9', 'K/BB']:
                    pitching_df[col] = pitching_df[col].fillna('0.000')
                elif col in ['W', 'L', 'SV', 'HLD', 'K', 'QS']:
                    pitching_df[col] = pitching_df[col].fillna(0).astype(int)
                else:
                    pitching_df[col] = pitching_df[col].fillna('')
            
            pitching_df = pitching_df.sort_values('ERA', ascending=True)
        else:
            pitching_df = pd.DataFrame()
        
        # Return appropriate DataFrame
        if batting_df.empty and pitching_df.empty:
            print("No players found with stats")
            return pd.DataFrame()  # Return empty DataFrame if no players found
        elif batting_df.empty:
            return pitching_df
        elif pitching_df.empty:
            return batting_df
        else:
            # Create blank row with all columns from pitching (which includes Next Start)
            blank_df = pd.DataFrame([[''] * len(pitching_cols)], columns=pitching_cols)
            
            # Combine DataFrames with consistent column ordering
            combined_df = pd.concat(
                [batting_df, blank_df, pitching_df],
                ignore_index=True
            ).fillna('')  # Final fillna to catch any remaining NaN values
            
            return combined_df

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
                "Injury Status": player.injuryStatus
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

    def _safe_float(self, value) -> float:
        """Safely convert a value to float, returning 0.0 if conversion fails"""
        if value is None or value == '':
            return 0.0
        try:
            if isinstance(value, str):
                # Remove any non-numeric characters except decimal point and negative sign
                value = ''.join(c for c in value if c.isdigit() or c in '.-')
                if not value:  # If string is empty after cleaning
                    return 0.0
            return float(value or 0.0)
        except (ValueError, TypeError):
            return 0.0

    def _safe_int(self, value) -> int:
        """Safely convert a value to int, returning 0 if conversion fails"""
        if value is None or value == '':
            return 0
        try:
            if isinstance(value, str):
                # Remove any non-numeric characters except negative sign
                value = ''.join(c for c in value if c.isdigit() or c == '-')
                if not value:  # If string is empty after cleaning
                    return 0
            return int(float(value or 0))
        except (ValueError, TypeError):
            return 0