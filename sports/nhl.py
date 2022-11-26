#!/usr/bin/env python

import argparse
import datetime
import pytz
import requests
import tzlocal
class Nhl:
    def __init__(self):
        self.records = {}
        self.divisions = {
            'Eastern/Atlantic': ['Bruins','Maple Leafs','Red Wings','Lightning','Canadiens','Panthers','Sabres','Senators'],
            'Eastern/Metropolitan': ['Devils','Islanders','Penguins','Hurricanes','Rangers','Capitals','Flyers','Blue Jackets'],
            'Western/Central': ['Stars','Jets','Avalanche','Blues','Predators','Wild','Coyotes','Blackhawks'],
            'Western/Pacific': ['Golden Knights','Kraken','Kings','Flames','Oilers','Canucks','Sharks','Ducks']
        }
    def get_schedule(self, days, verbose=False, silent=False):
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
                self.add_record(competition['competitors'][0]['team']['shortDisplayName'], competition['competitors'][0]['records'][0]['summary'])
                self.add_record(competition['competitors'][1]['team']['shortDisplayName'], competition['competitors'][1]['records'][0]['summary'])
                teams[competition['competitors'][0]['id']] = competition['competitors'][0]['team']['abbreviation']
                teams[competition['competitors'][1]['id']] = competition['competitors'][1]['team']['abbreviation']
                if not silent:
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
                self.add_record(competition['competitors'][0]['team']['shortDisplayName'], competition['competitors'][0]['records'][0]['summary'])
                self.add_record(competition['competitors'][1]['team']['shortDisplayName'], competition['competitors'][1]['records'][0]['summary'])
                if not silent:
                    print(f"{away} at {home} {_tm}")

    def add_record(self, team, record):
        if team in self.records:
            return
        if record.startswith('('):
            record = record[1,-1]
        tokens = record.split('-')
        wins = int(tokens[0])
        draws = int(tokens[2])
        points = wins * 2 + draws
        self.records[team] = (team, points, record)

    def schedules(self, start, end, verbose, silent=False):
        for count in range(start, end):
            self.get_schedule(count, verbose, silent)

    def standings(self, start):
        while len(self.records) < 32:
            start -= 1
            self.schedules(start, start-1, verbose=False, silent=True)
        for divi in self.divisions:
            print(divi)
            teams = []
            for team in self.divisions[divi]:
                teams.append(self.records[team])
            teams.sort(key=lambda d: d[1], reverse=True)
            for team in teams:
                print(f"{team[0]:15} {team[2]:10} {team[1]:3}")

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
    if pargs.schedule:
        hockey.schedules(pargs.start, pargs.end, pargs.verbose)
    if pargs.standings:
        hockey.standings(pargs.start)
