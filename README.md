# Searching algorithms
The repo is an assignment as part of Introduction to AI course in my school

## 1. How to run
First cd to game folder 
```bash
cd game
```
In game file you do
### 1.1 Minesweeper game 
+ To play with a custom board, first you change the board matrix at the end of game.py file, in main() function, in the minesweeper code section. (Will change place to put matrix if I have free time). And then execute:

```bash
python game.py --game minesweeper --mode default
```

+ To view the result step by step. Let's run:
```bash
python minesweeperUI.py
```

+ To play with random board in a specific row, column size and number of mines. Execute:

```bash
python game.py --game minesweeper -r {number of row} -c {number of cols} -m {number of mines}
python game.py --game minesweeper -r 7 -c 7 -m 20
```

+ To export the minesweeper measures which includes: 
  + Number of explored nodes.
  + Execution time

Notice that we try many different random boards (30 by default) in different board size (from 4x4 -> 9x9) to get the measures, export process may thus take long time to finish.
```bash
python game.py --game minesweeper --export --sameple-size {number of different random boards} --timeout {timeout in second algorithm will execute on a board}
python game.py --game minesweeper --export --sameple-size 20  --timeout 30
```
You can also add -r, -c, -m parameter to the above command  to custom number of rows, cols, and mines.
### 1.2 Sudoku game 
+ To play with a custom board, first you change the board matrix at the end of game.py file, in main() function, in sudoku code section (Will change place to put matrix if I have free time). And then execute:

```bash
python game.py --game sudoku --mode default
```

+ To play with random board in a specific row, column size and number of mine.

```bash
python game.py --game sudoku --size {size in perfect square number}
python game.py --game sudoku --size 9
```

+ To export the sudoku measures which includes: 
  + Number of explored nodes.
  + Execution time

Notice that we try many different random boards (30 by default) in different board size (from 4x4 -> 9x9) to get the measures, export process may thus take long time to finish.
```bash
python game.py --game sudoku --export --sameple-size {number of different random boards} --timeout {timeout in second algorithm will execute on a board}
python game.py --game sudoku --export --sameple-size 20  --timeout 30
```
You can also add -s parameter to the above command  to custom number of rows, cols, and mines.


## 2. Export
Export files after running should be created in the export folder.

