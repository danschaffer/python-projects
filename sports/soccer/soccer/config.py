"""Configuration settings for the soccer module."""

from typing import Dict, Any

# API Configuration
API_CONFIG: Dict[str, Any] = {
    'BASE_URL': 'https://site.api.espn.com/apis/site/v2/sports/soccer',
    'TIMEOUT': 10,
    'HEADERS': {
        'User-Agent': 'Mozilla/5.0 (compatible; SoccerStats/1.0)',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9'
    }
}

# League Configuration
LEAGUE_CONFIG: Dict[str, Dict[str, Any]] = {
    'eng.1': {
        'size': 20,
        'relegation_zone': 3,
        'champions_league': 4,
        'europa_league': 1,
        'europa_conference': 1
    },
    'esp.1': {
        'size': 20,
        'relegation_zone': 3,
        'champions_league': 4,
        'europa_league': 1,
        'europa_conference': 1
    },
    'ger.1': {
        'size': 18,
        'relegation_zone': 2,
        'relegation_playoff': 1,
        'champions_league': 4,
        'europa_league': 1,
        'europa_conference': 1
    },
    'ita.1': {
        'size': 20,
        'relegation_zone': 3,
        'champions_league': 4,
        'europa_league': 1,
        'europa_conference': 1
    },
    'fra.1': {
        'size': 18,
        'relegation_zone': 2,
        'relegation_playoff': 1,
        'champions_league': 3,
        'europa_league': 1,
        'europa_conference': 1
    },
    'usa.1': {
        'size': 29,
        'relegation_zone': 0,
        'tournament': 9  # Top 9 teams qualify for MLS Cup Playoffs
    },
    'eng.2': {
        'size': 24,
        'promotion': 2,
        'promotion_playoff': 4,  # Teams 3-6 compete in playoffs for final promotion spot
        'relegation_zone': 3
    },
    'eng.3': {
        'size': 24,
        'promotion': 2,
        'promotion_playoff': 4,
        'relegation_zone': 4
    },
    'esp.2': {
        'size': 22,
        'promotion': 2,
        'promotion_playoff': 4,
        'relegation_zone': 4
    },
    'ita.2': {
        'size': 20,
        'promotion': 2,
        'promotion_playoff': 4,
        'relegation_zone': 3
    },
    'fra.2': {
        'size': 20,
        'promotion': 2,
        'promotion_playoff': 1,
        'relegation_zone': 3
    },
    'ger.2': {
        'size': 18,
        'promotion': 2,
        'promotion_playoff': 1,
        'relegation_zone': 2,
        'relegation_playoff': 1
    },
    'egy.1': {
        'size': 18,
        'relegation_zone': 3,
        'champions_league': 2,
        'confederation_cup': 1
    }
}

# Default configuration for leagues not specifically defined
DEFAULT_LEAGUE_CONFIG = {
    'size': 20,
    'relegation_zone': 3,
    'champions_league': 0,
    'europa_league': 0,
    'europa_conference': 0,
    'promotion': 0,
    'promotion_playoff': 0
}

# Scoring Configuration
POINTS: Dict[str, int] = {
    'WIN': 3,
    'DRAW': 1,
    'LOSS': 0
}

# Date Format Configuration
DATE_FORMAT: Dict[str, str] = {
    'API': '%Y%m%d',
    'DISPLAY': '%a %b %-d',
    'TIME': '%-I:%M%p'
}

# Cache Configuration
CACHE_CONFIG: Dict[str, int] = {
    'TIMEOUT': 300,  # 5 minutes
    'MAX_SIZE': 32   # Maximum number of cached items
}

# League Configuration
LEAGUE_SIZE: Dict[str, int] = {
    'arg.1': 28,
    'arg.2': 37,  # Argentine Primera Nacional
    'aus.1': 12,
    'aut.1': 12,
    'bel.1': 18,
    'bel.2': 12,  # Belgian Challenger Pro League
    'bra.1': 20,
    'bra.2': 20,  # Campeonato Brasileiro Série B
    'chn.1': 16,
    'den.1': 12,
    'egy.1': 18,
    'eng.1': 20,
    'eng.2': 24,  # Championship
    'eng.3': 24,
    'eng.fa': 20,
    'eng.league_cup': 20,
    'esp.1': 20,
    'esp.2': 22,  # La Liga 2
    'esp.copa_del_ray': 20,
    'fra.1': 20,
    'fra.2': 20,  # Ligue 2
    'ger.1': 18,
    'ger.2': 18,  # 2. Bundesliga
    'gre.1': 14,
    'ita.1': 20,
    'ita.2': 20,  # Serie B
    'jpn.1': 18,
    'jpn.2': 22,  # J2 League
    'kor.1': 12,
    'mar.1': 16,
    'mex.1': 18,
    'mex.2': 18,  # Liga de Expansión MX
    'ned.1': 18,
    'ned.2': 20,  # Eerste Divisie
    'nor.1': 16,
    'pol.1': 18,
    'por.1': 18,
    'por.2': 18,  # Liga Portugal 2
    'rsa.1': 16,
    'rus.1': 16,
    'sco.1': 12,
    'sco.2': 10,  # Scottish Championship
    'sui.1': 12,
    'swe.1': 16,
    'tur.1': 20,
    'tur.2': 19,  # TFF First League
    'ukr.1': 16,
    'uefa.champions': 32,
    'uefa.europa': 32,
    'usa.1': 29,
    'usa.2': 24   # USL Championship
}

# League names for display
LEAGUE_NAMES: Dict[str, str] = {
    'arg.1': 'Argentine Primera División',
    'arg.2': 'Argentine Primera Nacional',
    'aus.1': 'Australian A-League',
    'aut.1': 'Austrian Bundesliga',
    'bel.1': 'Belgian Pro League',
    'bel.2': 'Belgian Challenger Pro League',
    'bra.1': 'Brazilian Série A',
    'bra.2': 'Brazilian Série B',
    'chn.1': 'Chinese Super League',
    'den.1': 'Danish Superliga',
    'egy.1': 'Egyptian Premier League',
    'eng.1': 'English Premier League',
    'eng.2': 'English Championship',
    'eng.3': 'English League One',
    'eng.fa': 'English FA Cup',
    'eng.league_cup': 'English League Cup',
    'esp.1': 'Spanish La Liga',
    'esp.2': 'Spanish La Liga 2',
    'esp.copa_del_ray': 'Spanish Copa del Rey',
    'fra.1': 'French Ligue 1',
    'fra.2': 'French Ligue 2',
    'ger.1': 'German Bundesliga',
    'ger.2': 'German 2. Bundesliga',
    'gre.1': 'Greek Super League',
    'ita.1': 'Italian Serie A',
    'ita.2': 'Italian Serie B',
    'jpn.1': 'Japanese J1 League',
    'jpn.2': 'Japanese J2 League',
    'kor.1': 'South Korean K League 1',
    'mar.1': 'Moroccan Botola Pro',
    'mex.1': 'Mexican Liga MX',
    'mex.2': 'Mexican Liga de Expansión MX',
    'ned.1': 'Dutch Eredivisie',
    'ned.2': 'Dutch Eerste Divisie',
    'nor.1': 'Norwegian Eliteserien',
    'pol.1': 'Polish Ekstraklasa',
    'por.1': 'Portuguese Primeira Liga',
    'por.2': 'Portuguese Liga Portugal 2',
    'rsa.1': 'South African Premier Division',
    'rus.1': 'Russian Premier League',
    'sco.1': 'Scottish Premiership',
    'sco.2': 'Scottish Championship',
    'sui.1': 'Swiss Super League',
    'swe.1': 'Swedish Allsvenskan',
    'tur.1': 'Turkish Süper Lig',
    'tur.2': 'Turkish TFF First League',
    'ukr.1': 'Ukrainian Premier League',
    'uefa.champions': 'UEFA Champions League',
    'uefa.europa': 'UEFA Europa League',
    'usa.1': 'Major League Soccer',
    'usa.2': 'USL Championship'
}

# Team name mapping for corrections
TEAM_NAME_MAPPING: Dict[str, Dict[str, str]] = {
    'eng.1': {
        'Sheffield Wednesday': 'Sheffield United',
        'Sheff Wed': 'Sheffield United',
        'Sheff Utd': 'Sheffield United'
    }
} 