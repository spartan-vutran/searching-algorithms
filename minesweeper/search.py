from utils import nullHeuristic
from typing import Optional
from problem import Action, SearchProblem, MineSweeperState
import utils


def testSearch(problem):
  return [Action(1,2), Action(3,1)]

def simpleDepthFirstSearch(problem: Optional[SearchProblem]):
  start_state = problem.getStartState()
  successors = problem.getSuccessors(start_state)
  state, action, cost = successors[0]

  print(f"Is the fisrt state goal state: {problem.isGoalState(state)}")
  problem.getCostOfActions([action])
  return [action]


def printArray(bitArray:MineSweeperState, problem: SearchProblem):
  for i in range(len(bitArray.board)):
    print(f"{bitArray.board[i]}",end=",")
    if (i+1) % problem.cols == 0:
      print("")
  print(bitArray.isLose)


def printArrayInt(list):
  print("[")
  for i in range(len(list)):
    print("\t[", end="")
    for j in range(len(list[i])):
      print(list[i][j], end=",")
    print("],")
  print("]")


def depthFirstSearch(problem: Optional[SearchProblem]):
  fringe = utils.Stack()  # Fringe (Stack) to store the nodes along with their paths
  visited_nodes = set()  # A set to maintain all the visited nodes
  fringe.push((problem.getStartState(), [Action(problem.start_row, problem.start_col)]))  # Pushing (Node, [Path from start-node till 'Node']) to the fringe
  while True:
    popped_element = fringe.pop()
    node = popped_element[0]
    path_till_node = popped_element[1]
    if problem.isGoalState(node):  # Exit on encountering goal node
      break
    else:
      if node not in visited_nodes:   # Skipping already visited nodes
        print("==========Explored node=============")
        printArray(node, problem)
        print("\n")
        printArrayInt(problem.board)
        visited_nodes.add(node)     # Adding newly encountered nodes to the set of visited nodes
        successors = problem.getSuccessors(node)
        for successor in successors:
          child_node = successor[0]
          print("==========Its successor=============")
          printArray(child_node, problem)
          print("\n")
          printArrayInt(problem.board)
          child_path = successor[1]
          full_path = path_till_node + [child_path]  # Computing path of child node from start node
          fringe.push((child_node, full_path)) # Pushing ('Child Node',[Full Path]) to the fringe

  return path_till_node


def aStarSearch(problem, heuristic=nullHeuristic):
  # """Search the node that has the lowest combined cost and heuristic first."""
  fringe = utils.PriorityQueue()    # Fringe (Priority Queue) to store the nodes along with their paths
  visited_nodes = set()    # A set to maintain all the visited nodes
  fringe.push((problem.getStartState(), [Action(problem.start_row, problem.start_col)], 0), heuristic(problem.getStartState(), problem) + 0)    # Pushing (Node, [Path from start-node till 'Node'], Culmulative backward cost till 'Node') to the fringe. In this case, we are using the sum of culmulative backward cost and the heutristic of the node as a factor based on which priority is decided.
  while True:
    popped_element = fringe.pop()
    node = popped_element[0]
    path_till_node = popped_element[1]
    cost_till_node = popped_element[2]
    if problem.isGoalState(node):    # Exit on encountering goal node
      print("==========Goal node=============")
      printArray(node, problem)
      print("\n")
      printArrayInt(problem.board)
      break
    else:
      if node not in visited_nodes:    # Skipping already visited nodes
        visited_nodes.add(node)     # Adding newly encountered nodes to the set of visited nodes
        successors = problem.getSuccessors(node)
        print("==========Exploring in progress node=============")
        printArray(node, problem)
        print("\n")
        printArrayInt(problem.board)
        for successor in successors:
          child_node = successor[0]
          child_path = successor[1]
          child_cost = successor[2]
          full_path = path_till_node + [child_path]    # Computing path of child node from start node
          full_cost = cost_till_node + child_cost    # Computing culmulative backward cost of child node from start node
          heuristic_cost = heuristic(child_node, problem)
          print("==========Its successor=============")
          printArray(child_node, problem)
          print(f"Cost F: {full_cost + heuristic_cost}.  G(s)={full_cost}. H(s)={heuristic_cost} ")
          print("\n")
          printArrayInt(problem.board)
          # TODO: Find a more efficient search, because update function would make the code to be O(n^2)
          fringe.update((child_node, full_path, full_cost), full_cost + heuristic_cost)    # Pushing (Node, [Path], Culmulative backward cost) to the fringe.
      else:
        print("==========Explored node=============")
        printArray(node, problem)
        print("\n")
        printArrayInt(problem.board)
  return path_till_node

dfs = depthFirstSearch
astar = aStarSearch