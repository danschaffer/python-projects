#!/usr/bin/env python3
"""Test script for soccer module."""

import logging
from soccer.client import SoccerClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Test the soccer client."""
    try:
        logger.info("Creating soccer client for Egyptian Premier League")
        client = SoccerClient('egy.1')
        
        logger.info("Fetching standings")
        standings = client.get_standings()
        
        if not standings:
            logger.info("No standings available")
        else:
            logger.info(f"Found {len(standings)} teams in standings")
            
        logger.info("Displaying standings")
        client.display_standings(format='text', show_city=True)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main() 