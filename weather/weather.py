#!/usr/bin/env python
import argparse
import json
import requests
import os
def get_weather(api_key, city, verbose=False, omitnewline=False):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        temp_celsius = data['main']['temp']
        temp_fahrenheit = (temp_celsius * 9/5) + 32
        weather_description = data['weather'][0]['main']
        if verbose:
            print(json.dumps(data))
        else:
            if omitnewline:
                print(f"{weather_description} {int(round(temp_fahrenheit))}°F", end='')
            else:
                print(f"{weather_description} {int(round(temp_fahrenheit))}°F")
    else:
        print(response.json())

def main():
    parser = argparse.ArgumentParser(description="Show weather from Open Weather")
    parser.add_argument("--apikey", help="API key")
    parser.add_argument("--city", help="City")
    parser.add_argument('--verbose', help="Show verbose", action="store_true")    
    parser.add_argument('--omitnewline', help="include newline", action="store_true")
    pargs = parser.parse_args()
    if 'OPENWEATHER_APIKEY' in os.environ:
        api_key = os.environ['OPENWEATHER_APIKEY'].strip()
    elif pargs.apikey:
        api_key = pargs.apikey
    else:
        api_key = input("Enter openweather api key: ").strip()
    if 'OPENWEATHER_CITY' in os.environ:
        city = os.environ['OPENWEATHER_CITY'].strip()
    elif pargs.city:
        city = pargs.city
    else:
        city = input("Enter city name: ").strip()
    get_weather(api_key, city, pargs.verbose, pargs.omitnewline)

if __name__ == "__main__":
    main()