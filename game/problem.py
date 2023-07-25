import copy
from bitarray import bitarray
from typing import Tuple
import math
class Action:
  def __init__(self, x,y):
    pass


class MineAction(Action):
  def __init__(self, x,y):
    self.x = x
    self.y = y
  def getX(self):
     return self.x
  def getY(self):
     return self.y
  

class SudokuAction(Action):
  def __init__(self, row, col, num):
    self.row = row
    self.col = col
    self.num =num

  def __eq__(self, other):
    if isinstance(other, SudokuAction):
      return self.row == other.row and self.col == other.col and self.num == other.num
    return False

  # def __hash__(self):
  #   # Ensure that instances of MyClass are hashable based on their value attribute
  #   return hash(self.board.tobytes())


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        pass
        # util.raiseNotDefined()
    

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        pass
        # util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        pass
        # util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        return 1
        # util.raiseNotDefined()



class SudokuProblem(SearchProblem):
  """
  This class outlines the structure of a search problem, but doesn't implement
  any of the methods (in object-oriented terminology: an abstract class).

  You do not need to change anything in this class, ever.
  """
  def __init__(self, gameState, useSmallestBf = False):
    # We create the 2D array tuple as we need it to be hastable to store in visited_set
    self.start_state = tuple(tuple(row) for row in gameState.grid_boxes_values)
    self.size = gameState.size
    self.useSmallestBf = useSmallestBf


  def get_valid_numbers(self, board, row, col):
    """Returns a set of possible numbers that could be inserted in a grid cell"""
    return self.get_valid_numbers_in_row(board, row, col) & self.get_valid_in_column(board, row, col) & self.get_valid_in_square(board, row, col)


  def get_valid_numbers_in_row(self, board, row, col):
      """Returns a set of numbers valid in box given the sudoku row constraints"""
      valid_numbers = set(range(1, self.size+1))
      for index, item in enumerate(board[row]):
          if index == col:
            continue
          elif item in valid_numbers:
            valid_numbers.remove(item)
      return valid_numbers


  def get_valid_in_column(self, board, row, col):
      """Returns a set of numbers valid in the column given sudoku constraints"""
      valid_numbers = set(range(1, self.size+1))
      for row_index in range(self.size):
          if row_index == row:
              continue
          square = board[row_index][col]
          if square in valid_numbers:
              valid_numbers.remove(square)
      return valid_numbers


  def get_valid_in_square(self, board, row, col):
      """Returns a set of numbers valid in the square given sudoku constraints"""
      valid_numbers = set(range(1, self.size+1))
      space_pos = int(math.sqrt(self.size))
      start_x = (col // space_pos) * space_pos
      start_y = (row // space_pos) * space_pos
      for y in range(start_y, start_y + space_pos):
          for x in range(start_x, start_x + space_pos):
              square_value = board[y][x]
              if y == row and x == col:
                  continue
              elif square_value in valid_numbers:
                  valid_numbers.remove(square_value)
      return valid_numbers


  def getStartState(self):
      """
      Returns the start state for the search problem.
      """
      return [self.start_state, []]


  def isGoalState(self, state: Tuple[Tuple[int]]):
    """
      state: Search state
    [
        [6,8,7,5,2,3,4,0,0,],
        [0,0,5,7,0,1,3,9,0,],
        [0,0,1,0,0,8,0,0,0,],
        [0,0,0,0,7,0,0,1,3,],
        [0,0,3,0,1,0,0,4,9,],
        [5,0,0,0,4,0,8,7,0,],
        [0,5,0,0,0,0,9,8,0,],
        [4,0,8,0,6,0,0,0,2,],
        [0,3,0,2,8,0,0,0,4,],
    ]
    Returns True if and only if the state is a valid goal state.
    """
    for row in range(self.size):
        for col in range(self.size):
            if state[row][col] not in self.get_valid_numbers(state, row, col):
                return False
    return True

  def copyStateWithNewNumber(self, state: Tuple[Tuple[int]], row:int, col:int, num:int) -> Tuple[Tuple[int]]:
    temp_array = list(state[row]) #Copy the row where we need change and turn it to list
    temp_array[col] = num
    new_state = ()
    for i in range(len(state)):
      if i == row:
        new_state += (tuple(temp_array),)
      else:
         new_state +=(state[i], )
    return new_state


  def getSuccessors(self, state: Tuple[Tuple[int]]):
      """
        state: Search state

      For a given state, this should return a list of triples, (successor,
      action, stepCost), where 'successor' is a successor to the current
      state, 'action' is the action required to get there, and 'stepCost' is
      the incremental cost of expanding to that successor.
      """
      # We have 2 ways to generate successor:
        # 1.  Choose first unfilled cell and then fill in the valid number
        # 2.  Generate all successors from all cells which may have a set of valid number => This results in greater BFS

      tripples = []
      for i in range(len(state)):
        for j in range(len(state[0])):
            if state[i][j] == 0:
              valid_numbers = self.get_valid_numbers(state, i, j)
              if not valid_numbers:
                return []
              for num in valid_numbers:
                successor = self.copyStateWithNewNumber(state, i, j, num)
                tripples.append((successor, SudokuAction(i, j, num), 1))
              if self.useSmallestBf:
                return tripples
      return tripples
                

  def getCostOfActions(self, actions):
    """
      actions: A list of actions to take

    This method returns the total cost of a particular sequence of actions.
    The sequence must be composed of legal moves.
    """
    return len(actions)
      


class MineSweeperState():
  def __init__(self, gameState, isLose=False, useSmallestBf = False):
    # Touched tracking board
    self.cols = gameState.cols
    self.rows = gameState.rows
    self.board = bitarray(gameState.cols*gameState.rows)
    self.board.setall(0)
    self.isLose = isLose
  
  def __getitem__(self, index):
    if isinstance(index, tuple) and len(index) == 2:
        row, col = index
        if 0 <= row < self.rows and 0 <= col < self.cols:
          pos = row*self.cols + col
          return self.board[pos]
        else:
            raise IndexError("Index out of range")
    else:
        raise TypeError("Invalid index format. Use (row, col)")

  def __setitem__(self, index, value):
    if isinstance(index, tuple) and len(index) == 2:
      row, col = index
      if 0 <= row < self.rows and 0 <= col < self.cols:
          pos = row*self.cols + col
          self.board[pos] = value
      else:
          raise IndexError("Index out of range")
    else:
        raise TypeError("Invalid index format. Use (row, col)")

  def __eq__(self, other):
    if isinstance(other, MineSweeperState):
      return self.board == other.board
    return False

  def __hash__(self):
    # Ensure that instances of MyClass are hashable based on their value attribute
    return hash(self.board.tobytes())


class MineSweeperProblem(SearchProblem):
    """
    A search problem defines the state space, start state, goal test, successor function and cost function. 

    The state space consists of (x,y) positions in a pacman game.

    Note: this search problem is fully specified; you should NOT change it.
    """
    def __init__(self, gameState, useSmallestBf=False):
      """
      Stores the start and goal. 
      gameState: A MineSweeperGame object (minesweeper.py)
      costFn: A function from a search state (tuple) to a non-negative number
      goal: A position in the gameState
      """
      # Check class name for the state
      if not gameState.__class__.__name__.startswith("MineSweeper"):
        raise TypeError("gameState does not belong to the MineSweeperGame class.")

      self.board = copy.deepcopy(gameState.board)
      self.cols = gameState.cols
      self.rows = gameState.rows
      # Init start state
      start_pos = 0
      start_row = 0
      start_col = 0
      while(self.board[start_row][start_col]==-1):
        start_pos +=1
        start_row = start_pos//self.cols 
        start_col = start_pos%self.cols 

      # Create start_state
      self.start_state = MineSweeperState(gameState)
      if self.board[start_row][start_col] == 0:
        self.expand(self.start_state, start_row, start_col)
      self.start_state[start_row, start_col] = 1
      self.firstAction = MineAction(start_row, start_col)

      # Create goal state
      self.goal_state = MineSweeperState(gameState)
      for i in range(self.rows):
         for j in range(self.cols):
            self.goal_state[i,j] = 0 if self.board[i][j] == -1 else 1
      
      return None

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        return [self.start_state, [self.firstAction]]
        # util.raiseNotDefined()

    def isGoalState(self, state: MineSweeperState):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        return state == self.goal_state
        # util.raiseNotDefined()
    

    def expand(self, state:MineSweeperState, row, col):
      # This function is called only when the touched cell is zero to expand and generate skipped state
      if self.board[row][col] != 0:
        return

      state[row,col] = 1 
      for i in [row-1, row, row+1]:
        if (i<0 or i>= self.rows):
          continue
        for j in [col-1, col, col+1]:
          if (j<0 or j>=self.cols) or (state[i,j] == 1):
            continue
          if self.board[i][j] == 0:
            self.expand(state, i, j)
          else:
            state[i, j] = 1

      
    def getSuccessors(self, state: MineSweeperState):
      """
      state: Search state

      For a given state, this should return a list of triples, (successor,
      action, stepCost), where 'successor' is a successor to the current
      state, 'action' is the action required to get there, and 'stepCost' is
      the incremental cost of expanding to that successor.
      """
      if state.isLose == True:
        return []
      
      successors = []
      # TODO: Apply more efficient search here
      for i in range(state.rows):
        for j in range(state.cols):
           if state[i, j] == 0:
              successor = copy.deepcopy(state)
              if self.board[i][j] == -1: #If the successor press a mine
                successor.isLose = True
              elif self.board[i][j] == 0:
                self.expand(successor, i, j)
              successor[i, j] = 1
              successors.append((successor, MineAction(i,j), 1))
      return successors

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        return len(actions)


def SudokuHeuristic(state, problem: SudokuProblem):
  left_cell= 0
  invalid_point = 0
  total_cell = problem.size**2
  for i in range(problem.size):
     for j in range(problem.size):
        if state[i][j] == 0:
          valid_fill_nums = problem.get_valid_numbers(state, i, j)
          if not valid_fill_nums:
            invalid_point +=2 #This is because we lost at least 2 steps to fix the wrong action
          else:
            left_cell +=1

  return left_cell + invalid_point - ((total_cell - left_cell)/total_cell if left_cell != 0 else 0)


# Calculate the number of cells aside bomb cells
def MineSweeperHeuristic(state: MineSweeperState, problem: MineSweeperProblem):
  cell_aside_bomb_count = set()
  # TODO: This algo is O(n^2), fix it if you have time
  
  for i in range(problem.rows):
    for j in range(problem.cols):
      if problem.board[i][j] == -1:
        for m in [i-1, i, i+1]:
          if m<0 or m >= problem.rows:
            continue
          for k in [j-1, j, j+1]:
            if (k<0 or k >= problem.cols) or (i==m and k==j):
              continue
            if state[m, k] == 0 and problem.board[m][k] != -1: 
              cell_aside_bomb_count.add((m,k))

  x = problem.goal_state.board.count(False)
  y = state.board.count(False)
  return len(cell_aside_bomb_count) - (x/y if x<y else 0)
     