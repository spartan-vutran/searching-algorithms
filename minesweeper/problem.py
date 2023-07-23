import copy
from bitarray import bitarray

class Action:
  def __init__(self, x,y):
    self.x = x
    self.y = y


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

class MineSweeperState():
  def __init__(self, gameState, isLose=False):
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
    def __init__(self, gameState):
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
      self.start_row = 0
      self.start_col =0
      while(self.board[self.start_row][self.start_col]==-1):
        start_pos +=1
        self.start_row = start_pos//self.cols 
        self.start_col = start_pos%self.cols 

      # Create start_state
      self.start_state = MineSweeperState(gameState)
      if self.board[self.start_row][self.start_col] == 0:
        self.expand(self.start_state, self.start_row, self.start_col)
      self.start_state[self.start_row, self.start_col] = 1

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
        return self.start_state
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
              successors.append((successor, Action(i,j), 1))
      return successors

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        return len(actions)
    

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
  
  return len(cell_aside_bomb_count)
     