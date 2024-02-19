#!/usr/bin/env python

import argparse
import datetime
import pytz
import requests
import tzlocal
import sys
class Nfl:
    def __init__(self):
       self.records = {}  # team: {'wins': '', 'losses': '', 'pct': ''}
       self.conf = ['afc east', 'afc north', 'afc south', 'afc west', 'nfc east', 'nfc north', 'nfc south', 'nfc west']
       self.teams = {
            'mia': 'afc east', 
            'buf': 'afc east',
            'nyj': 'afc east', 
            'ne' : 'afc east', 
            'cle': 'afc north', 
            'cin': 'afc north', 
            'bal': 'afc north', 
            'pit': 'afc north', 
            'jax': 'afc south',
            'ten': 'afc south',
            'ind': 'afc south',
            'hou': 'afc south',
            'kc' : 'afc west',
            'lac': 'afc west',
            'den': 'afc west',
            'lv' : 'afc west',
            'phi': 'nfc east',
            'dal': 'nfc east',
            'nyg': 'nfc east',
            'wsh': 'nfc east',
            'min': 'nfc north',
            'gb' : 'nfc north',
            'chi': 'nfc north',
            'det': 'nfc north',
            'tb' : 'nfc south',
            'atl': 'nfc south',
            'car': 'nfc south',
            'no' : 'nfc south',
            'sf' : 'nfc west',
            'lar': 'nfc west',
            'ari': 'nfc west',
            'sea': 'nfc west',
        }

    def get_schedule(self, day, verbose=False, teamsmatch=[], quiet=False):
        datePrinted = False
        data = requests.get(f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={day}").json()
        for event in data['events']:
            record1 = record2 = None
            if not datePrinted:
                if not quiet:
                    print(f"{day[0:4]}-{day[4:6]}-{day[6:8]}")
                datePrinted =True
            status = event['status']['type']['shortDetail']
            team1 = event['competitions'][0]['competitors'][0]['team']['abbreviation'].lower()
            score1 = int(event['competitions'][0]['competitors'][0]['score'])
            for record in event['competitions'][0]['competitors'][0]['records']:
                if record['name'] == 'All Splits' or record['name'].lower() == 'ytd' or record['name'] == 'overall':
                    record1 = record['summary']
            team2 = event['competitions'][0]['competitors'][1]['team']['abbreviation'].lower()
            score2 = int(event['competitions'][0]['competitors'][1]['score'])
            for record in event['competitions'][0]['competitors'][1]['records']:
                if record['name'] == 'All Splits' or record['name'].lower() == 'ytd' or record['name'] == 'overall':
                    record2 = record['summary']
            if team1 not in self.records:
                self.records[team1] = record1
            if team2 not in self.records:
                self.records[team2] = record2
            if quiet:
                continue
            if score1 > score2:
                print(f"{team1:3} {'('+record1+')':8} {score1:2} {team2:3} {'('+record2+')':8} {score2:2} {status}")
            else:
                print(f"{team2:3} {'('+record2+')':8} {score2:2} {team1:3} {'('+record1+')':8} {score1:2} {status}")

    def schedules(self, week, verbose=False, quiet=False, teams=[]):
      if teams == '':
        teams = []
      else:
        teams = teams.split(',')
      for day in self.get_week(week):
        self.get_schedule(day, verbose=verbose, teamsmatch=teams, quiet=quiet)
      if not quiet:
        byes = []
        for team in self.teams:
          if team not in self.records:
            byes.append(team)
        if len(byes)>1:
          print("byes: " + ','.join(byes))

    def standings(self, week):
        print()
        while len(self.records) < 32:
            week -= 1
            assert week > 0
            self.schedules(week, quiet=True, teams='')
        lines = ['','','','','']
        for conf in self.conf:
            teams = []
            lines[0] += (f"{conf:10}")
            for team in self.teams:
                if self.teams[team] == conf:
                    wins = int(self.records[team].split('-')[0])
                    record = self.records[team]
                    teams.append({'wins': wins, 'name': team, 'record': record})
                    teams.sort(key=lambda d: d['wins'], reverse=True)
            for i,s in enumerate(teams):
                lines[i+1] +=  str(f"{s['name']:3} {s['record']:6}")
            if conf == "afc west" or conf == "nfc west":
                for line in lines:
                    print(line)
                lines = ['','','','','']


    def get_week(self, week):
        result = []
        start = datetime.datetime(2023, 9, 7)
        for i in range(7):
            result.append((start + datetime.timedelta(days=(week-1)*7+i)).strftime("%Y%m%d"))
        if week == 1:
            del(result[0])
        if week == 18:
            result.append('2023011')
        return result

    def get_week_from_day(self, day=None):
        if not day:
            day = datetime.datetime.now().strftime('%Y%m%d')
        for i in range(1,19):
            week = self.get_week(i)
            if day in week:
                return i

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true', help='increase verbosity')
    parser.add_argument('--week', help='show schedule')
    parser.add_argument('--schedule', action='store_true', help='show schedule')
    parser.add_argument('--standings', action='store_true', help='show standings')
    parser.add_argument('--teams', default='', help='teams')
    pargs = parser.parse_args()
    if not pargs.schedule and not pargs.standings:
        pargs.schedule = pargs.standings = True
    nfl = Nfl()
    if not pargs.week:
        week = nfl.get_week_from_day()
    else:
        week = int(pargs.week)
    if not week:
        print("season is over")
        sys.exit(1)
    print(f"week {week}")
    if pargs.schedule:
        nfl.schedules(week, verbose=pargs.verbose, teams=pargs.teams, quiet=False)
    if pargs.standings:
        nfl.standings(week)
