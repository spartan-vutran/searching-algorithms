import search
import problem
import time
import utils

class Agent:
    """
    An agent must define a getAction method, but may also define the
    following methods which will be called if they exist:

    def registerInitialState(self, state): # inspects the starting state
    """
    def __init__(self, index=0):
        self.index = index

    def getAction(self, state):
        """
        The Agent will receive a GameState (from either {pacman, capture, sonar}.py) and
        must return an action from Directions.{North, South, East, West, Stop}
        """
        pass


class SearchAgent(Agent):
  """
    This very general search agent finds a path using a supplied search
    algorithm for a supplied search problem, then returns actions to follow that
    path.

    As a default, this agent runs DFS on a PositionSearchProblem to find
    location (1,1)

    Options for fn include:
      depthFirstSearch or dfs
      breadthFirstSearch or bfs
  """

  def __init__(self, fn='depthFirstSearch', prob='SimpleProblem', heuristic='nullHeuristic', useSmallestBf = False):
    self.useSmallestBf=useSmallestBf
    if fn not in dir(search):
      raise (AttributeError, fn + ' is not a search function in search.py.')
    func = getattr(search, fn)
    if 'heuristic' not in func.__code__.co_varnames:
      print('[SearchAgent] using function '+fn)
      self.searchFunction = func
    else:
      heur = None
      for mod in [utils, problem]:
        if heuristic in dir(mod):
          heur = getattr(mod, heuristic)
          break
      if heur == None:
        raise (AttributeError, heuristic + ' is not a function in searchAgents.py or search.py.')
      print('[SearchAgent] using function %s and heuristic %s' % (fn, heuristic))
      # Note: this bit of Python trickery combines the search algorithm and the heuristic
      self.searchFunction = lambda x: func(x, heuristic=heur)
      
    if prob not in dir(problem) or not prob.endswith('Problem'):
      raise(AttributeError, prob + ' is not a search problem type in SearchAgents.py.')
    self.searchType = getattr(problem, prob)
    print('[SearchAgent] using problem type ' + prob)
  
  def registerInitialState(self, state):
    """
      This is the first time that the agent sees the layout of the game
      board. Here, we choose a path to the goal. In this phase, the agent
      should compute the path to the goal and store it in a local variable.
      All of the work is done in this method!

      state: a GameState object (pacman.py)
    """
    if self.searchFunction == None:
      raise (Exception, "No search function provided for SearchAgent")
    starttime = time.time()
    problem = self.searchType(state, self.useSmallestBf) # Makes a new search problem, make sure state is your specific game state (Minesweeper or Sudoku)
    self.searchResult = self.searchFunction(problem) #Find a path
    totalCost = problem.getCostOfActions(self.searchResult.actions)
    print('Path found with total cost of %d in %.1f seconds' % (totalCost, time.time() - starttime))
    print(f"Explored action cost: {len(self.searchResult.explored_actions)}")
    # if '_expanded' in dir(problem): print('Search nodes expanded: %d' % problem._expanded)

  def getAction(self):
    """
    Returns the next action in the path chosen earlier (in
    registerInitialState). 

    state: a GameState object (minesweeper.py)
    """
    # TODO: We have to define action first
    return self.searchResult.actions
    # if 'actionIndex' not in dir(self): self.actionIndex = 0
    # i = self.actionIndex
    # self.actionIndex += 1
    # if i < len(self.actions):
    #     yield self.actions[i]
    # else:
    #     return Directions.STOP

  def getExploredAction(self):
    return self.searchResult.explored_actions