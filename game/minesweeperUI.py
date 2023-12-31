#!/usr/bin/env python3
"""
pynpuzzle - Solve n-puzzle with Python

Version : 1.0.0
Author : Hamidreza Mahdavipanah
Repository: http://github.com/mahdavipanah/pynpuzzle
License : MIT License
"""
import math
import random
import re
import webbrowser
import sys
import traceback
from os import listdir
from os.path import isfile, join
import datetime
from importlib import import_module
import multiprocessing
import threading
import time
from copy import deepcopy

import tkinter
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog, scrolledtext
from game import MineSweeperGame
from searchAgent import SearchAgent
from queue import Queue

import psutil

# Global variables
#
# Stores app logs
LOGS = []
search_process = None
# An event object that tells the timer thread to stop
timer_event = multiprocessing.Event()
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

#Dict store cell search
CELL_SEARCHED = {} 
#set default maxtrix
ROWS_MATRIX_DEFAULT = 10
COLUMN_MATRIX_DEFAULT = 10
NUM_OF_MINES = 12
BOARD = [
        [0,0,0,0,0,1,1,1,0,0,],
        [0,0,0,0,0,1,-1,1,0,0,],
        [0,0,1,2,2,2,1,1,0,0,],
        [0,1,2,-1,-1,1,0,0,0,0,],
        [0,1,-1,4,3,2,0,0,1,1,],
        [1,2,2,2,-1,1,0,0,1,-1,],
        [1,-1,1,2,2,2,0,0,1,1,],
        [1,1,2,2,-1,1,1,1,1,0,],
        [1,1,1,-1,2,1,2,-1,2,0,],
        [-1,1,1,1,1,0,2,-1,2,0,],
  ]
minesweepergame = MineSweeperGame(ROWS_MATRIX_DEFAULT, ROWS_MATRIX_DEFAULT, NUM_OF_MINES, BOARD)

# Main window
main_window = tkinter.Tk()
main_window.title("MineSweeper with Python")
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


def return_false_validate():
    """
    Validation function for output entry widgets.

    Returns OUTPUT_EDITABLE global variable.
    """
    return OUTPUT_EDITABLE


def draw_puzzle(puzzle_frame, numOfRows, numOfColumns, read_only=False):
    """
    Fills a frame widget with n + 1 entry widget.

    puzzle_frame : The puzzle frame to get filled by entry widgets.
    n : Puzzle type (n-puzzle).
    read_only : Should widgets be read-only or not
    """
    # n = int(math.sqrt(n + 1))

    for i in range(numOfRows):
        for j in range(numOfColumns):
            entry = tkinter.Entry(puzzle_frame, width=4, justify='center')
            entry.grid(row=i, column=j, sticky='WENS')

            if read_only:
                # Bind the widget validation command to return_false_validate command and therefore
                #   OUTPUT_EDITABLE global variable.
                entry.config(validatecommand=return_false_validate, validate=tkinter.ALL)

        # puzzle_frame.grid_columnconfigure(i, weight=1)
        # puzzle_frame.grid_rowconfigure(i, weight=1)


def config_frame_state(frame, state):
    """
    Changes the status property of a frame children.
    """
    for child in frame.winfo_children():
        # Only output_play_button can change output_stop_button's state
        if child is output_stop_button:
            # If output is playing right now
            if play_event:
                # Someone wants to disable the output frame, so output play must stop
                play_event.set()
            continue

        child['state'] = state

    # output_0_label's and output_to_label's cursor property are depending on their frame status
    if frame is output_action_frame:
        cursor = 'arrow'
        if state == tkinter.NORMAL:
            cursor = 'fleur'
        output_0_label['cursor'] = cursor
        output_to_label['cursor'] = cursor


def config_io_frame_state(frame, state):
    """
    A special function only for changing the state of output or input label
    """
    if frame is output_labelframe:
        # For the sake of user experience output entry widgets are not getting disabled and instead their values
        #   Are not editable
        config_frame_state(output_action_frame, state)
    else:
        config_frame_state(input_puzzle_frame, state)
        config_frame_state(input_action_frame, state)


def create_puzzle_frame(parent_frame, numOfRows, numOfColumns, current_puzzle_frame=None, read_only=False):
    """
    Creates a new puzzle frame inside a parent frame and if the puzzle frame already exists, first destroys it.
    This is done because when the n changes we have to change the puzzle frame's grid row and column configurations
    and it turned out in tkinter it can be done by recreating the frame widget!

    Returns the newly created puzzle frame.
    """
    if current_puzzle_frame:
        current_puzzle_frame.destroy()

    puzzle_frame = tkinter.Frame(parent_frame)
    puzzle_frame.grid(row=0, column=0, sticky='WENS')

    draw_puzzle(puzzle_frame, numOfRows, numOfColumns, read_only)

    return puzzle_frame

# def open_zero_cell_around(puzzle_frame, row, col):
#     entry_widget = puzzle_frame.grid_slaves(row=row, column=col)[0]
#     if minesweepergame.board[row][col] == 0:
#         entry_widget.config(bg="red")
#         for i in range(-1, 2):
#             for j in range(-1, 2):
#                 search_row, search_col = row + i, col + j
#                 if 0 <= row + i < minesweepergame.rows and 0 <= col + j < minesweepergame.cols and CELL_SEARCHED.get(f"{search_row}-{search_col}", False) == False:
#                     # entry_widget.config(bg="red")
#                     open_zero_cell_around(puzzle_frame, row + i, col + j)
        
#     return
def open_zero_cell_around(puzzle_frame, start_row, start_col):
    rows, cols = len(minesweepergame.board), len(minesweepergame.board[0])
    visited = set()
    queue = Queue()
    queue.put((start_row, start_col))

    while not queue.empty():
        row, col = queue.get()
        entry_widget = puzzle_frame.grid_slaves(row=row, column=col)[0]
        
        if (row, col) in visited:
            continue

        visited.add((row, col))

        if entry_widget.cget('bg') != "#CDCDC8" and entry_widget.cget('bg') != "green":
            entry_widget.config(bg="#CDCDC8")
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_row, new_col = row + i, col + j
                if 0 <= new_row < rows and 0 <= new_col < cols and (new_row, new_col) not in visited and minesweepergame.board[row][col] == 0:
                    queue.put((new_row, new_col))

    return


def fill_puzzle_frame(puzzle_frame, board, action = None):
    """
    Fills a puzzle frame with a puzzle list.
    """
    global OUTPUT_EDITABLE
    lst = []
    # lst = ['' if x == 0 else x for x in lst]
    for row in range(minesweepergame.rows):
        for col in range(minesweepergame.cols):
            lst.append(minesweepergame.board[row][col])
    # Enable editing the output puzzle temporarily
    OUTPUT_EDITABLE = True
    i = 0
    # for child in puzzle_frame.winfo_children():
    for i, child in enumerate(puzzle_frame.winfo_children()):
        child.delete(0, tkinter.END)
        child.insert(0, lst[i])
        if puzzle_frame is input_puzzle_frame:
            if hasattr(child, '_highlight_frame') and child._highlight_frame.winfo_exists():
                child._highlight_frame.destroy()
            # child.config(state=tkinter.DISABLED, bg="#CDCDC8")
            child.config(state=tkinter.DISABLED, bg="#CDCDC8")

        
        # child['highlightbackground'] = 'red'
        # puzzle_frame.after(1, set_highlight_background, child)

        # if puzzle_frame is output_puzzle_frame and lst[i] == 0:
        #     child['highlightbackground'] = 'Orange'
        # elif puzzle_frame is output_puzzle_frame:
        #     # Change the child's highlightbackground color to entry widget's default property using another
        #     #   entry widget which we are sure has default property's value
        #     child['highlightbackground'] = output_step_text['highlightbackground']

        i += 1
    
    if action != None:
        print(action)
        for row in range(len(minesweepergame.board)):
            for col in range(len(minesweepergame.board[0])):
                entry_widget = puzzle_frame.grid_slaves(row=row, column=col)[0]
                # entry_widget.delete(0, tkinter.END)
                # entry_widget.insert(0, minesweepergame.board[row][col])
                if row == action.getX() and col == action.getY():
                    # if minesweepergame.board[row][col] == 0:
                    #     for i in range(-1, 2):
                    #         for j in range(-1, 2):
                    #             if 0 <= row + i < minesweepergame.rows and 0 <= col + j < minesweepergame.cols:
                    #                 around_entry_widget = puzzle_frame.grid_slaves(row=row+i, column=col+j)[0]
                    #                 around_entry_widget.config(bg="red")

                    # CELL_SEARCHED[f"{row}-{col}"] = True
                    open_zero_cell_around(puzzle_frame, row, col)
                    entry_widget.config(bg="green")

                # if row == action.getX() and col == action.getY():
                #     entry_widget['highlightbackground'] = 'Orange'
                # else:
                #     entry_widget['highlightbackground'] = puzzle_frame.cget('background')
    # if action != None:
    #     print(action)
    #     for i, child in enumerate(puzzle_frame.winfo_children()):
    #         child.delete(0, tkinter.END)
    #         child.insert(0, lst[i])
    #         if puzzle_frame is output_puzzle_frame:
    #             if hasattr(child, '_highlight_frame') and child._highlight_frame.winfo_exists():
    #                 child._highlight_frame.destroy()
    #             child.config(state=tkinter.DISABLED, bg="#CDCDC8")
    # Disable editing the output puzzle
    OUTPUT_EDITABLE = False

def fill_puzzle_frame_step_n(puzzle_frame, action):
    """
    Fills a puzzle frame with a puzzle list.
    """
    global OUTPUT_EDITABLE
    lst = []
    # lst = ['' if x == 0 else x for x in lst]
    for row in range(minesweepergame.rows):
        for col in range(minesweepergame.cols):
            lst.append(minesweepergame.board[row][col])
    # Enable editing the output puzzle temporarily
    OUTPUT_EDITABLE = True
    # i = 0
    # for child in puzzle_frame.winfo_children():
    #     child.delete(0, tkinter.END)
    #     child.insert(0, lst[i])

    #     if puzzle_frame is output_puzzle_frame and lst[i] == 0:
    #         child['highlightbackground'] = 'Orange'
    #     elif puzzle_frame is output_puzzle_frame:
    #         # Change the child's highlightbackground color to entry widget's default property using another
    #         #   entry widget which we are sure has default property's value
    #         child['highlightbackground'] = output_step_text['highlightbackground']

    #     i += 1
    print(action)
    for row in range(len(minesweepergame.board)):
        for col in range(len(minesweepergame.board[0])):
            entry_widget = puzzle_frame.grid_slaves(row=row, column=col)[0]
            entry_widget.delete(0, tkinter.END)
            entry_widget.insert(0, minesweepergame.board[row][col])

            if row == action.x and col == action.y:
                entry_widget['highlightbackground'] = 'Orange'
            else:
                entry_widget['highlightbackground'] = puzzle_frame.cget('background')
    # Disable editing the output puzzle
    OUTPUT_EDITABLE = False


def list_to_puzzle(lst):
    """
    Converts a one dimensional puzzle list and returns it's two dimensional representation.

    [1, 2, 3, 4, 5, 6, 7, 8, 0] --> [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    """
    n_sqrt = int(math.sqrt(len(lst)))

    puzzle = []
    for i in range(0, len(lst), n_sqrt):
        line = []
        for j in range(0, n_sqrt):
            line.append(lst[i + j])
        puzzle.append(line)

    return puzzle


def puzzle_to_list(puzzle):
    """
    Converts a two dimensional puzzle to a one dimensional puzzle.

    [[1, 2, 3], [4, 5, 6], [7, 8, 9]] --> [1, 2, 3, 4, 5, 6, 7, 8, 0]
    """
    lst = []
    # for row in puzzle:
    #     lst.extend(row)
    lst.append(puzzle)

    return lst

def actions_to_list(puzzle):
    """
    Converts a two dimensional puzzle to a one dimensional puzzle.

    [[1, 2, 3], [4, 5, 6], [7, 8, 9]] --> [1, 2, 3, 4, 5, 6, 7, 8, 0]
    """
    lst = []
    for row in puzzle:
        lst.extend(row)

    return lst


def check_puzzle_list(lst, n):
    """
    Checks a puzzle one dimensional list and validates it.

    lst : The list to be validated.
    n : Puzzle type (n-puzzle).

     Returns True of it's fine and False if it's not valid.
    """
    # Check list's length
    if len(lst) != n + 1:
        return False

    lst = lst[:]

    lst = [0 if x == '' else x for x in lst]

    # Generate a new list containing numbers from 0 to n
    #   and then check if the list has all of those numbers in it
    new_lst = [i for i in range(0, n + 1)]
    for lst_item in new_lst:
        try:
            lst.remove(lst_item)
        except ValueError:
            return False

    if len(lst) != 0:
        return False

    return True


def get_puzzle_frame_list(puzzle_frame):
    """
    Returns a one dimensional puzzle list that is inside a frame widget.
    """
    lst = []
    for child in puzzle_frame.winfo_children():
        txt = child.get().strip()
        if txt == '':
            txt = 0
        lst.append(int(txt))

    return lst


def start_timer():
    """
    Starts the timer for updating status bar.
    """
    global timer_thread
    global timer_event
    global timer_clear_status_bar

    max_ram_var.set('0')
    cpu_var.set('0')

    search_process_psutil = psutil.Process(search_process.pid)

    def timing():
        while not timer_event.is_set():
            prev_val = float(max_ram_var.get())
            new_val = round(search_process_psutil.memory_full_info().uss / (2 ** 20), 3)

            ram_var.set(new_val)

            if new_val > prev_val:
                max_ram_var.set(new_val)

            cpu_times = search_process_psutil.cpu_times()
            cpu_var.set(round(cpu_times.user + cpu_times.system, 3))

            timer_event.wait(0.001)

        if timer_clear_status_bar:
            cpu_var.set('')
            max_ram_var.set('')
            ram_var.set('')

    timer_event.clear()

    timer_clear_status_bar = False
    timer_thread = threading.Thread(target=timing, daemon=True)
    timer_thread.start()


def load_output_step(n):
    """
    Fills the output puzzle with nth output step.
    """
    global OUTPUT_STEP

    OUTPUT_STEP = n
    # step_n_lst = OUTPUT_LST[n]
    step_n_lst = minesweepergame.board
    fill_puzzle_frame(output_puzzle_frame, step_n_lst, OUTPUT_LST[n])

    output_step_text.delete(0, tkinter.END)
    output_step_text.insert(0, n)


def piper():
    """
    A thread target that listens for algorithm's output through a pipe
    :return:
    """
    global OUTPUT_LST
    global OUTPUT_STEP
    global timer_event
    global timer_clear_status_bar

    try:
        # Waits for algorithm to send the result
        OUTPUT_LST = output_pipe.recv()
        print(len(OUTPUT_LST))
        print(OUTPUT_LST)
        count = 1
        for action in OUTPUT_LST:
            print(f"Action{count}: {action.x}, {action.y}")

        output_error = False
        output_exception = False

        # # If the returned value is a string, Some exception has have happened
        if type(OUTPUT_LST) is str:
            output_exception = True
        else:
            # Validate algorithm's output
            if not OUTPUT_LST:
                output_error = True
            elif type(OUTPUT_LST) is not list:
                output_error = True
            else:
                n = 6
                # try:
                #     n = 6
                #     sqrt_n = math.sqrt(n + 1)
                #     for output_step in OUTPUT_LST:
                #         if type(output_step) is not list:
                #             raise BaseException()
                #         if len(output_step) != sqrt_n:
                #             raise BaseException()
                #         for step_row in output_step:
                #             if type(step_row) is not list:
                #                 raise BaseException()
                #             if len(step_row) != sqrt_n:
                #                 raise BaseException()
                #         if not check_puzzle_list([int(output_step[i][j])
                #                                   for i in range(len(output_step))
                #                                   for j in range(len(output_step))],
                #                                  n):
                #             raise BaseException()
                # except:
                #     output_error = True

            if not output_error:
                # Converts output's puzzles to one dimensional representation of them
                tmp_lst = []
                for result in OUTPUT_LST:
                    # tmp_lst.append(puzzle_to_list(result))
                    tmp_lst.append(result)
                OUTPUT_LST = tmp_lst

    except EOFError:
        # Stop button pressed
        pass
    else:
        # Calculation successfully done!
        #
        # Stop status thread
        if output_exception or output_error:
            timer_clear_status_bar = True
        timer_event.set()

        calculation_stop()

        # If some exception has have happened inside algorithm's function
        if output_exception:
            messagebox.showerror("Algorithm exception", "Some exception happened in algorithm's source code:\n\n" +
                                 OUTPUT_LST, parent=main_window)

            OUTPUT_LST = []
            OUTPUT_STEP = 0

            return

        if output_error:
            messagebox.showerror("Algorithm output error", "Algorithm's output is not valid.", parent=main_window)

            OUTPUT_LST = []
            OUTPUT_STEP = 0

            return

        # Enable output's action frame
        config_frame_state(output_action_frame, tkinter.NORMAL)
        output_to_label['text'] = len(OUTPUT_LST)-1
        output_0_label['text'] = '0'

        # Load the first step to output puzzle
        load_output_step(0)


def start_piping():
    """
    Starts the piper thread to listen to algorithm's output.
    """
    global pipe_thread
    global output_pipe

    output_pipe, process_pipe = multiprocessing.Pipe()

    pipe_thread = threading.Thread(target=piper, daemon=True)
    pipe_thread.start()

    # Return the sender pipe
    return process_pipe


def log_datetime():
    """
    Returns the datetime for logging.
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M")


def update_logs_text_if_visible():
    """
    If show logs window is open, then update the text widget's content.
    If someone updates app logs, then should invoke this function.
    """
    if logs_text:
        logs_text['state'] = tkinter.NORMAL
        logs_text.delete(0.0, tkinter.END)
        logs_text.insert(0.0, ''.join(LOGS))
        logs_text['state'] = tkinter.DISABLED
        # Scroll to end of text
        logs_text.see(tkinter.END)


def load_algorithms():
    """
    Load algorithm's modules from ./algorithm/ folder.
    It assumes all python files as algorithms and tries to load them.
    """
    
    global LOGS
    algorithms_names = ["A*", "DFS", "BrFS"]
    update_logs_text_if_visible()

    prev_algorithm_name = algorithm_name.get()
    # Update algorithms combobox with loaded algorithm's names
    algorithm_combobox['values'] = algorithms_names
    # If there is any loaded algorithms
    if len(algorithms_names):
        if algorithms_names.count(prev_algorithm_name):
            # Select the previously selected algorithm
            algorithm_combobox.set(prev_algorithm_name)
        else:
            # Select the first algorithm from combobox
            algorithm_combobox.set(algorithms_names[0])
# Menu bar
menu_bar = tkinter.Menu(main_window)
# Add menu bar to main window
main_window['menu'] = menu_bar

# n frame
n_frame = tkinter.Frame(main_window)
n_frame.grid(row=0, column=0, sticky='EWN', padx=5, pady=5)
n_frame.grid_rowconfigure(0, weight=1)
n_frame.grid_columnconfigure(1, weight=1)
# n label
tkinter.Label(n_frame, text="").grid(row=0, column=0)

# Algorithm frame
algorithm_frame = tkinter.Frame(main_window)
algorithm_frame.grid(row=0, column=1, sticky='EWN', padx=5, pady=5)
algorithm_frame.grid_rowconfigure(0, weight=1)
algorithm_frame.grid_columnconfigure(1, weight=1)
# Algorithm label
algorithm_combobox_label = tkinter.Label(algorithm_frame, text="algorithm: ")
algorithm_combobox_label.grid(row=0, column=0)
# Algorithm combobox
algorithm_name = tkinter.StringVar()
algorithm_combobox = ttk.Combobox(algorithm_frame,
                                  textvariable=algorithm_name,
                                  validate=tkinter.ALL,
                                  validatecommand=lambda: False)
algorithm_combobox.grid(row=0, column=1, sticky='EWN')


def calculation_stop():
    """
    Does some routine works that has to be done when to stop calculation.
    """
    # Show start button
    start_button.grid()
    start_button_border_frame.grid()
    # Hide progress bar
    progress_bar.grid_remove()
    progress_bar.stop()
    stop_button['state'] = tkinter.DISABLED
    # n_spinbox['state'] = tkinter.NORMAL
    # Enable input data entry
    config_io_frame_state(input_labelframe, tkinter.NORMAL)


def stop_button_cmd():
    """
    Stop button click handler
    """
    # Do some routines for stopping calculation
    calculation_stop()
    # Stop algorithm's process
    search_process.terminate()
    output_pipe.close()
    # Stop timer thread and stop refreshing status bar
    timer_event.set()
    # Clear status labels
    threading.Timer(0.1, max_ram_var.set, args=('',)).start()
    threading.Timer(0.1, cpu_var.set, args=('',)).start()
    threading.Timer(0.1, ram_var.set, args=('',)).start()


# Action buttons
#
# Output stop widget and it's border frame
stop_button_border_frame = tkinter.Frame(main_window, bg='Red')
stop_button_border_frame.grid(row=1, column=0, sticky='EWN', padx=5, pady=5)
stop_button_border_frame.grid_columnconfigure(0, weight=1)
stop_button = tkinter.Button(stop_button_border_frame, text="Stop", state=tkinter.DISABLED,
                             command=lambda: stop_button_cmd())
stop_button.grid(row=0, column=0, sticky='EWN', padx=1, pady=1)


def is_input_puzzle_valid(puzzle_frame):
    """
    Checks if given puzzle frame has a valid puzzle in it.

    If puzzle frame has a valid input return's it's one dimensional list and returns None otherwise.
    """
    try:
        lst = get_puzzle_frame_list(puzzle_frame)
        # if not check_puzzle_list(lst, int(n_spinbox.get())):
        #     raise Exception
        return lst
    except:
        return None


def search_runner(func, pipe, arg):
    """
    This function invokes the given func with lst and goal_state arguments and sends func's returned value to pipe.
    If some exception happened in func, sends print ready exception's string to show to user.
    """
    try:
        # ret_val = func(lst, goal_state)
        ret_val = func(arg)
        pipe.send(ret_val)
    except BaseException as e:
        exception_message = traceback.format_exception(type(e), e, e.__traceback__)
        del exception_message[1]
        pipe.send(''.join(exception_message))


def start_button_cmd():
    """
    Start button click handler
    """
    global output_puzzle_frame
    global search_process
    global OUTPUT_EDITABLE

    # Check if input puzzle has a valid input
    lst = is_input_puzzle_valid(input_puzzle_frame)
    if not lst:
        messagebox.showerror("Input error", "Inputs are not valid!", parent=main_window)
        return
    # Change widgets's looks
    start_button.grid_remove()
    start_button_border_frame.grid_remove()
    progress_bar.grid()
    progress_bar.start()
    stop_button['state'] = tkinter.NORMAL
    # n_spinbox['state'] = tkinter.DISABLED
    config_io_frame_state(input_labelframe, tkinter.DISABLED)
    output_to_label['text'] = ''
    output_0_label['text'] = ''
    output_step_text.delete(0, tkinter.END)
    config_io_frame_state(output_labelframe, tkinter.DISABLED)
    # Clear output puzzle
    OUTPUT_EDITABLE = True
    for child in output_puzzle_frame.winfo_children():
        # if child.get().strip() == '':
        #     child['highlightbackground'] = output_step_text['highlightbackground']
        child.config(bg="white")
        child.delete(0, tkinter.END)
    OUTPUT_EDITABLE = False
    print(algorithm_name.get())
    search_function = minesweepergame.runAgentWihtoutDisplay
    # Algorithm's search process
    search_process = multiprocessing.Process(target=search_runner,
                                             args=(search_function,
                                                   start_piping(), algorithm_name.get()))
    search_process.daemon = True
    search_process.start()
    start_timer()


# Start button widget and it's border frame
start_button_border_frame = tkinter.Frame(main_window, bg='Green')
start_button_border_frame.grid(row=1, column=1, sticky='EWN', padx=5, pady=5)
start_button_border_frame.grid_columnconfigure(0, weight=1)
start_button = tkinter.Button(start_button_border_frame, text="Start", command=start_button_cmd)
start_button.grid(row=0, column=0, sticky='WENS', padx=1, pady=1)
# Progress bar widget
progress_bar = ttk.Progressbar(main_window, mode='indeterminate', maximum=20)
progress_bar.grid(row=1, column=1, sticky='EW', padx=5, pady=5)
progress_bar.grid_remove()
# Output labelframe
output_labelframe = tkinter.LabelFrame(main_window, text="Output")
output_labelframe.grid(row=2, column=0, sticky='WENS', padx=5, pady=5)
output_labelframe.grid_rowconfigure(0, weight=1)
output_labelframe.grid_columnconfigure(0, weight=1)
# Output puzzle frame
output_puzzle_frame = create_puzzle_frame(output_labelframe, ROWS_MATRIX_DEFAULT, COLUMN_MATRIX_DEFAULT, None, True)
# Output action frame
output_action_frame = tkinter.Frame(output_labelframe, bd=1, relief=tkinter.SUNKEN)


def output_0_to_label_click(n):
    """
    output_0_label click handler

    Goes to first step of the output.
    """
    if output_0_label['cursor'] == 'fleur':
        load_output_step(n-1)


# output_0_label widget
output_0_label = tkinter.Label(output_action_frame, cursor="fleur")
output_0_label.pack(side=tkinter.LEFT)
output_0_label.bind('<Button-1>', lambda x: output_0_to_label_click(0))


def prev_step_button():
    """
    Output's previous step button click handler

    Goes to previous step of the output.
    """
    if OUTPUT_STEP == 0:
        return False

    load_output_step(OUTPUT_STEP - 1)
    return True


tkinter.Button(output_action_frame, text="<<", width=0, command=prev_step_button).pack(side=tkinter.LEFT)


def output_stop_button_cmd():
    """
    Output's stop button click handler

    Stops playing the output.
    """
    play_event.set()

    output_play_button['state'] = tkinter.NORMAL
    output_stop_button['state'] = tkinter.DISABLED


# Output's stop button widget
output_stop_button = tkinter.Button(output_action_frame, text="Stop", width=0, fg='Red', state=tkinter.DISABLED,
                                    command=output_stop_button_cmd)
output_stop_button.pack(side=tkinter.LEFT)
output_step_text = tkinter.Entry(output_action_frame, width=10, justify=tkinter.CENTER)
output_step_text.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)


def step_text_enter(*_):
    """
    Output's step text widget 'Enter' and 'Return' key handler

    Goes to entered step of the output.
    """
    # Check if the entered text is a number
    try:
        step_num = int(output_step_text.get())
    except ValueError:
        output_step_text.delete(0, tkinter.END)
        output_step_text.insert(0, OUTPUT_STEP)
        return
    # Check if the entered number is in the range of the steps
    if not (0 <= step_num <= int(output_to_label['text'])):
        output_step_text.delete(0, tkinter.END)
        output_step_text.insert(0, OUTPUT_STEP)
        return

    load_output_step(step_num)


output_step_text.bind('<KP_Enter>', step_text_enter)
output_step_text.bind('<Return>', step_text_enter)


def play_button_command():
    """
    Output's play button click handler

    Start playing the output steps one by one.
    """
    global play_event
    global play_timer

    def playing():
        """
        Target function for play_thread

        Plays output step's one by one with one second delay between them.
        """
        time.sleep(1)
        while not play_event.is_set():
            next_step_button()
            if OUTPUT_STEP == int(output_to_label['text']):
                output_stop_button_cmd()
                return
            play_event.wait(1)

    # Disable play button
    output_play_button['state'] = tkinter.DISABLED
    # Enable stop button
    output_stop_button['state'] = tkinter.NORMAL

    # If output's step is already the last one, change the step to the first step so it can be played from beginning
    if OUTPUT_STEP == int(output_to_label['text']):
        load_output_step(0)

    play_event = threading.Event()
    play_timer = threading.Thread(target=playing)
    play_timer.start()


# Output's play button widget
output_play_button = tkinter.Button(output_action_frame, text="Play", width=0, fg='Green', command=play_button_command)
output_play_button.pack(side=tkinter.LEFT)


def next_step_button():
    """
    Output's next step button click handler

    Goes to next step of the output.
    """
    if OUTPUT_STEP == int(output_to_label['text']):
        return False

    load_output_step(OUTPUT_STEP + 1)
    return True



tkinter.Button(output_action_frame, text=">>", width=0, command=next_step_button).pack(side=tkinter.LEFT)
output_to_label = tkinter.Label(output_action_frame, text="", cursor='fleur')
output_to_label.pack(side=tkinter.LEFT)
output_to_label.bind('<Button-1>', lambda x: output_0_to_label_click(int(output_to_label['text'])))
output_action_frame.grid(row=1, column=0, sticky='WENS')
# Config output frame
config_io_frame_state(output_labelframe, tkinter.DISABLED)
# Input labelframe
input_labelframe = tkinter.LabelFrame(main_window, text="Input")
input_labelframe.grid(row=2, column=1, sticky='WENS', padx=5, pady=5)
input_labelframe.grid_rowconfigure(0, weight=1)
input_labelframe.grid_columnconfigure(0, weight=1)

# Input puzzle frame
input_puzzle_frame = create_puzzle_frame(input_labelframe, ROWS_MATRIX_DEFAULT, COLUMN_MATRIX_DEFAULT)
# Input action frame
input_action_frame = tkinter.Frame(input_labelframe)
input_action_frame.grid(row=1, column=0, sticky='WENS')
input_action_frame.grid_columnconfigure(0, weight=1, uniform=1)
input_action_frame.grid_columnconfigure(1, weight=1, uniform=1)
input_action_frame.grid_columnconfigure(2, weight=1, uniform=1)
input_action_frame.grid_columnconfigure(3, weight=1, uniform=1)

def reset_cell_colors(puzzle_frame):
    for entry_widget in puzzle_frame.winfo_children():
        # Set the background color to the default color
        entry_widget.config(bg="")  # Replace "" with the default color you want

# Example usage:
# Call this function whenever you need to reset the colors of all cells in the puzzle frame.

def random_button_command(puzzle_frame):
    """
    Generates a random solvable puzzle and fills the puzzle_frame with it.

    See https://www.sitepoint.com/randomizing-sliding-puzzle-tiles/ for more information.
    """
    # n = 6
    # lst = [i for i in range(0, n + 1)]
    # random.shuffle(lst)

    # sum_inversions = 0
    # for tile in [x for x in lst if x != 0]:
    #     before_tiles = GOAL_STATE[:GOAL_STATE.index(tile)]
    #     for after_tile in [x for x in lst[lst.index(tile):] if x != 0]:
    #         if before_tiles.count(after_tile):
    #             sum_inversions += 1

    # sqrt_n = math.sqrt(n + 1)

    # def row_number(i):
    #     return math.ceil((i + 1) / sqrt_n)

    # if sqrt_n % 2 == 1:
    #     solvable = sum_inversions % 2 == 0
    # else:
    #     solvable = (sum_inversions + abs(row_number(lst.index(0)) - row_number(GOAL_STATE.index(0)))) % 2 == 0

    # if not solvable:
    #     if lst[0] != 0 and lst[1] != 0:
    #         lst[0], lst[1] = lst[1], lst[0]
    #     else:
    #         lst[len(lst) - 1], lst[len(lst) - 2] = lst[len(lst) - 2], lst[len(lst) - 1]
   

    #test
    # stop_button['state'] = tkinter.NORMAL
    # n_spinbox['state'] = tkinter.DISABLED
    # config_io_frame_state(input_labelframe, tkinter.NORMAL)
    output_to_label['text'] = ''
    output_0_label['text'] = ''
    output_step_text.delete(0, tkinter.END)
    config_io_frame_state(output_labelframe, tkinter.NORMAL)
    # Clear output puzzle
    OUTPUT_EDITABLE = True
    for child in output_puzzle_frame.winfo_children():
        # if child.get().strip() == '':
        #     child['highlightbackground'] = output_step_text['highlightbackground']
        child.config(bg="white")
        child.delete(0, tkinter.END)
    OUTPUT_EDITABLE = False

    new_minesweepergame = MineSweeperGame(ROWS_MATRIX_DEFAULT, ROWS_MATRIX_DEFAULT, NUM_OF_MINES)
    minesweepergame.board = new_minesweepergame.board
    minesweepergame.buttons = new_minesweepergame.buttons
    # reset_cell_colors(puzzle_frame)
    fill_puzzle_frame(puzzle_frame, minesweepergame.board)
    


# Input's random button widget
tkinter.Button(input_action_frame,
               text="Random",
               command=lambda: random_button_command(input_puzzle_frame)).grid(row=0,
                                                                               column=0,
                                                                               sticky='WENS',
                                                                               columnspan=2)


def operator(puzzle):
    """
    Returns all possible puzzle's states that are reachable from current puzzle's state
    """
    states = []

    zero_i = None
    zero_j = None

    for i in range(len(puzzle)):
        for j in range(len(puzzle)):
            if puzzle[i][j] == 0:
                zero_i = i
                zero_j = j
                break

    def add_swap(i, j):
        new_state = deepcopy(puzzle)
        new_state[i][j], new_state[zero_i][zero_j] = new_state[zero_i][zero_j], new_state[i][j]
        states.append(new_state)

    if zero_i != 0:
        add_swap(zero_i - 1, zero_j)

    if zero_j != 0:
        add_swap(zero_i, zero_j - 1)

    if zero_i != len(puzzle) - 1:
        add_swap(zero_i + 1, zero_j)

    if zero_j != len(puzzle) - 1:
        add_swap(zero_i, zero_j + 1)

    return states


def puzzles_equal(first, second):
    for i in range(len(first)):
        for j in range(len(first)):
            if first[i][j] != second[i][j]:
                return False
    return True

# Status bar
status_frame = tkinter.Frame(main_window, bd=1, relief=tkinter.SUNKEN)
status_frame_1 = tkinter.Frame(status_frame, bd=1, relief=tkinter.GROOVE)
tkinter.Label(status_frame_1, text="Execution time(s): ").grid(row=0, column=0, sticky='WENS', padx=2)
tkinter.Label(status_frame_1, textvariable=cpu_var).grid(row=0, column=1, sticky='W')
status_frame_1.grid_columnconfigure(1, weight=1)
status_frame_1.grid(row=0, column=0, sticky='WENS')
status_frame_2 = tkinter.Frame(status_frame, bd=1, relief=tkinter.GROOVE)
tkinter.Label(status_frame_2, text="Max RAM usage(MB): ").grid(row=0, column=0, sticky='WENS', padx=2)
tkinter.Label(status_frame_2, textvariable=max_ram_var).grid(row=0, column=1, sticky='W')
status_frame_2.grid_columnconfigure(1, weight=1)
status_frame_2.grid(row=0, column=1, sticky='WENS')
status_frame_3 = tkinter.Frame(status_frame, bd=1, relief=tkinter.GROOVE)
tkinter.Label(status_frame_3, text="RAM usage(MB): ").grid(row=0, column=0, sticky='WENS', padx=2)
tkinter.Label(status_frame_3, textvariable=ram_var).grid(row=0, column=1, sticky='W')
status_frame_3.grid_columnconfigure(1, weight=1)
status_frame_3.grid(row=0, column=2, sticky='WENS')
status_frame_4 = tkinter.Frame(status_frame, bd=1, relief=tkinter.SUNKEN)
tkinter.Label(status_frame_4, text="Available RAM(MB): ").grid(row=0, column=0, sticky='WENS', padx=2)
tkinter.Label(status_frame_4, textvariable=available_ram_var).grid(row=0, column=1, sticky='W')
status_frame_4.grid_columnconfigure(1, weight=1)
status_frame_4.grid(row=0, column=3, sticky='WENS')
status_frame.grid(row=3, column=0, sticky='WENS', columnspan=2)
status_frame.columnconfigure(0, weight=1, uniform=1)
status_frame.columnconfigure(1, weight=1, uniform=1)
status_frame.columnconfigure(2, weight=1, uniform=1)
status_frame.columnconfigure(3, weight=1, uniform=1)

load_algorithms()
fill_puzzle_frame(input_puzzle_frame, minesweepergame.board)


def available_ram_display():
    """
    A thread target that updates available ram status label every 1 millisecond
    """
    while True:
        available_ram_var.set(round(psutil.virtual_memory().available / (2 ** 20), 3))
        time.sleep(0.001)

if __name__ == '__main__':
    threading.Thread(target=available_ram_display, daemon=True).start()

    # Support windows binary freezing
    multiprocessing.freeze_support()
    # Show the main window
    main_window.mainloop()