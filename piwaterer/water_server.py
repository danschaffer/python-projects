from flask import Flask, render_template, request, redirect, url_for, jsonify
from water import Waterer
import datetime
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEDULE_FILE = os.path.join(BASE_DIR, 'watering_schedule.json')
LOG_FILE = os.path.join(BASE_DIR, 'watering.log')

app = Flask(__name__)
waterer = Waterer()
waterer.logfile = LOG_FILE  # Override the logfile path
scheduler = BackgroundScheduler()
scheduler.start()

def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    default_schedule = {
        'morning': {'time': '09:00', 'durations': [60, 60, 60]},
        'evening': {'time': '18:00', 'durations': [60, 60, 60]}
    }
    save_schedule(default_schedule)  # Create initial schedule file
    return default_schedule

def save_schedule(schedule):
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(schedule, f, indent=4)

def log_watering_event(message):
    """Log watering events with timestamp"""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"{ts}: {message}\n")

def run_scheduled_watering(period):
    schedule = load_schedule()
    durations = schedule[period]['durations']
    log_watering_event(f"Starting scheduled {period} watering")
    
    for valve, duration in enumerate(durations):
        if duration > 0:  # Only water if duration is set
            log_watering_event(f"Scheduled watering: Valve {valve} for {duration} seconds")
            waterer.water(valve, duration, True)
    
    log_watering_event(f"Completed scheduled {period} watering")

def setup_schedules():
    schedule = load_schedule()
    
    # Clear existing jobs
    scheduler.remove_all_jobs()
    
    # Add morning schedule
    scheduler.add_job(
        run_scheduled_watering,
        CronTrigger(hour=9, minute=0),
        args=['morning'],
        id='morning_schedule'
    )
    
    # Add evening schedule
    scheduler.add_job(
        run_scheduled_watering,
        CronTrigger(hour=18, minute=0),
        args=['evening'],
        id='evening_schedule'
    )
    
    log_watering_event("Schedules initialized")

def get_watering_history():
    if not os.path.exists(LOG_FILE):
        return []
    
    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines[-50:]]  # Get last 50 entries

@app.route('/')
def index():
    history = get_watering_history()
    schedule = load_schedule()
    return render_template('index.html', history=history, schedule=schedule)

@app.route('/water', methods=['POST'])
def water():
    valve = int(request.form.get('valve', 0))
    seconds = int(request.form.get('seconds', 30))
    
    if valve in [0, 1, 2]:
        log_watering_event(f"Manual watering: Valve {valve} for {seconds} seconds")
        waterer.water(valve, seconds, True)
    
    return redirect(url_for('index'))

@app.route('/update_schedule', methods=['POST'])
def update_schedule():
    schedule = load_schedule()
    
    # Update both morning and evening schedules
    for period in ['morning', 'evening']:
        durations = [
            int(request.form.get(f'{period}_duration_{i}', 60))
            for i in range(3)
        ]
        schedule[period] = {
            'time': '09:00' if period == 'morning' else '18:00',
            'durations': durations
        }
    
    save_schedule(schedule)
    setup_schedules()
    log_watering_event("Schedule updated for both morning and evening periods")
    
    return redirect(url_for('index'))

@app.route('/test_valve/<int:valve>', methods=['GET'])
def test_valve(valve):
    if valve in [0, 1, 2]:
        log_watering_event(f"Testing valve {valve}")
        waterer.water(valve, 5, True)  # Run for 5 seconds
        return jsonify({'status': 'success', 'message': f'Tested valve {valve}'})
    return jsonify({'status': 'error', 'message': 'Invalid valve number'})

# Initialize schedules on startup
setup_schedules()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 