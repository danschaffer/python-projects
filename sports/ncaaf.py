#!/usr/bin/env python

import argparse
import datetime
import pytz
import requests
import tzlocal
class Ncaab:
    def __init__(self):
        pass

    def get_schedule(self, days, verbose):
        _date = datetime.datetime.now() + datetime.timedelta(days=days)
        day = _date.strftime('%Y%m%d')
        datePrinted = False
        data = requests.get(f"http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates={day}").json()
        for event in data['events']:
            if not datePrinted:
                print(_date.strftime("%a %b %-d"))
                datePrinted =True
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
            if clock != '0.0':
                competition = event['competitions'][0]
                name0 = competition['competitors'][0]['team']['location']
                rank0 = competition['competitors'][0]['curatedRank']['current']
                name1 = competition['competitors'][1]['team']['location']
                rank1 = competition['competitors'][1]['curatedRank']['current']
                if rank0 < 26:
                    name0 += f"({rank0})"
                if rank1 < 26:
                    name1 += f"({rank1})"
                if competition['competitors'][0]['homeAway'] == 'home':
                    home = f"{name0}({competition['competitors'][0]['records'][0]['summary']}) {competition['competitors'][0]['score']}"
                    away = f"{name1}({competition['competitors'][1]['records'][0]['summary']}) {competition['competitors'][1]['score']}"
                else:
                    away = f"{name0}({competition['competitors'][0]['records'][0]['summary']}) {competition['competitors'][1]['score']}"
                    home = f"{name1}({competition['competitors'][1]['records'][0]['summary']}) {competition['competitors'][0]['score']}"
                teams[competition['competitors'][0]['id']] = competition['competitors'][0]['team']['displayName']
                teams[competition['competitors'][1]['id']] = competition['competitors'][1]['team']['displayName']
                print(f"{away} at {home} {clock}")
                if verbose:
                    for team in competition['competitors']:
                        if 'leaders' in team:
                            for leader in team['leaders']:
                                print(f"  {teams[leader['leaders'][0]['athlete']['team']['id']]} {leader['displayName']} {leader['leaders'][0]['athlete']['displayName']} {leader['leaders'][0]['displayValue']}")
            else:
                competition = event['competitions'][0]
                name0 = competition['competitors'][0]['team']['location']
                name1 = competition['competitors'][1]['team']['location']
                if rank0 < 26:
                    name0 += f"({rank0})"
                if rank1 < 26:
                    name1 += f"({rank1})"
                if competition['competitors'][0]['homeAway'] == 'home':
                    home = f"{name0}({competition['competitors'][0]['records'][0]['summary']})"
                    away = f"{name1}({competition['competitors'][1]['records'][0]['summary']})"
                else:
                    away = f"{name0}({competition['competitors'][0]['records'][0]['summary']})"
                    home = f"{name1}({competition['competitors'][1]['records'][0]['summary']})"
                print(f"{away} at {home} {_tm}")

    def schedules(self, start, end, verbose):
        for count in range(start, end):
            self.get_schedule(count, verbose)

    def standings(self):
        print("Rankings")
        data = requests.get(f"http://site.api.espn.com/apis/site/v2/sports/football/college-football/rankings").json()
        for team in data['rankings'][0]['ranks']:
            print(f"{team['current']:2} {team['trend']:4} {team['team']['abbreviation']:4} {team['team']['nickname']:15} {team['recordSummary']:10}")

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
    ncaa = Ncaab()
    if pargs.standings:
        ncaa.standings()
    if pargs.schedule:
        ncaa.schedules(pargs.start, pargs.end, pargs.verbose)
