import tkinter as tk
import random
import utils
from searchAgent import SearchAgent
import copy
import threading
from random import choice, randint
import time
import math



class MineSweeperGame:
  def __init__(self, rows, cols, num_mines, board = None):
    if board == None:
      self.rows = rows
      self.cols = cols
      self.num_mines = num_mines
      self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
      self.initBoard()
    else:
      self.board = board
      self.rows = len(self.board)
      self.cols = len(self.board[0])
      self.num_mines = 0 
      # TODO: Check for valid board
      for i in range(self.rows):
        for j in range(self.cols):
          if self.board[i][j] == -1:
            self.num_mines +=1
      
    self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
    self.leftCount = self.rows*self.cols


  def initBoard(self):
    mines = random.sample(range(self.rows * self.cols), self.num_mines)
    for mine in mines:
        row = mine // self.cols
        col = mine % self.cols
        self.board[row][col] = -1

    # Calculate numbers for adjacent cells
    for row in range(self.rows):
        for col in range(self.cols):
            if self.board[row][col] == -1:
                continue

            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= row + i < self.rows and 0 <= col + j < self.cols and self.board[row + i][col + j] == -1:
                        self.board[row][col] += 1


  def end_game(self):
    for i in range(self.rows):
      for j in range(self.cols):
        if self.board[i][j] == -1:
          self.buttons[i][j].config(text = "*")
        self.buttons[i][j].config(state=tk.DISABLED) #End game
    return
  

  def reveal_cell(self, row, col):
    cell_value = self.board[row][col]

    if cell_value == -1:
      # Game over, show all mines
      self.end_game()
      self.replay_button.config(image=self.crying_icon)
      return

    if cell_value == 0:
        self.buttons[row][col].config(text=' ', state=tk.DISABLED, relief=tk.SUNKEN, bg="red")
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= row + i < self.rows and 0 <= col + j < self.cols and self.buttons[row + i][col + j]['state'] == tk.NORMAL:
                    self.reveal_cell(row + i, col + j)
    else:
        self.buttons[row][col].config(text=str(cell_value), state=tk.DISABLED, relief=tk.SUNKEN, bg="red")
    
    self.leftCount -= 1
    if self.leftCount == self.num_mines: #Check win 
      self.end_game()
      self.replay_button.config(image=self.win_icon)
       

  def replay(self):
    for i in range(self.rows):
      for j in range(self.cols):
          self.board[i][j] = 0
          self.buttons[i][j].config(text='', state=tk.NORMAL, relief=tk.RAISED, bg="#dddddd")
    self.replay_button.config(image=self.playing_icon)
    self.leftCount = self.rows*self.cols
    self.initBoard()


  def run_game(self):
    root = tk.Tk()
    root.title('Minesweeper')

    # Frame
    for i in range(self.rows):
      for j in range(self.cols):
        button = tk.Button(root, width=3, height=1, command=lambda row=i, col=j: self.reveal_cell(row, col), bg="#dddddd")
        button.grid(row=i, column=j)
        self.buttons[i][j] = button

    ## Init icon
    self.playing_icon = utils.resize_icon_image("./assets/playing.png", 35, 35)
    self.crying_icon = utils.resize_icon_image("./assets/crying.png", 35, 35)
    self.win_icon = utils.resize_icon_image("./assets/win.png", 35, 35)

    self.replay_button = tk.Button(root, width=40, height=40, command=self.replay, image=self.playing_icon, borderwidth=0, highlightthickness=0,compound=tk.CENTER) 
    self.find_path_button = tk.Button(root, text="Find", width=5, height=2, command=self.runAgent, compound=tk.CENTER)
    bomb_count_label = tk.Label(root, text="Bombs: {}".format(self.num_mines), compound=tk.CENTER)

    self.replay_button.grid(row=self.rows, column=int(self.cols*0.45), columnspan=1, pady=10)
    self.find_path_button.grid(row=self.rows, column=int(self.cols*0.7), columnspan=2, pady=10)
    bomb_count_label.grid(row=self.rows, column=int(self.cols*0.2), columnspan=2, pady=10)

    # self.runAgent()
    root.mainloop()


  def runAgent(self):
    # agent = SearchAgent("depthFirstSearch", "MineSweeperProblem")
    agent = SearchAgent("aStarSearch", "MineSweeperProblem", "MineSweeperHeuristic")
    agent.registerInitialState(self)

    count = 1
    for action in agent.getAction():
      print(f"Action{count}: {action.x}, {action.y}")
      count +=1
      self.reveal_cell(action.x, action.y)


  def runAgentWihtoutDisplay(self, algorithm):
    # aStarSearch
    agent = SearchAgent("depthFirstSearch", "MineSweeperProblem")
    if algorithm == "A*":
      agent = SearchAgent("aStarSearch", "MineSweeperProblem", "MineSweeperHeuristic")
    elif algorithm == "BrFs":
      #change into Breath First Search when it defined
      agent = SearchAgent("depthFirstSearch", "MineSweeperProblem")
    agent.registerInitialState(self)
    return agent.getAction()

# pathfinding_thread = None
# display_thread = None
    
# def start_pathfinding():
#     global pathfinding_thread
#     # Create and start the pathfinding thread
#     pathfinding_thread = threading.Thread(target=pathfinding_worker)
#     pathfinding_thread.start()

# def start_display():
#   global display_thread
#   # Create and start the display thread
#   display_thread = threading.Thread(target=Game.run_game)
#   display_thread.start()

class Action:
  def __init__(self, row, col, num):
    self.row = row
    self.col = col
    self.num =num

  def __eq__(self, other):
    if isinstance(other, Action):
      return self.row == other.row and self.col == other.col and self.num == other.num
    return False

  # def __hash__(self):
  #   # Ensure that instances of MyClass are hashable based on their value attribute
  #   return hash(self.board.tobytes())


def print_sudoku_grid(grid):
    space_pos = int(math.sqrt(len(grid)))
    print("\n")
    for row_index, row in enumerate(grid):
        if row_index % space_pos == 0 and row_index != 0:
            print("-" * 26)
        for col_index, cell in enumerate(row):
            if col_index % space_pos == 0 and col_index != 0:
                print("|", end="  ")
            if cell == 0:
                print("*", end="  ")
            else:
                print(cell, end="  ")
        print()
    print("\n")

class SudokuGame():
    def __init__(self, window, size, board = None):
        self.window = window
        self.grid_boxes_gui = []
        self.buttons = []
        self.feedback_label = None
        if board == None:
          self.size = size
          self.new_board()
        else:
          self.grid_boxes_values = board
          self.size = len(self.grid_boxes_values)
        self.setup_gui()
        # self.grid_boxes_values = [[1, 0, 0, 0, 7, 0, 3, 0, 0],
        #                           [0, 8, 0, 0, 2, 0, 7, 0, 0],
        #                           [3, 0, 0, 0, 8, 9, 0, 0, 4],
        #                           [8, 4, 0, 0, 0, 1, 9, 0, 3],
        #                           [0, 0, 3, 7, 0, 8, 5, 0, 0],
        #                           [9, 0, 1, 2, 0, 0, 0, 7, 8],
        #                           [7, 0, 0, 3, 5, 0, 0, 0, 9],
        #                           [0, 0, 9, 0,4 ,0 ,0 ,5 ,0],
        #                           [0, 0, 4, 0, 1, 0, 0, 0, 2]]



        
        print_sudoku_grid(self.grid_boxes_values) # in ra man hinh ma tran
        
        self.set_grid_gui_from_values(self.grid_boxes_values)
        self.total_sleep_time = 0

    def setup_gui(self):
        """Creates buttons and labels used in the GUI"""
        self.window.title("Sudoku")
        self.set_dimensions()
        self.create_grid_gui()
        self.create_buttons()
        self.feedback_label = tk.Label(self.window, text="")
        self.feedback_label.grid(column=int(self.size*0.3), row=self.size+3, columnspan=2)

    def set_dimensions(self):
        self.window.geometry('690x550')
        self.window.columnconfigure(0, minsize=20)
        self.window.rowconfigure(0, minsize=20)
        self.window.rowconfigure(self.size+1, minsize=20)

    def create_buttons(self):
        """Creates the reset, new, solve and check buttons and binds their click events to methods"""
        reset_board_button = tk.Button(self.window, text="Reset Board", command=self.set_grid_gui_from_values, font=('Ubuntu', 12))
        new_board_button = tk.Button(self.window, text="New Board", command=self.new_board, font=('Ubuntu', 12))
        # check_solution_button = tk.Button(self.window, text="Check Solution", command=self.check_solution, font=('Ubuntu', 12))
        solve_board_button = tk.Button(self.window, text="Solve Board", command=self.solve_board, font=('Ubuntu', 12))
        new_board_button.grid(column=int(self.size*0.25), row=self.size+2, columnspan=2 if self.size > 4 else 1)
        # check_solution_button.grid(column=3, row=11, columnspan=2)
        reset_board_button.grid(column=int(self.size*0.5), row=self.size+2, columnspan=2 if self.size > 4 else 1)
        solve_board_button.grid(column=int(self.size*0.75), row=self.size+2, columnspan=2 if self.size > 4 else 1)
        # self.buttons = [solve_board_button, check_solution_button, new_board_button, reset_board_button]
        self.buttons = [solve_board_button, new_board_button, reset_board_button]

    def create_grid_gui(self):
        """Creates the GUI squares for the sudoku board"""
        space_pos = int(math.sqrt(self.size))
        for row in range(self.size):
            self.grid_boxes_gui.append([])
            for col in range(self.size):
                input_box = SudokuGridBox(self.window, width=3, font=('Ubuntu', 28), justify='center')
                input_box.configure(highlightbackground="red", highlightcolor="red")
                pady = (10, 0) if row % space_pos == 0 else 0
                padx = (10, 0) if col % space_pos == 0 else 0
                input_box.grid(column=col + 1, row=row + 1, padx=padx, pady=pady)
                self.grid_boxes_gui[row].append(input_box)

    def set_grid_gui_from_values(self, grid=None):
        """Sets the board to display the numbers in a sudoku grid given in nested list format,
        resets the board to what it was previously set as if grid is None"""
        if grid is None:
            grid = self.grid_boxes_values
        for row_index, row in enumerate(self.grid_boxes_gui):
            for column_index, box in enumerate(row):
                value = grid[row_index][column_index]
                if value != 0:
                    box.set(value)
                    box.config(state='readonly')
                else:
                    box.set("")
                    box.config(state="normal")
        self.reset_grid_colour()

    def get_grid_values_from_gui(self):
        """Gets a nested list representation of the current values in each of the boards squares"""
        board = []
        for index, row in enumerate(self.grid_boxes_gui):
            board.append([])
            for col in row:
                value = col.get()
                board[index].append(int(value)) if value != "" else board[index].append(0)
        return board

    # def check_solution(self):
    #     """Checks if the current values in the gui are a valid solution using the rules of sudoku and displays the result
    #     to the user"""
    #     board = self.get_grid_values_from_gui()
    #     if is_solution(board):
    #         self.feedback_label.config(text="Correct solution", fg="Green")
    #     else:
    #         self.feedback_label.config(text="Incorrect solution", fg="Red")

    def solve_board(self):
        """Solves the current board and updates the gui to display the solution"""
        self.toggle_buttons(False)
        self.set_grid_gui_from_values()
        solve_thread = threading.Thread(target=self.runAgent, daemon=True)
        solve_thread.start()


    def generate_new_sudoku_board(self):
      """Randomly generates a seed for a board, then solves the board and randomly removes numbers"""
      new_board = [[0] * self.size for i in range(self.size)]
      possible_numbers = list(range(1, self.size+1))
      row = randint(0,self.size - 1)
      for col in range(self.size):
          value = choice(possible_numbers)
          possible_numbers.remove(value)
          new_board[row][col] = value

      # Fill action
      # TODO: Open this comment and remove the below line if you have implemented SudokuSearch
      agent = SearchAgent("depthFirstSearch", "SudokuProblem", useSmallestBf=True)
      # agent = SearchAgent("aStarSearch", "SudokuProblem", "SudokuHeuristic", useSmallestBf=True)
      self.grid_boxes_values = new_board #First change the board before send into the agent
      agent.registerInitialState(self)
      actions = agent.getAction()
      for action in actions:
         new_board[action.row][action.col] = action.num

      for row in range(self.size):
          num_squares_to_delete = randint(self.size - 2, self.size)
          for _ in range(num_squares_to_delete):
              col = randint(0,self.size - 1)
              new_board[row][col] = 0

      return new_board

    def new_board(self):
        """Generates a new list of values to fill the grid squares and sets the GUI to this new list"""
        self.grid_boxes_values = self.generate_new_sudoku_board()
        
        print_sudoku_grid(self.grid_boxes_values) # in ra man hinh ma tran
        self.set_grid_gui_from_values(self.grid_boxes_values)
        self.reset_grid_colour()


    def update_single_grid_gui_square(self, row, col, colour, value=None):
        """Updates the colour and value of a single square in the grid GUI"""
        self.grid_boxes_gui[row][col].config(fg=colour)
        if value is not None:
            if value == 0:
                value = ""
            self.grid_boxes_gui[row][col].set(value)

    def reset_grid_colour(self):
        """Sets all squares to be coloured black"""
        for row in self.grid_boxes_gui:
            for col in row:
                col.config(fg="black")

    def toggle_buttons(self, clickable):
        """Toggles if the buttons in the UI are clickable or not"""
        for button in self.buttons:
            button.config(state=tk.NORMAL if clickable else tk.DISABLED)


    def runNewAction(self, actions):
      for action in actions:
        self.update_single_grid_gui_square(action.row, action.col, "Green", action.num) 
        time.sleep(0.2)


    def runRemovedAction(self, actions):
      for i in range(len(actions) - 1, -1, -1):
        self.update_single_grid_gui_square(actions[i].row, actions[i].col, "Red")
        time.sleep(0.1)
        self.update_single_grid_gui_square(actions[i].row, actions[i].col, "Red", 0)
        time.sleep(0.1)


    def runAgent(self):
      # First disable button
      # agent = SearchAgent("depthFirstSearch", "SudokuProblem", useSmallestBf=True)
      agent = SearchAgent("aStarSearch", "SudokuProblem", "SudokuHeuristic", useSmallestBf=True)
      agent.registerInitialState(self)
      # TODO: Run your agent here
      explored_paths = agent.getExploredAction()

      old_action = []
      for path in explored_paths:
        if not path:
          continue
        if not old_action:  
          old_action = path
          self.runNewAction(path)
          continue
        
        # Find removed and added actions
        i = 0
        while i< len(old_action) and i < len(path) and old_action[i] == path[i]:
          i +=1
        remove_actions= old_action[i:] if i< len(old_action) else []
        add_actions=path[i:] if i< len(path) else []

        # Display on GUI
        self.runRemovedAction(remove_actions)
        self.runNewAction(add_actions)

        old_action = path

      self.toggle_buttons(True)
            
        # print(f"Action{count}: {action.row}, {action.col}, {action.num}")
        # count +=1
        # self.reveal_cell(action.x, action.y)

class SudokuGridBox(tk.Entry):
    def __init__(self, master=None, **kwargs):
        self.var = tk.StringVar()
        tk.Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = ''
        self.var.trace('w', self.validate_input)
        self.get, self.set = self.var.get, self.var.set

    def validate_input(self, *args):
        """Ensures input to a grid box is a number from 1-9"""
        value = self.get()
        if not value:
            self.set("")
        elif value.isdigit() and len(value) < 2 and value != "0":
            # the current value is only digits; allow this
            self.old_value = self.get()
        else:
            self.set(self.old_value)



if __name__ == '__main__':
  ################## MINESWEEPER #############################
  # rows = 10
  # cols = 10
  # num_mines = 12
  # ## Init with board
  # board = [
  #       [0,0,0,0,0,1,1,1,0,0,],
  #       [0,0,0,0,0,1,-1,1,0,0,],
  #       [0,0,1,2,2,2,1,1,0,0,],
  #       [0,1,2,-1,-1,1,0,0,0,0,],
  #       [0,1,-1,4,3,2,0,0,1,1,],
  #       [1,2,2,2,-1,1,0,0,1,-1,],
  #       [1,-1,1,2,2,2,0,0,1,1,],
  #       [1,1,2,2,-1,1,1,1,1,0,],
  #       [1,1,1,-1,2,1,2,-1,2,0,],
  #       [-1,1,1,1,1,0,2,-1,2,0,],
  # ]
  # game = MineSweeperGame(rows, cols, num_mines, board)
  # game.run_game()

  # Init with random board
  # game = MineSweeperGame(rows, cols, num_mines)

  ################## SUDOKU #############################
  ## Init with board
  board = [[9, 8, 0, 0, 0, 0, 0, 2, 0], [0, 2, 0, 0, 0, 0, 3, 9, 7], [0, 3, 1, 0, 0, 9, 5, 0, 8], [0, 0, 0, 4, 7, 5, 0, 1, 0], [0, 0, 0, 0, 1, 2, 0, 8, 0], [4, 1, 0, 0, 3, 0, 0, 5, 0], [3, 7, 0, 1, 0, 0, 0, 0, 2], [0, 0, 0, 0, 8, 0, 1, 7, 0], [0, 6, 8, 0, 5, 0, 0, 0, 0]]
  window = tk.Tk()
  SudokuGame(window, 9, board)
  window.mainloop()

  # Init with random board
  # window = tk.Tk()
  # SudokuGame(window, 9)
  # window.mainloop()