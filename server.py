import threading

from flask import Flask, render_template ,request

from common import settings, settings_lock
from sac import super_alarm_clock


app = Flask(__name__)
HTML = 'web/bootstrap_index.html'
ALARM_SET = False


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
