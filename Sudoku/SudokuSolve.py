from random import choice, randint
import time
import psutil
import threading

total_sleep_time = 0
DFS_time_solve = 0
memory_used = 0

# def solve(board, gui=None):
#     """Solves the board and displays board to GUI/renables buttons if gui is not none.
#     Returns solved board as nested list """
    
#     # tính toán thời gian chạy DFS
    
#     global total_sleep_time
#     start_time = time.time()
    
#     solved_board = dfs_solve(board, gui)
    
#     end_time = time.time()
#     DFS_time_solve = end_time - start_time - total_sleep_time
#     if gui!=None:
#         print(f"The time to solve the sudoku matrix with DFS is: {DFS_time_solve:.6f} seconds")
#     total_sleep_time = 0
    
    
#     if gui:
#         gui.toggle_buttons(True)
#     return solved_board


def solve_async(board, gui=None, callback=None):
    # Create a thread and start the solving process
    solve_thread = threading.Thread(target=solveProblem, args=(board, gui, callback, "DFS"))
    solve_thread.start()

    # Return the thread, so the caller can choose to join or continue without blocking
    return solve_thread

def solveProblem(board, gui=None, callback=None, algorithm = "DFS"):
    """Solves the board and displays board to GUI/renables buttons if gui is not none.
    Returns solved board as nested list """
    
    # tính toán thời gian chạy DFS
    
    global total_sleep_time, memory_used, DFS_time_solve
    start_time = time.time()
    start_memory_usage = psutil.Process().memory_info().rss / 1024.0 / 1024.0
    
    solved_board = dfs_solve(board, gui)
    
    end_time = time.time()
    end_memory_usage = psutil.Process().memory_info().rss / 1024.0 / 1024.0

    DFS_time_solve = end_time - start_time - total_sleep_time
    memory_used = end_memory_usage - start_memory_usage;
    if gui!=None:
        print(f"The time to solve the sudoku matrix with DFS is: {DFS_time_solve:.6f} seconds")
        print(f"The time to sleep the sudoku matrix with DFS is: {total_sleep_time:.6f} seconds")
        print(f"The memory used to solve the sudoku matrix with DFS is: {memory_used:.2f} megabytes")
    # total_sleep_time = 0
    
    
    if gui:
        gui.toggle_buttons(True)
    if callback is not None:
        callback(DFS_time_solve, memory_used)


def solve(board, gui=None):
    """Solves the board and displays board to GUI/renables buttons if gui is not none.
    Returns solved board as nested list """
    
    # tính toán thời gian chạy DFS
    
    global total_sleep_time, memory_used, DFS_time_solve
    start_time = time.time()
    start_memory_usage = psutil.Process().memory_info().rss / 1024.0 / 1024.0
    
    solved_board = dfs_solve(board, gui)
    
    end_time = time.time()
    end_memory_usage = psutil.Process().memory_info().rss / 1024.0 / 1024.0

    DFS_time_solve = end_time - start_time - total_sleep_time
    memory_used = end_memory_usage - start_memory_usage;
    if gui!=None:
        print(f"The time to solve the sudoku matrix with DFS is: {DFS_time_solve:.6f} seconds")
        print(f"The time to sleep the sudoku matrix with DFS is: {total_sleep_time:.6f} seconds")
        print(f"The memory used to solve the sudoku matrix with DFS is: {memory_used:.2f} megabytes")
    # total_sleep_time = 0
    
    
    if gui:
        gui.toggle_buttons(True)
    return solved_board




def dfs_solve(board, gui):
    """Solves the sudoku board represented as a nested list using DFS backtracking.
    If a GUI reference is passed in, the solving process is displayed to the user"""
    
    
    global total_sleep_time
    
    
    if is_solution(board):   
        return board
    row, col = get_first_unfilled_square(board)
    possible_solutions = get_valid_numbers(board, row, col)   
    if possible_solutions:     # Nếu trống => False
        for number in possible_solutions:
            if gui:
                gui.update_single_grid_gui_square(row, col, "Green", number)
                time.sleep(0.2)
                total_sleep_time+=0.2
            board[row][col] = number
            solved = dfs_solve(board, gui)
            if is_solution(solved):
                return solved

    board[row][col] = 0
    if gui:
        gui.update_single_grid_gui_square(row, col, "Red")
        time.sleep(0.1)
        gui.update_single_grid_gui_square(row, col, "Red", 0)
        time.sleep(0.1)
        total_sleep_time+=0.2
    return board

def get_valid_numbers(board, row, col):
    """Returns a set of possible numbers that could be inserted in a grid cell"""
    return get_valid_numbers_in_row(board, row, col) & get_valid_in_column(board, row, col) & get_valid_in_square(board, row, col)


def get_valid_numbers_in_row(board, row, col):
    """Returns a set of numbers valid in box given the sudoku row constraints"""
    valid_numbers = {1,2,3,4,5,6,7,8,9}
    for index, item in enumerate(board[row]):
        if index == col:
            continue
        elif item in valid_numbers:
            valid_numbers.remove(item)
    return valid_numbers


def get_valid_in_column(board, row, col):
    """Returns a set of numbers valid in the column given sudoku constraints"""
    valid_numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    for row_index in range(9):
        if row_index == row:
            continue
        square = board[row_index][col]
        if square in valid_numbers:
            valid_numbers.remove(square)
    return valid_numbers


def get_valid_in_square(board, row, col):
    """Returns a set of numbers valid in the square given sudoku constraints"""
    valid_numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    start_x = (col // 3) * 3
    start_y = (row // 3) * 3
    for y in range(start_y, start_y + 3):
        for x in range(start_x, start_x + 3):
            square_value = board[y][x]
            if y == row and x == col:
                continue
            elif square_value in valid_numbers:
                valid_numbers.remove(square_value)
    return valid_numbers


def is_solution(board):
    """Checks if the board is completely filled with non zero numbers"""
    for row in range(9):
        for col in range(9):
            if board[row][col] not in get_valid_numbers(board, row, col):
                return False
    return True


def get_first_unfilled_square(board):
    """Gets the first square in the board that has a value of zero"""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return row, col


def generate_new_board():
    """Randomly generates a seed for a board, then solves the board and randomly removes numbers"""
    new_board = [[0] * 9 for i in range(9)]
    possible_numbers = [1,2,3,4,5,6,7,8,9]
    row = randint(0,8)
    for col in range(9):
        value = choice(possible_numbers)
        possible_numbers.remove(value)
        new_board[row][col] = value

    new_board = solve(new_board, None)

    for row in range(9):
        num_squares_to_delete = randint(7,9)
        for _ in range(num_squares_to_delete):
            col = randint(0,8)
            new_board[row][col] = 0

    return new_board




