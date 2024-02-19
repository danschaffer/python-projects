#!/usr/bin/env python
import argparse
import datetime
import pytz
import requests
import tzlocal
from operator import *
class Soccer:
    def __init__(self, league='eng.1', team=''):
        self.track_fixtures = True
        self.team = None
        if team:
            self.team = team.lower().replace('_',' ').split(',')
        self.league = league
        self.fixtures_data = []
        self.table_data = {}
        self.league_size = {
            'eng.1': 20,
            'ger.1': 18,
            'esp.1': 20,
            'fra.1': 20,
            'usa.1': 28,
            'mex.1': 18,
            'por.1': 18,
            'ned.1': 18,
            'ita.1': 20,
            'uefa.champions': 32,
            'uefa.europa': 32,
            'eng.fa': 20,
            'eng.league_cup': 20,
            'esp.copa_del_ray': 20,
            'eng.2': 24,
            'eng.3': 24,
            'bel.1': 18,
            'jpn.1': 18,
        }
        self.league_name = {
            'eng.1': 'English Premier League',
            'ger.1': 'German Bundesliga',
            'esp.1': 'Spanish La Liga',
            'fra.1': 'French Ligue 1',
            'usa.1': 'American MLS',
            'mex.1': 'Mexican Liga MX',
            'por.1': 'Portuguese Liga',
            'ned.1': 'Dutch Erediv',
            'ita.1': 'Italian Series A',
            'uefa.champions': 'European Champions',
            'uefa.europa': 'European Europa',
            'eng.fa': 'English FA Cup',
            'eng.league_cup': 'English League Cup',
            'esp.copa_del_ray': 'Spanish Copa Del Ray',
            'eng.2': 'British League Championship',
            'eng.3': 'British League One',
            'bel.1': 'Belgium First',
            'jpn.1': 'Japan J League',
        }

    def get_score(self, data):
        score = str(int(data['score']))
        if 'shootoutScore' in data:
            score += f" ({str(int(data['shootoutScore']))})"
        return score

    def get_record(self, obj):
        result = ''
        if 'records' in obj and 'summary' in obj['records'][0]:
            summary=obj['records'][0]['summary'].split('-')
            points=int(summary[0])*3+int(summary[1])
            result = f"({points}) "
        return result

    def get_schedule(self, days, verbose):
        _date = datetime.datetime.now() + datetime.timedelta(days=days)
        day = _date.strftime('%Y%m%d')
        daystr = _date.strftime('%m/%d')
        datePrinted = False
        data = requests.get(f"http://site.api.espn.com/apis/site/v2/sports/soccer/:league/scoreboard?league={self.league}&dates={day}").json()
        if 'events' not in data:
            return
        for event in data['events']:
            if not datePrinted and self.track_fixtures:
                self.fixtures_data.append(_date.strftime("%a %b %-d"))
                datePrinted =True
            name = event['name']
            if event['status']['type']['completed']:
                clock = ''
            else:
                clock = event['status']['displayClock']
            local_timezone = tzlocal.get_localzone()
            utc_time = datetime.datetime.strptime(event['date'], '%Y-%m-%dT%H:%MZ')
            local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
            _tm = local_time.strftime("%-I:%M") + local_time.strftime("%p")[0].lower()
            score = ""
            teams = {}
            if clock != "0'":
                competition = event['competitions'][0]
                if competition['competitors'][0]['homeAway'] == 'home':
                    home = f"{competition['competitors'][0]['team']['shortDisplayName']} {self.get_score(competition['competitors'][0])}"
                    away = f"{competition['competitors'][1]['team']['shortDisplayName']} {self.get_score(competition['competitors'][1])}"
                else:
                    away = f"{competition['competitors'][0]['team']['shortDisplayName']}{self.get_score(competition['competitors'][0])}"
                    home = f"{competition['competitors'][1]['team']['shortDisplayName']}{self.get_score(competition['competitors'][1])}"
                teams[competition['competitors'][0]['id']] = competition['competitors'][0]['team']['abbreviation']
                teams[competition['competitors'][1]['id']] = competition['competitors'][1]['team']['abbreviation']
                if self.track_fixtures:
                    self.fixtures_data.append(f"{daystr} {away} at {home} {clock}")
                if verbose:
                    for detail in competition['details']:
                        desc = "  " + detail['type']['text']
                        desc += " " + detail['clock']['displayValue']
                        if 'athletesInvolved' in detail and len(detail['athletesInvolved'])>0:
                            desc += " " + detail['athletesInvolved'][0]['displayName']
                            desc += " " + teams[detail['athletesInvolved'][0]['team']['id']]
                        if self.track_fixtures:
                            self.fixtures_data.append(desc)

            else:
                competition = event['competitions'][0]
                if competition['competitors'][0]['homeAway'] == 'home':
                    home = f"{competition['competitors'][0]['team']['shortDisplayName']}"
                    away = f"{competition['competitors'][1]['team']['shortDisplayName']}"
                else:
                    away = f"{competition['competitors'][0]['team']['shortDisplayName']}"
                    home = f"{competition['competitors'][1]['team']['shortDisplayName']}"
                if self.track_fixtures:
                    self.fixtures_data.append(f"{daystr} {away} at {home} {_tm}")
            for competitor in event['competitions'][0]['competitors']:
                if 'records' not in competitor:
                    break
                record = competitor['records'][0]['summary']
                team = competitor['team']['name']
                tokens = record.split('-')
                wins = int(tokens[0])
                draws = int(tokens[1])
                losses = int(tokens[2])
                points = wins * 3 + draws
                self.table_data[team] = {'team': team, 'record': record, 'wins': wins, 'losses': losses, 'draws': draws, 'points': points}

    def match(self, team):
        for match in self.team:
            if team.lower().find(match.lower()) > -1:
                return True
        return False

    def fixtures(self, start, end, verbose):
        for count in range(start, end):
            self.get_schedule(count, verbose)
        league_len = self.league_size.get(self.league, 10)
        self.track_fixtures = False
        if len(self.table_data.keys()) == 0:
            return
        while len(self.table_data.keys()) < league_len:
            start -= 1
#            print(f"{start} {len(self.table_data.keys())}")
            self.get_schedule(start, False)

    def display_fixtures(self):
        for line in self.fixtures_data:
            if self.team is None or self.match(line):
                print(line)

    def display_table(self):
        for team in sorted(self.table_data.items(), key=lambda x:getitem(x[1],'points'), reverse=True):
            if self.team is None or self.match(team[1]['team']):
                print(f"{team[1]['team']:28} {team[1]['points']:3} {team[1]['record']}")
    
    def table(self):
        data = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/:league/teams?league={self.league}").json()
        print(data['sports'][0]['leagues'][0]['name'])
        table = []
        for team in data['sports'][0]['leagues'][0]['teams']:
            name = team['team']['name']
            if 'record' not in team['team'] or 'items' not in team['team']['record']:
                continue
            record = team['team']['record']['items'][0]['summary']
            for stat in team['team']['record']['items'][0]['stats']:
                if stat['name'] == 'gamesPlayed':
                    games = int(stat['value'])
                elif stat['name'] == 'points':
                    points = int(stat['value'])
            table.append({'name':name, 'points': points, 'record': record, 'games': games})
        for team in sorted(table, key=lambda k: k['points'], reverse=True):
            print(f"{team['name']:<25} {team['points']:<3} {team['games']:<3} {team['record']}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--league', default="eng.1", help="league name eng.1,ger.1,esp.1,fra.1,usa.1,mex.1,por.1,ned.1,ita.1,uefa.champions,uefa.europa,eng.fa,eng.league_cup,eng.2,eng.3")
    parser.add_argument('--team', help="show team")
    parser.add_argument('--start', type=int, default=-2, help="start number of days")
    parser.add_argument('--end', type=int, default=3, help="end number of days")
    parser.add_argument('--verbose', action='store_true', help='increase verbosity')
    parser.add_argument('--fixtures', action='store_true', help='show fixtures')
    parser.add_argument('--table', action='store_true', help='show table')
    pargs = parser.parse_args()
    if not pargs.fixtures and not pargs.table:
        pargs.fixtures = pargs.table = True
    soccer = Soccer(pargs.league, pargs.team)
    soccer.fixtures(pargs.start, pargs.end, pargs.verbose)
    name = soccer.league_name.get(pargs.league, 'unknown')
    print(f"{name} - {pargs.league}")
    if pargs.fixtures:
        soccer.display_fixtures()
    if pargs.table:
        soccer.display_table()

