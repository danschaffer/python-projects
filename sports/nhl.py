#!/usr/bin/env python

import argparse
import datetime
import pytz
import requests
import tzlocal
class Nhl:
    def __init__(self):
        pass

    def get_schedule(self, days, verbose):
        _date = datetime.datetime.now() + datetime.timedelta(days=days)
        day = _date.strftime('%Y%m%d')
        datePrinted = False
        data = requests.get(f"http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard?dates={day}").json()
        for event in data['events']:
            if not datePrinted:
                print(_date.strftime("%a %b %-d"))
                datePrinted =True
            if event['status']['type']['completed']:
                clock = ''
            else:
                clock = event['status']['displayClock']
                period = event['status']['period']
            local_timezone = tzlocal.get_localzone()
            utc_time = datetime.datetime.strptime(event['date'], '%Y-%m-%dT%H:%MZ')
            local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
            _tm = local_time.strftime("%-I:%M") + local_time.strftime("%p")[0].lower()
            score = ""
            teams = {}
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
                print(f"{away} at {home} {clock}")
                if verbose:
                    for team in competition['competitors']:
                        for leader in team['leaders']:
                            print(f"  {teams[leader['leaders'][0]['athlete']['team']['id']]} {leader['shortDisplayName']} {leader['leaders'][0]['athlete']['displayName']} {leader['leaders'][0]['displayValue']}")
            else:
                competition = event['competitions'][0]
                if competition['competitors'][0]['homeAway'] == 'home':
                    home = f"{competition['competitors'][0]['team']['shortDisplayName']}({competition['competitors'][0]['records'][0]['summary']})"
                    away = f"{competition['competitors'][1]['team']['shortDisplayName']}({competition['competitors'][1]['records'][0]['summary']})"
                else:
                    away = f"{competition['competitors'][0]['team']['shortDisplayName']}({competition['competitors'][0]['records'][0]['summary']})"
                    home = f"{competition['competitors'][1]['team']['shortDisplayName']}({competition['competitors'][1]['records'][0]['summary']})"
                print(f"{away} at {home} {_tm}")

    def schedules(self, start, end, verbose):
        for count in range(start, end):
            self.get_schedule(count, verbose)

    def standings(self):
        data = requests.get('http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/teams').json()
        print(data['sports'][0]['leagues'][0]['name'])
        standings = []
        for team in data['sports'][0]['leagues'][0]['teams']:
            name = team['team']['name']
            if 'items' not in team['team']['record']:
                continue
            record = team['team']['record']['items'][0]['summary']
            for stat in team['team']['record']['items'][0]['stats']:
                if stat['name'] == 'playoffSeed':
                    seed = int(stat['value'])
                elif stat['name'] == 'points':
                    points = int(stat['value'])
                elif stat['name'] == 'winPercent':
                    winPercent = float(stat['value'])
            standings.append({'name': name, 'record': record, 'winPercent': winPercent, 'seed': seed, 'points': points})
        for team in sorted(standings, key=lambda k: k['points'], reverse=True):
            print(f"{team['name']:<14} {team['points']:<3} {team['record']:<6} {int(100*team['winPercent']):<3} {team['seed']:<4}")

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
    hockey = Nhl()
    if pargs.standings:
        hockey.standings()
    if pargs.schedule:
        hockey.schedules(pargs.start, pargs.end, pargs.verbose)
