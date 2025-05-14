from flask import Flask, render_template, request, redirect, url_for
from water import Waterer
import datetime
import os

app = Flask(__name__)
waterer = Waterer()

def get_watering_history():
    if not os.path.exists(waterer.logfile):
        return []
    
    with open(waterer.logfile, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines[-50:]]  # Get last 50 entries

@app.route('/')
def index():
    history = get_watering_history()
    return render_template('index.html', history=history)

@app.route('/water', methods=['POST'])
def water():
    valve = int(request.form.get('valve', 0))
    seconds = int(request.form.get('seconds', 30))
    
    if valve in [0, 1, 2]:
        waterer.water(valve, seconds, True)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 