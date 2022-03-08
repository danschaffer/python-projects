#!/usr/bin/env python
import argparse
import datetime
import pytz
import requests
import tzlocal
class Soccer:
    def __init__(self, league='eng.1'):
        self.league = league

    def get_score(self, data):
        score = str(int(data['score']))
        if 'shootoutScore' in data:
            score += f" ({str(int(data['shootoutScore']))})"
        return score

    def get_schedule(self, days, verbose):
        _date = datetime.datetime.now() + datetime.timedelta(days=days)
        day = _date.strftime('%Y%m%d')
        datePrinted = False
        data = requests.get(f"http://site.api.espn.com/apis/site/v2/sports/soccer/:league/scoreboard?league={self.league}&dates={day}").json()
        for event in data['events']:
            if not datePrinted:
                print(_date.strftime("%a %b %-d"))
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
                    away = f"{competition['competitors'][0]['team']['shortDisplayName']} {self.get_score(competition['competitors'][0])}"
                    home = f"{competition['competitors'][1]['team']['shortDisplayName']} {self.get_score(competition['competitors'][1])}"
                teams[competition['competitors'][0]['id']] = competition['competitors'][0]['team']['abbreviation']
                teams[competition['competitors'][1]['id']] = competition['competitors'][1]['team']['abbreviation']
                print(f"{away} at {home} {clock}")
                if verbose:
                    for detail in competition['details']:
                        desc = "  " + detail['type']['text']
                        desc += " " + detail['clock']['displayValue']
                        if 'athletesInvolved' in detail and len(detail['athletesInvolved'])>0:
                            desc += " " + detail['athletesInvolved'][0]['displayName']
                            desc += " " + teams[detail['athletesInvolved'][0]['team']['id']]
                        print(desc)

            else:
                competition = event['competitions'][0]
                if competition['competitors'][0]['homeAway'] == 'home':
                    home = f"{competition['competitors'][0]['team']['shortDisplayName']}"
                    away = f"{competition['competitors'][1]['team']['shortDisplayName']}"
                else:
                    away = f"{competition['competitors'][0]['team']['shortDisplayName']}"
                    home = f"{competition['competitors'][1]['team']['shortDisplayName']}"
                print(f"{away} at {home} {_tm}")

    def fixtures(self, start, end, verbose):
        for count in range(start, end):
            self.get_schedule(count, verbose)

    def table(self):
        data = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/:league/teams?league={self.league}").json()
        print(data['sports'][0]['leagues'][0]['name'])
        table = []
        for team in data['sports'][0]['leagues'][0]['teams']:
            name = team['team']['name']
            if 'items' not in team['team']['record']:
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
    parser.add_argument('--league', default="eng.1", help="league name eng.1,ger.1,esp.1,fra.1,usa.1,mex.1,por.1,ned.1,ita.1,uefa.champions,uefa.europa,eng.fa,eng.league_cup,esp.copa_del_ray,us.open")
    parser.add_argument('--start', type=int, default=-2, help="start number of days")
    parser.add_argument('--end', type=int, default=3, help="end number of days")
    parser.add_argument('--verbose', action='store_true', help='increase verbosity')
    parser.add_argument('--fixtures', action='store_true', help='show fixtures')
    parser.add_argument('--table', action='store_true', help='show table')
    pargs = parser.parse_args()
    if not pargs.fixtures and not pargs.table:
        pargs.fixtures = pargs.table = True
    soccer = Soccer(pargs.league)
    if pargs.table:
        soccer.table()
    if pargs.fixtures:
        soccer.fixtures(pargs.start, pargs.end, pargs.verbose)
