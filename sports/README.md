* sports
## summary
Some cli sports scores showing standings and current results using the espn hidden apis.

## soccer

* scoreboard data is from http://site.api.espn.com/apis/site/v2/sports/soccer/:league/scoreboard?league={league}&dates={day}
* league and tournament examples are: 
eng.1,ger.1,esp.1,fra.1,usa.1,mex.1,por.1,ned.1,ita.1,uefa.champions,uefa.europa,eng.fa,eng.league_cup,esp.copa_del_ray,us.open
* .2 would be 2nd tier leagues etc
* day format is YYYYMMDD e.g. 20220308

* standings data is from https://site.api.espn.com/apis/site/v2/sports/soccer/:league/teams?league={league}

## basketball

* scoreboard data is from http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard
* standings data is from http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams