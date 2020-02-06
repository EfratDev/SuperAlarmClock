from pathlib import Path
import threading

from flask import Flask, render_template ,request

from common import settings, settings_lock
from sac import super_alarm_clock


TEMPLATE_DIR = 'web/html'
STATIC_DIR = 'web/static'
HTML = 'index.html'
ALARM_SET = False
app = Flask(__name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR)

#with open(str(HTML)) as f:
#    print(f.readlines(55))

@app.route('/')
def form():
    return render_template(HTML)

@app.route('/', methods=['POST'])
def set_alarm():
    global settings
    with settings_lock:
        for setting in settings:
            settings[setting] = request.form.get(setting)

    if not ALARM_SET:
        clock_thread = threading.Thread(super_alarm_clock())
        clock_thread.start()
    

def run_app():
    app.run()

run_app()