import openpyxl
from game import MineSweeperGame
from game import SudokuGame
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
testcases = [
    [8,8,10],
    [9,9,11],
    [10,10,13],
    [11,11,15],
    [12,12,18],
    [13,13,19],
    [14,14,20]
    # [15,15,25],
    # [16,16,30],
]
testcasesSodoku = [
    [9,9,11]
]
game = None
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.append(["Size board", "Num of mine", "Algorithm", "Time used", "Memory used, Explored action"])
# sheet.append(["Size board", "Algorithm", "Time used", "Memory used"])

for algorithm in ["A*", "DFS"]:
    for testcase in testcasesSodoku:
        row, col, num_mines = testcase[0],testcase[1],testcase[2]
        window = tk.Tk()
        game =  SudokuGame(window, row)
        game.runAgentForStatistic(algorithm)
        sheet.append([f"{row}x{col}", algorithm, game.time_used.get(), game.memory_used.get(), game.exploredAction])

# for testcase in testcases:
#     row, col, num_mines = int(testcase[0]),int(testcase[1]),int(testcase[2])
#     game = MineSweeperGame(row, col, num_mines)
#     game.runAgentForStatistic("A*")
#     sheet.append([f"{row}x{col}", "A*", game.time_used.get(), game.memory_used.get(), game.exploredAction])
#     game.clear()
#     game.runAgentForStatistic("DFS")
#     sheet.append([f"{row}x{col}", "DFS", game.time_used.get(), game.memory_used.get(), game.exploredAction])
#     game.clear()

root.mainloop()

workbook.save('output_file.xlsx')
workbook.close()
