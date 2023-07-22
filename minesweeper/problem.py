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

class SimpleProblem(SearchProblem):
    """
    A search problem defines the state space, start state, goal test, successor function and cost function. 

    The state space consists of (x,y) positions in a pacman game.

    Note: this search problem is fully specified; you should NOT change it.
    """
    def __init__(self, gameState, goal= 1, costFn = lambda x: 1, start = None, warn=True, visualize=True):
      """
      Stores the start and goal. 
      gameState: A GameState object (minesweeper.py)
      costFn: A function from a search state (tuple) to a non-negative number
      goal: A position in the gameState
      """
      # self.walls =gameState.
      return None

    def getCostOfActions(self, actions):
      """
        actions: A list of actions to take

      This method returns the total cost of a particular sequence of actions.
      The sequence must be composed of legal moves.
      """
      return 1