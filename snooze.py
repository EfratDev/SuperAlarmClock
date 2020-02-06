from selenium.webdriver import Firefox
from selenium import webdriver
from pathlib import Path
import selenium
import tkinter

snooze_path = Path(Path().absolute(), 'snooze.html')
SNOOZE_URL = f'file://{snooze_path}'

root = tkinter.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
driver = Firefox()
driver.set_window_rect(0, 0, width, height/10)
driver.get(SNOOZE_URL)
