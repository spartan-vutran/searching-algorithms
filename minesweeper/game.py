import tkinter as tk
import random
import utils
from searchAgent import SearchAgent


class MineSweeperGame:
  def __init__(self, rows, cols, num_mines):
    self.rows = rows
    self.cols = cols
    self.num_mines = num_mines
    self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
    self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
    self.initBoard()
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
        self.buttons[row][col].config(text=' ', state=tk.DISABLED, relief=tk.SUNKEN)
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= row + i < rows and 0 <= col + j < cols and self.buttons[row + i][col + j]['state'] == tk.NORMAL:
                    self.reveal_cell(row + i, col + j)
    else:
        self.buttons[row][col].config(text=str(cell_value), state=tk.DISABLED, relief=tk.SUNKEN)
    
    self.leftCount -= 1
    if self.leftCount == self.num_mines: #Check win 
      self.end_game()
      self.replay_button.config(image=self.win_icon)
       

  def replay(self):
    for i in range(rows):
      for j in range(cols):
          self.board[i][j] = 0
          self.buttons[i][j].config(text='', state=tk.NORMAL, relief=tk.RAISED)
    self.replay_button.config(image=self.playing_icon)
    self.leftCount = self.rows*self.cols
    self.initBoard()


  def run_game(self):
    root = tk.Tk()
    root.title('Minesweeper')

    # Frame
    for i in range(rows):
      for j in range(cols):
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
    agent = SearchAgent("simpleDepthFirstSearch", "MineSweeperProblem")
    agent.registerInitialState(self)

    for action in agent.getAction(1):
      self.reveal_cell(action.x, action.y)

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

if __name__ == '__main__':
  rows = 8
  cols = 8
  num_mines = 2

  game = MineSweeperGame(rows, cols, num_mines)
  game.run_game()