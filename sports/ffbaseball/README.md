# ESPN Fantasy Baseball Stats Tracker

A command-line tool to track and display ESPN Fantasy Baseball league statistics, including current matchup data and season-long player statistics.

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

You can configure the application using either command-line arguments or environment variables:

- League ID: Can be specified via `--league-id` or `ESPN_LEAGUE_ID` environment variable
- ESPN S2 (Cookie): Can be specified via `--espn-s2` or `ESPN_S2` environment variable
- SWID: Can be specified via `--swid` or `ESPN_SWID` environment variable

Default league ID is set to 87636.

### Finding ESPN_S2 and SWID Values in Chrome

To find your ESPN_S2 and SWID values, follow these steps in Chrome:

1. Go to your ESPN Fantasy Baseball league page (make sure you're logged in)
2. Right-click anywhere on the page and select "Inspect" (or press F12)
3. In the Developer Tools window that opens:
   - Click on the "Application" tab
   - In the left sidebar, expand "Cookies"
   - Click on "https://www.espn.com"
4. In the cookies list, find:
   - `ESPN_S2`: A long string that serves as your authentication token
   - `SWID`: A shorter string in curly braces, like `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}`
5. Copy these values and use them in one of these ways:

Create a `.env` file:
```
ESPN_S2=your_s2_value_here
SWID=your_swid_value_here
```

Or set environment variables:
```bash
export ESPN_S2="your_s2_value_here"
export SWID="your_swid_value_here"
```

Or pass them directly in commands:
```bash
python ffbaseball.py --espn-s2 "your_s2_value_here" --swid "your_swid_value_here" matchup
```

**Note**: These cookies expire periodically, so you may need to get new values if you start getting authentication errors. Keep these values private as they provide access to your ESPN account.

## Usage

### View Current Matchup
```bash
python ffbaseball.py matchup
```

### View Team Summary
```bash
python ffbaseball.py team --team-id <team_id>
```

### View Season Stats
```bash
python ffbaseball.py season
```

## Features

- Current matchup statistics
- Team roster with season and current matchup statistics
- Season-long player statistics
- Command-line interface with various options
- Support for private and public leagues 