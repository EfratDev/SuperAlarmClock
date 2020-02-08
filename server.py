from pathlib import Path
import threading

from flask import Flask, render_template ,request

from common import settings, settings_lock
from sac import super_alarm_clock
import common
import snooze


OK = 'OK'
TEMPLATE_DIR = 'web/templates/'
STATIC_DIR = 'web/static/'
HTML = 'index.html'
SNOOZE_HTML = 'snooze.html'
ALARM_SET = False
app = Flask(__name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR)


@app.route('/')
def form():
    return render_template(HTML)


@app.route('/', methods=['POST'])
def set_alarm():
    global ALARM_SET, settings
    with settings_lock:
        for setting in settings:
            settings[setting] = request.form.get(setting, False)

    if not ALARM_SET:
        clock_thread = threading.Thread(target=super_alarm_clock)
        clock_thread.start()
        ALARM_SET = True
    return render_template(HTML)


@app.route('/snooze', methods=['GET', 'POST'])
def snooze_button():
    if request.method == 'GET':
        return render_template(SNOOZE_HTML)
    elif request.method == 'POST':
        common.KEEP_PLAYING, common.SNOOZE = 0, 1
        return OK


@app.route('/dismiss', methods=['POST'])
def dismiss():
    common.KEEP_PLAYING, common.SNOOZE = 0, 0
    return OK


if __name__ == "__main__":
    app.run()
