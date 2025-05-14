#!/usr/bin/env python3
from gpiozero import LED
import datetime
import time
import argparse

class Waterer:

    def __init__(self):
        self.logfile = '/var/log/water.log'
        self.pump_gpio = 17
        self.pump = LED(self.pump_gpio)
        self.pump.off()
        self.valves_gpio = [22, 4, 27]
        self.valves = [LED(n) for n in self.valves_gpio]
        self.turn_all_valves_off()
        self.log('System initialized')

    def turn_all_valves_off(self):
        """Turn off all valves"""
        for valve in self.valves:
            valve.off()
        self.log('All valves turned off')

    def water(self, nvalve, secs, log):
        if log:
            self.log(f'Starting water valve {nvalve} for {secs}s')
        assert nvalve in [0, 1, 2], 'valve must be 0,1,2'
        
        # Ensure all valves are off before starting
        self.turn_all_valves_off()
        
        # Turn on the selected valve
        valve = self.valves[nvalve]
        if log:
            self.log(f'Turning on valve {nvalve} (GPIO {self.valves_gpio[nvalve]})')
        valve.on()
        time.sleep(0.5)
        
        # Turn on pump
        if log:
            self.log('Turning on pump')
        self.pump.on()
        time.sleep(secs)
        
        # Turn off pump and valve
        if log:
            self.log('Turning off pump')
        self.pump.off()
        if log:
            self.log(f'Turning off valve {nvalve}')
        valve.off()
        
        # Double check all valves are off
        self.turn_all_valves_off()
        
        if log:
           self.log(f'Completed water valve {nvalve} for {secs}s')

    def log(self, message):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.logfile, 'a') as myfile:
            myfile.write(ts + ': ' + message + '\n')    

    def run(self, pargs):
        for valve in pargs.valve.split(','):
            self.water(int(valve), pargs.time, pargs.log)
            time.sleep(10)
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--time', type=int, default=120, help='time to open valve')
    parser.add_argument('--valve', default='0', help='valve to open 0,1,2')
    parser.add_argument('--log', action='store_true', help='logs to /var/log/water.log')
    pargs = parser.parse_args()
    waterer = Waterer()
    waterer.run(pargs)

