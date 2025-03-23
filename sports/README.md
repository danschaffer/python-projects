# Soccer Stats Viewer

A command-line tool for viewing soccer fixtures and standings from various leagues using the ESPN API.

## Features

- View fixtures and standings for multiple soccer leagues
- Filter results by team name
- Multiple output formats (text, JSON, CSV)
- Cached API responses for better performance
- Detailed match information
- Support for multiple time zones
- Error handling and logging

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sports
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
# View EPL fixtures and standings (default)
python -m soccer

# View specific league
python -m soccer --league esp.1

# View specific team
python -m soccer --team "Arsenal"

# View fixtures only
python -m soccer --fixtures

# View standings only
python -m soccer --standings

# List available leagues
python -m soccer --list-leagues
```

Advanced options:
```bash
# Custom date range (days relative to today)
python -m soccer --start -7 --end 14

# Output in JSON format
python -m soccer --format json

# Output in CSV format
python -m soccer --format csv

# Show detailed match information
python -m soccer --verbose

# Enable debug logging
python -m soccer --debug
```

## Supported Leagues

- Major European Leagues (EPL, La Liga, Bundesliga, Serie A, Ligue 1)
- Other European Leagues (Eredivisie, Primeira Liga, Belgian Pro League)
- English Leagues (Championship, League One, FA Cup, League Cup)
- European Competitions (Champions League, Europa League)
- Americas (MLS, Liga MX, Brasileirão, Primera División)
- Others (J-League, Copa del Rey)

## Development

Run tests:
```bash
pytest tests/
```

## License

MIT License

* sports
## summary
Some cli sports scores showing standings and current results using the espn hidden apis.

## soccer

* league and tournament examples are: 
eng.1,ger.1,esp.1,fra.1,usa.1,mex.1,por.1,ned.1,ita.1,uefa.champions,uefa.europa,eng.fa,eng.league_cup,esp.copa_del_ray,us.open,fifa.world
* .2 would be 2nd tier leagues etc
* day format is YYYYMMDD e.g. 20220308

* standings data is from https://site.api.espn.com/apis/site/v2/sports/soccer/:league/teams?league={league}

## basketball

* scoreboard data is from http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates=20220308
* standings data is from http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams

dates=20211003
Nets(1-0) 123 at Lakers(1-0) 97, FINAL/OT
  Cam Thomas NETS 21 points
  Paul Mislap NET 10 rebounds
  Paul Mislap NETS 3 assists

## football

* scoreboard http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?week=2

## ESPN undocumented apis
https://gist.github.com/akeaswaran/b48b02f1c94f873c6655e7129910fc3b
