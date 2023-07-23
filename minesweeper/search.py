from heuristic import nullHeuristic
from typing import Optional
from problem import Action, SearchProblem



def testSearch(problem):
  return [Action(1,2), Action(3,1)]

def simpleDepthFirstSearch(problem: Optional[SearchProblem]):
  start_state = problem.getStartState()
  successors = problem.getSuccessors(start_state)
  state, action, cost = successors[0]

  print(f"Is the fisrt state goal state: {problem.isGoalState(state)}")
  problem.getCostOfActions([action])
  return [action]

def depthFirstSearch(problem):
  pass

def aStarSearch(problem, heuristic=nullHeuristic):
  pass

dfs = depthFirstSearch
astar = aStarSearch