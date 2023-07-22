from heuristic import nullHeuristic

class Action:
  def __init__(self, x,y):
    self.x = x
    self.y = y

def testSearch(problem):
  return [Action(1,2), Action(3,1)]

def depthFirstSearch(problem):
  pass


def aStarSearch(problem, heuristic=nullHeuristic):
  pass

dfs = depthFirstSearch
astar = aStarSearch