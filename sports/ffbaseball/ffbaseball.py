#!/usr/bin/env python3

import click
from espn_api_client import ESPNFantasyBaseball
from tabulate import tabulate
from typing import Optional
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

@click.group()
@click.option('--league-id', default=87636, help='ESPN league ID')
@click.option('--espn-s2', help='ESPN S2 cookie for private leagues')
@click.option('--swid', help='ESPN SWID cookie for private leagues')
@click.pass_context
def cli(ctx, league_id: int, espn_s2: Optional[str], swid: Optional[str]):
    """ESPN Fantasy Baseball Statistics Tracker"""
    ctx.ensure_object(dict)
    ctx.obj['client'] = ESPNFantasyBaseball(
        league_id=league_id,
        espn_s2=espn_s2,
        swid=swid
    )

@cli.command()
@click.pass_context
def matchup(ctx):
    """Display current matchup statistics"""
    client = ctx.obj['client']
    matchups = client.get_current_matchup()
    
    if not matchups:
        print("\nNo active matchups found. This could be because:")
        print("- It's currently between matchup periods")
        print("- The season hasn't started yet")
        print("- The season is over")
        print("- There might be an issue with the ESPN API authentication")
        return

    for matchup in matchups:
        print(f"\nMatchup: {matchup['home_team']} vs {matchup['away_team']}")
        print(f"Score: {matchup['home_score']} - {matchup['away_score']}")
        
        # Prepare detailed stats table
        stats_data = []
        all_categories = set()
        
        # Collect all stat categories
        for stats in [matchup['home_stats'], matchup['away_stats']]:
            all_categories.update(stats.keys())
        
        # Sort categories for consistent display
        categories = sorted(all_categories)
        
        # Create rows for each category
        for category in categories:
            home_value = matchup['home_stats'].get(category, '-')
            away_value = matchup['away_stats'].get(category, '-')
            stats_data.append([
                category,
                home_value,
                away_value
            ])
        
        if stats_data:
            print("\nDetailed Statistics:")
            print(tabulate(
                stats_data,
                headers=['Category', matchup['home_team'], matchup['away_team']],
                tablefmt='grid',
                numalign='right'
            ))
        print("\n" + "="*50)

@cli.command()
@click.option('--team-id', type=int, help='Team ID to show stats for')
@click.pass_context
def team(ctx, team_id: Optional[int]):
    """Display team summary and player statistics"""
    client = ctx.obj['client']
    
    # Get team stats
    team_stats = client.get_team_stats(team_id)
    if team_stats.empty:
        print(f"\nNo team found with ID {team_id}")
        return
        
    print("\nTeam Statistics:")
    print(tabulate(team_stats, headers='keys', tablefmt='grid', showindex=False))
    
    # Get player stats
    player_stats = client.get_player_stats(team_id)
    if not player_stats.empty:
        # Format numeric columns
        for col in player_stats.columns:
            if col in ['AVG', 'OBP', 'SLG', 'OPS', 'ERA', 'WHIP', 'K/9', 'K/BB']:
                player_stats[col] = player_stats[col].apply(lambda x: f"{float(x):.3f}" if pd.notnull(x) else "0.000")
            elif col in ['HR', 'RBI', 'R', 'SB', 'W', 'L', 'SV', 'HLD', 'K', 'QS']:
                player_stats[col] = player_stats[col].apply(lambda x: f"{int(x)}" if pd.notnull(x) else "0")
        
        # Convert boolean Injured column to Yes/No
        player_stats['Injured'] = player_stats['Injured'].map({True: 'Yes', False: 'No'})
        
        # Set column widths
        col_widths = {
            'Player': 20,
            'Position': 8,
            'Pro Team': 8,
            'Eligible Positions': 20,
            'Injury Status': 12
        }
        
        # Add stat column widths
        stat_cols = [col for col in player_stats.columns if col not in col_widths.keys()]
        for col in stat_cols:
            col_widths[col] = 6
        
        # Display columns in order
        display_columns = [
            'Player', 'Position', 'Pro Team', 'Eligible Positions', 
            'Injured', 'Injury Status'
        ]
        
        # Add any additional stat columns that exist
        stat_columns = [col for col in player_stats.columns if col not in display_columns + ['Team']]
        display_columns.extend(stat_columns)
        
        # Filter out any columns that don't exist
        display_columns = [col for col in display_columns if col in player_stats.columns]
        
        print("\nRoster:")
        print(tabulate(
            player_stats[display_columns],
            headers='keys',
            tablefmt='simple',
            showindex=False,
            maxcolwidths=[col_widths.get(col, None) for col in display_columns],
            numalign='right',
            stralign='left'
        ))

@cli.command()
@click.pass_context
def season(ctx):
    """Display season-long statistics for all teams"""
    client = ctx.obj['client']
    
    # Get all team stats
    team_stats = client.get_team_stats()
    print("\nSeason Statistics:")
    print(tabulate(team_stats, headers='keys', tablefmt='grid', showindex=False))

@cli.command()
@click.pass_context
def schedule(ctx):
    """Display the full season matchup schedule"""
    client = ctx.obj['client']
    schedule = client.get_season_schedule()
    
    if not schedule:
        print("\nNo schedule found. This could be because:")
        print("- The season schedule hasn't been generated yet")
        print("- The season hasn't started")
        print("- There might be an issue with the ESPN API authentication")
        return

    # Group matchups by week
    current_week = None
    for matchup in schedule:
        if current_week != matchup['week']:
            current_week = matchup['week']
            print(f"\nWeek {current_week}:")
            print("-" * 50)
        
        # Format scores if they exist
        score_str = ""
        if matchup['home_score'] > 0 or matchup['away_score'] > 0:
            score_str = f" (Score: {matchup['home_score']} - {matchup['away_score']})"
            
        print(f"{matchup['home_team']} vs {matchup['away_team']}{score_str}")

@cli.command()
@click.option('--position', '-p', help='Filter by position (e.g., SP, 1B, OF)')
@click.option('--season', '-s', type=int, default=2025, help='Season year (2024 or 2025)')
@click.pass_context
def free_agents(ctx, position: Optional[str], season: int):
    """Display best available free agents, optionally filtered by position"""
    client = ctx.obj['client']
    
    # Validate season
    if season not in [2024, 2025]:
        print("\nError: Season must be either 2024 or 2025")
        return
    
    # Get free agents
    free_agents = client.get_free_agents(position, season)
    
    if free_agents.empty:
        print("\nNo free agents found. This could be because:")
        print("- There are no available players matching your criteria")
        print("- The season hasn't started")
        print("- There might be an issue with the ESPN API authentication")
        return
    
    # Format numeric columns
    for col in free_agents.columns:
        if col in ['AVG', 'OBP', 'SLG', 'OPS', 'ERA', 'WHIP', 'K/9', 'K/BB']:
            free_agents[col] = free_agents[col].apply(lambda x: f"{float(x):.3f}" if pd.notnull(x) else "0.000")
        elif col in ['HR', 'RBI', 'R', 'SB', 'W', 'L', 'SV', 'HLD', 'K', 'QS']:
            free_agents[col] = free_agents[col].apply(lambda x: f"{int(x)}" if pd.notnull(x) else "0")
    
    # Set column widths
    col_widths = {
        'Player': 20,
        'Position': 8,
        'Pro Team': 8,
        'Injury Status': 12,
    }
    
    # Add stat column widths
    stat_cols = [col for col in free_agents.columns if col not in col_widths.keys()]
    for col in stat_cols:
        col_widths[col] = 6
    
    # Convert boolean Injured column to Yes/No
    free_agents['Injured'] = free_agents['Injured'].map({True: 'Yes', False: 'No'})
    
    print(f"\nBest Available{f' {position}' if position else ''} Players ({season} Season):")
    print(tabulate(
        free_agents,
        headers='keys',
        tablefmt='simple',
        showindex=False,
        maxcolwidths=[col_widths.get(col, None) for col in free_agents.columns],
        numalign='right',
        stralign='left'
    ))

if __name__ == '__main__':
    cli(obj={}) 