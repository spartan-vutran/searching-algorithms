
import tkinter
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog, scrolledtext

import psutil

# Global variables
#
# Stores app logs
LOGS = []
# Loaded algorithms modules from ./algorithm/ folder
algorithms_modules = []
# Process that runs the algorithm
# If it's None it means app is not calculating
# If it's not None it contains multiprocessing.Process object and app is calculating
search_process = None
# An event object that tells the timer thread to stop
# timer_event = multiprocessing.Event()
# The thread that updates execution time, max ram usage and ram usage information
timer_thread = None
# The thread that is waiting for the algorithm to send it's result
pipe_thread = None
# A pipe which algorithm can send it's result to app through it
output_pipe = None
# A list containing current output steps's statuses
OUTPUT_LST = []
# Number of current output's step
OUTPUT_STEP = 0
# An event object that tells the play thread to stop
play_event = None
# The thread that plays output steps one by one
play_timer = None
# A ScrolledText widget that contains application logs and is inside show logs window
logs_text = None
# Goal state
GOAL_STATE = [i for i in range(9)]
# Show logs window
logs_window = None
# About window
about_window = None
# Controls whether the output text validation is enable or not
# For the sake of user experience, output entries are not disabled and instead are bound to a validation method
#   That always returns false, but sometimes the app itself wants to change the entries values, so temporarily
#   changes this variable's value to true
OUTPUT_EDITABLE = False
# Indicates whether timer thread should clear status bar or not (It's useful when some problems happened)
timer_clear_status_bar = False

# Main window
main_window = tkinter.Tk()
main_window.title("pynpuzzle - Solve n-puzzle with Python")
main_window.grid_rowconfigure(2, weight=1)
main_window.grid_columnconfigure(0, weight=1, uniform=1)
main_window.grid_columnconfigure(1, weight=1, uniform=1)
# Main window size configurations
main_window.minsize(width=840, height=360)
main_window.geometry("840x360")

# Status bar variables that are bound to status bar labes
max_ram_var = tkinter.StringVar()
cpu_var = tkinter.StringVar()
ram_var = tkinter.StringVar()
available_ram_var = tkinter.StringVar()

menu_bar = tkinter.Menu(main_window)
menu_bar.add_command(label="Change goal state", command=menu_change_goal_state_command)
menu_bar.add_command(label="Reload algorithms", command=menu_reload_algorithms_command)
menu_bar.add_command(label="Show logs", command=menu_bar_show_logs_command)
menu_bar.add_command(label="About", command=menu_bar_about_command)
# Add menu bar to main window
main_window['menu'] = menu_bar
