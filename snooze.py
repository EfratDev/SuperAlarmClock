from pathlib import Path

from selenium import webdriver
import selenium
import tkinter


FIREFOX_PROFILE = 'browser_profiles/firefox'
SNOOZE_URL = 'http://127.0.0.1:5000/snooze'
BROWSER_WIDTH = 350


def get_screen_size():
    root = tkinter.Tk()
    return root.winfo_screenwidth(), root.winfo_screenheight()


def popup_snooze():
    fp = webdriver.FirefoxProfile(FIREFOX_PROFILE)
    driver = webdriver.Firefox(fp)
    screen_width, screen_height = get_screen_size()
    pos_x = screen_width/2 - BROWSER_WIDTH/2
    driver.set_window_rect(pos_x, 0, BROWSER_WIDTH, screen_height/10)
    driver.get(SNOOZE_URL)
    return driver
