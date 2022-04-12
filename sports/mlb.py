#!/usr/bin/env python

import argparse
import datetime
import pytz
import requests
import tzlocal
class Mlb:
    def __init__(self):
        pass

    def get_schedule(self, days, verbose):
        _date = datetime.datetime.now() + datetime.timedelta(days=days)
        day = _date.strftime('%Y%m%d')
        datePrinted = False
        data = requests.get(f"http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={day}").json()
        teams = {}
        for event in data['events']:
            pitching = ''
            if not datePrinted:
                print(_date.strftime("%a %b %-d"))
                datePrinted =True
            if event['status']['type']['completed']:
                clock = ''
                inning = ''
                start = ''
            else:
                clock = event['status']['displayClock']
                inning = event['status']['period']
            local_timezone = tzlocal.get_localzone()
            utc_time = datetime.datetime.strptime(event['date'], '%Y-%m-%dT%H:%MZ')
            local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
            _tm = local_time.strftime("%-I:%M") + local_time.strftime("%p")[0].lower()
            competition = event['competitions'][0]
            teams[competition['competitors'][0]['id']] = competition['competitors'][0]['team']['abbreviation']
            teams[competition['competitors'][1]['id']] = competition['competitors'][1]['team']['abbreviation']
            if verbose:
                if 'probables' in competition['competitors'][0]:
                    team = teams[competition['competitors'][0]['probables'][0]['athlete']['team']['id']]
                    name = competition['competitors'][0]['probables'][0]['athlete']['displayName']
                    pos = competition['competitors'][0]['probables'][0]['athlete']['position']
                    wins = losses = era = ''
                    for stat in competition['competitors'][0]['probables'][0]['statistics']:
                        if stat['name'] == 'wins':
                            wins = stat['displayValue']
                        if stat['name'] == 'losses':
                            losses = stat['displayValue']
                        if stat['name'] == 'ERA':
                            era = stat['displayValue']
                    pitching += f"\n  {team} {name} {pos} {wins}-{losses} {era}"
                    team = teams[competition['competitors'][1]['probables'][0]['athlete']['team']['id']]
                    name = competition['competitors'][1]['probables'][0]['athlete']['displayName']
                    pos = competition['competitors'][1]['probables'][0]['athlete']['position']
                    wins = losses = era = ''
                    for stat in competition['competitors'][1]['probables'][0]['statistics']:
                        if stat['name'] == 'wins':
                            wins = stat['displayValue']
                        if stat['name'] == 'losses':
                            losses = stat['displayValue']
                        if stat['name'] == 'ERA':
                            era = stat['displayValue']
                    pitching += f"\n  {team} {name} {pos} {wins}-{losses} {era}"
            score = ""
            if clock != '0:00':
                competition = event['competitions'][0]
                if competition['competitors'][0]['homeAway'] == 'home':
                    home = f"{competition['competitors'][0]['team']['shortDisplayName']}({competition['competitors'][0]['records'][0]['summary']}) {competition['competitors'][0]['score']}"
                    away = f"{competition['competitors'][1]['team']['shortDisplayName']}({competition['competitors'][1]['records'][0]['summary']}) {competition['competitors'][1]['score']}"
                else:
                    away = f"{competition['competitors'][0]['team']['shortDisplayName']}({competition['competitors'][0]['records'][0]['summary']}) {competition['competitors'][1]['score']}"
                    home = f"{competition['competitors'][1]['team']['shortDisplayName']}({competition['competitors'][1]['records'][0]['summary']}) {competition['competitors'][0]['score']}"
                teams[competition['competitors'][0]['id']] = competition['competitors'][0]['team']['abbreviation']
                teams[competition['competitors'][1]['id']] = competition['competitors'][1]['team']['abbreviation']
                if verbose:
                    if 'featuredAthletes' in competition['status']:
                        for athlete in competition['status']['featuredAthletes']:
                            team = teams[athlete['athlete']['team']['id']]
                            name = athlete['athlete']['displayName']
                            pos = athlete['athlete']['position']
                            event = athlete['displayName']
                            wins = losses = era = ''
                            for stat in athlete['statistics']:
                                if stat['name'] == 'wins':
                                    wins = stat['displayValue']
                                if stat['name'] == 'losses':
                                    losses = stat['displayValue']
                                if stat['name'] == 'ERA':
                                    era = stat['displayValue']
                            pitching += f"\n  {event} {team} {name} {pos} {wins}-{losses} {era}"
                    for team in competition['competitors']:
                        if 'leaders' in team:
                            for leader in team['leaders']:
                                if leader['leaders'][0]['value'] > 0:
                                    team = ""
                                    if leader['leaders'][0]['athlete']['team']['id'] in teams:
                                        team = teams[leader['leaders'][0]['athlete']['team']['id']]
                                    value = str(leader['leaders'][0]['value'])
                                    if value.endswith('.0'):
                                        value = value[:-2]
                                    if len(value)>5:
                                        value = str(round(leader['leaders'][0]['value'],3))[1:]
                                    print(f"  {team} {leader['displayName']} {value} {leader['leaders'][0]['athlete']['displayName']} {leader['leaders'][0]['athlete']['position']['abbreviation']} {leader['leaders'][0]['displayValue']}")
                print(f"{away} at {home} {inning} {clock}{pitching}")
            else:
                competition = event['competitions'][0]
                if competition['competitors'][0]['homeAway'] == 'home':
                    home = f"{competition['competitors'][0]['team']['shortDisplayName']}({competition['competitors'][0]['records'][0]['summary']})"
                    away = f"{competition['competitors'][1]['team']['shortDisplayName']}({competition['competitors'][1]['records'][0]['summary']})"
                else:
                    away = f"{competition['competitors'][0]['team']['shortDisplayName']}({competition['competitors'][0]['records'][0]['summary']})"
                    home = f"{competition['competitors'][1]['team']['shortDisplayName']}({competition['competitors'][1]['records'][0]['summary']})"
                print(f"{away} at {home} {_tm}{pitching}")

    def schedules(self, start, end, verbose):
        for count in range(start, end):
            self.get_schedule(count, verbose)

    def standings(self):
        divisions = ['al east', 'al central', 'al west', 'nl east', 'nl central', 'nl west']
        standings = {'al east': [], 'al central': [], 'al west': [], 'nl east': [], 'nl central': [], 'nl west': []}
        teams = {
            'Padres': 'nl west', 
            'Astros': 'al west',
            'Phillies': 'nl east', 
            'Blue Jays': 'al east', 
            'Cubs': 'nl central', 
            'White Sox': 'al central', 
            'Cardinals': 'nl central', 
            'Mets': 'nl east', 
            'Reds': 'nl central',
            'Guardians': 'al central',
            'Tigers': 'al central',
            'Royals': 'al central',
            'Twins': 'al central',
            'Yankees': 'al east',
            'Athletics': 'al west',
            'Mariners': 'al west',
            'Braves': 'nl east',
            'Angels': 'al west',
            'Nationals': 'nl east',
            'Dodgers': 'nl west',
            'Pirates': 'nl east',
            'Orioles': 'al east',
            'Red Sox': 'al east',
            'Brewers': 'nl central',
            'Rangers': 'al west',
            'Rockies': 'nl west',
            'Diamondbacks': 'nl west',
            'Marlins': 'nl east',
            'Giants': 'nl west',
            'Rays': 'al east',
        }
        for page in range(1,3):
            data = requests.get(f"http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams?page={page}").json()
            for team in data['sports'][0]['leagues'][0]['teams']:
                name = team['team']['name']
                print(name)
                if 'items' not in team['team']['record']:
                    continue
                record = team['team']['record']['items'][0]['summary']
                for stat in team['team']['record']['items'][0]['stats']:
                    if stat['name'] == 'playoffSeed':
                        seed = int(stat['value'])
                    elif stat['name'] == 'divisionGamesBehind':
                        gamesBehind = int(stat['value'])
                    elif stat['name'] == 'winPercent':
                        winPercent = float(stat['value'])
                standings[teams[name]].append({'name': name, 'record': record, 'winPercent': winPercent, 'seed': seed, 'gamesBehind': gamesBehind})
        for division in divisions:
            print(division)
            for team in sorted(standings[division], key=lambda k: k['winPercent'], reverse=True):
                print(f"{team['name']:<14} {team['record']:<6} {int(100*team['winPercent']):<3} {team['gamesBehind']:<3} {team['seed']:<4}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=-1, help="start number of days")
    parser.add_argument('--end', type=int, default=1, help="end number of days")
    parser.add_argument('--verbose', action='store_true', help='increase verbosity')
    parser.add_argument('--schedule', action='store_true', help='show schedule')
    parser.add_argument('--standings', action='store_true', help='show standings')
    pargs = parser.parse_args()
    if not pargs.schedule and not pargs.standings:
        pargs.schedule = pargs.standings = True
    soccer = Mlb()
    if pargs.standings:
        soccer.standings()
    if pargs.schedule:
        soccer.schedules(pargs.start, pargs.end, pargs.verbose)
